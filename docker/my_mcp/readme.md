# MCP Python Server (Add, Greet, HN RSS) — Local & Podman/Nginx

A minimal **Model Context Protocol (MCP)** server in Python with three example tools:

1. `add(a, b)` – add two numbers
2. `greet(name)` – return a friendly greeting
3. `get_hn_newest(limit)` – fetch newest Hacker News posts from `https://hnrss.org/newest`

This README matches your repo layout and uses **Podman** (with optional `podman-compose`) to run the MCP server behind **Nginx**.

---

## Directory Layout

```
my_mcp
├─ src/
│  ├─ server.py                # MCP server (FastMCP) with 3 tools
│  ├─ client_streamable.py     # Minimal client for HTTP testing
│  └─ requirements.txt         # Python deps
│
├─ dockerfile.mcp              # MCP server container
├─ docker-compose-mcp.yml      # Nginx + MCP services (compose-compatible)
└─ nginx.conf                  # Reverse proxy to MCP server
```

---

## Prerequisites

* Python **3.11+**
* Podman **4+**
* Optional: `podman-compose` (to use `docker-compose-mcp.yml` as-is)
* Optional: **OpenCode** (to consume the MCP server from the IDE/agent)

---

## What’s in the code

### `src/server.py`

* Uses `FastMCP("DemoMCP", host="0.0.0.0", port=8000)`, so the HTTP server binds on all interfaces (container-friendly).
* Switches transports via `MCP_TRANSPORT`:

  * `stdio` (default) for local dev and the MCP Inspector
  * `http` for Streamable HTTP (production/reverse proxy friendly)
* Tools: `add`, `greet`, `get_hn_newest (feedparser + hnrss.org/newest)`

### `src/client_streamable.py`

* Uses the Streamable HTTP client:

  ```py
  from mcp import ClientSession
  from mcp.client.streamable_http import streamablehttp_client
  ```

* Default `base_url` is `http://localhost:8081/mcp` (Nginx on host port **8081**).
  Override with `MCP_BASE_URL`.

### `nginx.conf`

* Proxies `/mcp` → `http://mcp:8000/mcp`
* Disables buffering for streaming
* Adds permissive CORS headers (tighten for prod)
* `/` responds with `ok` for a quick health probe

### `dockerfile.mcp`

* Builds from `python:3.11-slim`
* Copies `src/` into `/app`
* Installs from `requirements.txt`
* Exposes `8000`
* Sets `MCP_TRANSPORT=http` and runs `server.py`

---

## Local Development (no containers)

### 1) Install

```bash
cd my_mcp
python -m venv .venv && . .venv/bin/activate
pip install -r src/requirements.txt
```

### 2) Run in stdio (best with MCP Inspector)

```bash
export MCP_TRANSPORT=stdio
# If the 'mcp' CLI is installed via the SDK:
mcp dev src/server.py
```

### 3) Run Streamable HTTP locally

```bash
export MCP_TRANSPORT=http
python src/server.py
# → http://localhost:8000/mcp
```

### 4) Try the tiny HTTP client

```bash
export MCP_BASE_URL=http://localhost:8000/mcp
python src/client_streamable.py
```

---

## Running with Podman

You can run with **plain Podman** or with **podman-compose**. Pick one.

### Option A — Plain Podman (pods + manual wiring)

Create a **pod** (shares network/ports) and run both containers into it:

```bash
cd my_mcp

# 1) Build the MCP image from dockerfile.mcp
podman build -t demo-mcp -f dockerfile.mcp .

# 2) Create a pod that exposes 8081 on the host (mapped to 80 inside the pod)
podman pod create --name mcp-pod -p 8081:80

# 3) Run the MCP server container (in the pod)
podman run -d --name mcp --pod mcp-pod demo-mcp

# 4) Run Nginx (in the pod), mounting your nginx.conf
podman run -d --name mcp-nginx --pod mcp-pod \
  -v "$(pwd)/nginx.conf:/etc/nginx/conf.d/default.conf:ro" \
  docker.io/library/nginx:alpine
```

