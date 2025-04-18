# SSE-Client
A lightweight SSE client that uses the httpx package based on [httpx-sse](https://github.com/florimondmanca/httpx-sse).

> [!WARNING]
> **This python package is currently in beta and will likely change. It is not yet ready for production use.**

## Installation
```bash
pip install sse-client
```

## Usage
#### Synchronous
```python
from sse_client import stream

for event in stream("https://example.com/sse"):
    print(event)
```

#### Asynchronous
```python
from sse_client import async_stream

async for event in async_stream("https://example.com/sse"):
    print(event)
```

#### Stream/ Async Stream Interface
The `stream` and `async_stream` functions follow the [httpx.request()](https://www.python-httpx.org/api/) interface.

```python
stream(method, url, *, params=None, content=None, data=None, files=None, json=None, headers=None, cookies=None, auth=None, proxy=None, timeout=Timeout(timeout=5.0), follow_redirects=False, verify=True, trust_env=True)
```

```python
async_stream(method, url, *, params=None, content=None, data=None, files=None, json=None, headers=None, cookies=None, auth=None, proxy=None, timeout=Timeout(timeout=5.0), follow_redirects=False, verify=True, trust_env=True)
```

Both functions connect to an SSE endpoint and yield ServerSentEvent objects.

Parameters:

- `method` - HTTP method for the new Request object: GET, OPTIONS, HEAD, POST, PUT, PATCH, or DELETE.
- `url` - URL for the new Request object.
- `params` - (Optional) Query parameters to include in the URL, as a string, dictionary, or sequence of two-tuples.
- `content` - (Optional) Binary content to include in the body of the request, as bytes or a byte iterator.
- `data` - (Optional) Form data to include in the body of the request, as a dictionary.
- `files` - (Optional) A dictionary of upload files to include in the body of the request.
- `json` - (Optional) A JSON serializable object to include in the body of the request.
- `headers` - (Optional) Dictionary of HTTP headers to include in the request.
- `cookies` - (Optional) Dictionary of Cookie items to include in the request.
- `auth` - (Optional) An authentication class to use when sending the request.
- `proxy` - (Optional) A proxy URL where all the traffic should be routed.
- `timeout` - (Optional) The timeout configuration to use when sending the request.
- `follow_redirects` - (Optional) Enables or disables HTTP redirects.
- `verify` - (Optional) Either True to use an SSL context with the default CA bundle, False to disable verification, or an instance of ssl.SSLContext to use a custom context.
- `trust_env` - (Optional) Enables or disables usage of environment variables for configuration.

`stream` returns an `Iterator[ServerSentEvent]` and `async_stream` returns an `AsyncIterator[ServerSentEvent]`.