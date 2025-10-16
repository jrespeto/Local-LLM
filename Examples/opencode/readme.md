# opencode with ollama models

## Setup opencode configs

For this setup you want to start up openwebui or ollama containers.

`podman-compose --profile openwebui up -d`

Login to your openwebui and get your API key.

Copy the `opencode-openwebui.json` to `~/.config/opencode/opencode.json`

Update the `sk-###########################` with your api token.

You can remove the models in the config if you dont have them and replace them with models you do have.

I been seeing that qwen3:8b works most of the time.

To download a model, such as `qwen3:8b` with openwebui.

## Updating Model Settings 16k

The default context length Ollama has set it 4096 for the models.

Even though ollama says the context is larger, for example for qwen3 it
says context is around 40k, upon running the model via ollama, it will use a default
of 4k context, this **has** to be setup by yourself. Also make sure the model
you are planning to use actually supports *agentic* tools.

This is how you can update the model setting to increase the context length.


```bash
$ podman exec -it ollama bash
$ ollama pull qwen3:8b # if you dont have it already
$ ollama run qwen3:8b
>>> /set parameter num_ctx 16384
Set parameter 'num_ctx' to '16384'
>>> /save qwen3:8b-16k
Created new model 'qwen3:8b-16k'
>>> /bye
```

## Troubleshooting

### Cert Errors

If you have cert errors or using self signed certs.

`export NODE_TLS_REJECT_UNAUTHORIZED=0`

### Reviewing logs

Running test to view logs.

`opencode run -m ollama/qwen3:30b-16k --print-logs --log-level DEBUG test`

### Dissble Thinking

To Dissble thinking you can use prompts or with model options.

`/no_think befor the promote`


```json
"qwen3:8b-16k":{
    "options": {
        "thinking": {
            "type": "false"
        },
    },
    "tools": true
}

```

## Reference

Docs: https://opencode.ai/docs/config/


https://github.com/p-lemonish/ollama-x-opencode/blob/main/README.md
