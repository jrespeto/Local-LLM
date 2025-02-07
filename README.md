# RAG_Local LLM

To run have on a system with a GPU

Before using podman make sure containers have GPU access.

https://podman-desktop.io/docs/podman/gpu

podman-compose version >= 1.2.0

docker-compose with podman does not pass the GPU to the container

## Running

This compose has 7 containers.

openWebUI - API's to ollama and

ollama - LLM management

qdrant

Langflow
    postgresql

searxng
    valkey

---

To start the containers

`podman-compose up -d`

To follow the logs

`podman-compose logs --follow`

To stop

`podman-compose down`


To remove volums from the containers

`podman volume ls`

`podman volume rm volume_name`