Test from the **host**:

```bash
curl http://localhost:8081/         # -> ok
curl -i http://localhost:8081/mcp   # 400/405 is fine (endpoint exists)
```

Run the client from the **host** (through Nginx):

```bash
export MCP_BASE_URL=http://localhost:8081/mcp
python src/client_streamable.py
```

Run the client from **inside the MCP container**:

```bash
podman exec -it mcp bash
export MCP_BASE_URL=http://localhost:8000/mcp   # bypass Nginx from inside this container
python client_streamable.py
```

> Notes
>
> * Inside the **pod**, service DNS names also work (e.g., `http://mcp:8000/mcp` or `http://mcp-nginx:80/mcp`).
> * We explicitly bound the server on `0.0.0.0` in `server.py`, so Nginx can reach it.

### Option B — `podman-compose` (compose file you already have)

If you have `podman-compose` installed, you can reuse `docker-compose-mcp.yml`.

1. Ensure your compose file maps **host 8081 → container 80** for Nginx, and **exposes 8000** for the MCP container. Example:

```yaml
# docker-compose.yml (example)
include:
  - docker-compose-openwebui.yml
  - docker-compose-ollama.yml
  - docker-compose-mcp.yml

# docker-compose-mcp.yml (example)
include:
  - docker-compose-common.yml

version: "3.9"
services:
  mcp:
    profiles:
      - mcp
    build:
      context: .
      dockerfile: dockerfile.mcp
    container_name: mcp
    hostname: mcp
    environment:
      - MCP_TRANSPORT=http
    # ports:
    # - "8000:8000" # optional direct access (bypass Nginx)

# docker-compose-common.yml (example)
version: "3.9"
services:
  nginx:
    profiles:
      - mcp
    image: nginx:alpine
    container_name: mcp-nginx
    depends_on:
      - mcp
    volumes:
      - ./data/nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    ports:
      - "8081:80"    # host:container
```

2. Launch:

```bash
podman-compose ---profile mcp up --build -d
```

3. Test from the **host**:

```bash
curl http://localhost:8081/         # -> ok
python src/client_streamable.py      # defaults to http://localhost:8081/mcp
```

Stop:

```bash
podman-compose ---profile mcp down
```

---

## OpenCode Configuration (optional)

Add the MCP endpoint so OpenCode can use the tools.

**Remote (Nginx proxy at [http://localhost:8081/mcp](http://localhost:8081/mcp)):**

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "demo-mcp-remote": {
      "type": "remote",
      "url": "http://localhost:8081/mcp",
      "enabled": true
    }
  }
}
```

**Local (spawned process, stdio) for development:**

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "demo-mcp-local": {
      "type": "local",
      "command": ["python", "src/server.py"],
      "enabled": true,
      "environment": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

> Put this in `~/.config/opencode/opencode.json` (global) or in your project as `./opencode.json`. Restart OpenCode after changes.

---

## Troubleshooting

**1) Connection failed from inside container**
Don’t use host `localhost:8081` from inside a container. Use:

* `http://localhost:8000/mcp` from **inside the MCP container** (bypasses Nginx), or
* `http://mcp:8000/mcp` / `http://mcp-nginx:80/mcp` via container DNS (pod network).

**2) Nginx can’t reach MCP**
Make sure the server binds to all interfaces (already handled):

```py
mcp = FastMCP("DemoMCP", host="0.0.0.0", port=8000)
```

**3) CORS / browser issues**
`nginx.conf` includes permissive headers for dev. Tighten `Access-Control-Allow-Origin` for prod.

**4) Health check returns 400/405**
That’s normal when curling `/mcp` without a streaming POST body; it still proves the route exists.

---

## Extending

Add new tools with a decorator:

```py
@mcp.tool()
def echo(text: str) -> str:
    """Echo text back."""
    return text
```

---

## License

MIT. Have fun building! 🚀
