# RAG_Local LLM

To run this on as system with a GPU, you need the container tool kit installed on your system. Review the podman doc link below.

Before using podman make sure containers have GPU access.

https://podman-desktop.io/docs/podman/gpu

podman-compose version >= 1.2.0

docker-compose with podman does not pass the GPU to the container

## Running

This compose has 8 containers.

openWebUI - API's to ollama and

ollama - LLM management

qdrant

Langflow
    postgresql

searxng - local search engin aggrator
    valkey

comfyui - image generation

---

To start the containers

`podman-compose up -d`

To start up the containers and comfyui

`podman-compose --profile comfyui up -d`s

To follow the logs

`podman-compose logs --follow`

To stop

`podman-compose down`

To working with volums from the containers

`podman volume ls` - list all the volums

`podman volume inspect volume_name` - this lets you see the mount points

`podman volume rm volume_name` - this is to remove the volume

## ComfyUI

You may need to update the FROM line in docker/dockerfile.comfyui for your systems version of cuda.

Watch the youtube links below on how to setup and use ComfyUI. Set the play speep to 1.5 :)

### openwebui

This will allow you to use comfyui to generate images with a default workflow.

ComfyUI is very advanced and can do way more then just image generation.

To intergrate ComfyUI with openwebUI you need to update the image setting under Admin settings.

![alt text](docs/images/image.png)

If you update the "ComfyUI Workflow" you need to updated the "ComfyUI Workflow Nodes".

i.e - node 3 is the object with seed and steps

You also need to set a default Model. Watch the video's and playlist below to understand which models "depending on  the ammount of vram on your GPU" and settings to use.

#### References Repos

- https://github.com/Teachings/AIServerSetup

#### Reference Youtube

- https://www.youtube.com/watch?v=Z914egVyXBw
- https://www.youtube.com/playlist?list=PL-pohOSaL8P9kLZP8tQ1K1QWdZEgwiBM0
