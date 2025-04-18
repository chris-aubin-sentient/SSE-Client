import httpx
import json
from contextlib import asynccontextmanager, contextmanager
from typing import (
    Any,
    AsyncIterator,
    Iterator,
    List,
    Optional,
)


class ServerSentEvent:
    def __init__(
        self,
        event: Optional[str] = None,
        data: Optional[str] = None,
        id: Optional[str] = None,
        retry: Optional[int] = None,
    ) -> None:
        if not event:
            event = "message"
        if data is None:
            data = ""
        if id is None:
            id = ""

        self._event = event
        self._data = data
        self._id = id
        self._retry = retry

    @property
    def event(self) -> str:
        return self._event

    @property
    def data(self) -> str:
        return self._data

    @property
    def id(self) -> str:
        return self._id

    @property
    def retry(self) -> Optional[int]:
        return self._retry

    def json(self) -> Any:
        return json.loads(self.data)
    
    def __repr__(self) -> str:
        return f"ServerSentEvent(event={self.event}, data={self.data}, id={self.id}, retry={self.retry})"


class SSEDecoder:
    """
    Given an SSE event, this class decodes it into a ServerSentEvent object.
    """
    
    def __init__(self) -> None:
        self._event = ""
        self._data: List[str] = []
        self._last_event_id = ""
        self._retry: Optional[int] = None

    def decode(self, line: str) -> Optional[ServerSentEvent]:
        if not line:
            if (
                not self._event
                and not self._data
                and not self._last_event_id
                and self._retry is None
            ):
                return None

            sse = ServerSentEvent(
                event=self._event,
                data="\n".join(self._data),
                id=self._last_event_id,
                retry=self._retry,
            )

            self._event = ""
            self._data = []
            self._retry = None

            return sse

        if line.startswith(":"):
            return None

        fieldname, _, value = line.partition(":")

        if value.startswith(" "):
            value = value[1:]

        if fieldname == "event":
            self._event = value
        elif fieldname == "data":
            self._data.append(value)
        elif fieldname == "id":
            if "\0" in value:
                pass
            else:
                self._last_event_id = value
        elif fieldname == "retry":
            try:
                self._retry = int(value)
            except (TypeError, ValueError):
                pass
        else:
            pass

        return None
    

class EventSource:
    """
    Given a httpx response to an SSE endpoint, this class casts the server sent
    events to ServerSentEvent objects and provides sync and async iterators
    over those objects.
    """

    def __init__(self, response: httpx.Response) -> None:
        self._response = response
        self._decoder = SSEDecoder()

    def _check_content_type(self) -> None:
        content_type = self._response.headers.get("content-type", "").partition(";")[0]
        if "text/event-stream" not in content_type:
            raise Exception(
                "Expected response header Content-Type to contain 'text/event-stream', "
                f"got {content_type!r}"
            )

    def iter_sse(self) -> Iterator[ServerSentEvent]:
        self._check_content_type()
        for line in self._response.iter_lines():
            line = line.rstrip("\n")
            sse = self._decoder.decode(line)
            if sse is not None:
                yield sse

    async def aiter_sse(self) -> AsyncIterator[ServerSentEvent]:
        self._check_content_type()
        async for line in self._response.aiter_lines():
            line = line.rstrip("\n")
            sse = self._decoder.decode(line)
            if sse is not None:
                yield sse


def stream(
    url: str,
    method: str = "GET",
    **kwargs: Any
) -> Iterator[ServerSentEvent]:
    client = httpx.Client()
    headers = kwargs.pop("headers", {})
    headers["Accept"] = "text/event-stream"
    headers["Cache-Control"] = "no-store"

    with client.stream(method, url, headers=headers, **kwargs) as response:
        yield from EventSource(response).iter_sse()


async def async_stream(
    url: str,
    method: str = "GET",
    **kwargs: Any
) -> AsyncIterator[ServerSentEvent]:
    client = httpx.AsyncClient()
    headers = kwargs.pop("headers", {})
    headers["Accept"] = "text/event-stream"
    headers["Cache-Control"] = "no-store"

    async with client.stream(method, url, headers=headers, **kwargs) as response:
        async for event in EventSource(response).aiter_sse():
            yield event
