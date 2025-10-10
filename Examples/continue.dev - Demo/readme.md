
# Continue Dev Demo

Start openweb-ui with podman-compose --profile openwebui up -d

## 1. Setup OpenWeb UI API Key

Setup your local account. If you have not done so yet.

Click on you avitar and select settings.

Click on Account

click on show next to the API key

Copy the api key and paste into the config.yaml file here over writing YOUR_TOKEN 3 times.

## 2. Setup OpenWeb UI Model

Go to the openwebui admin Panel -> Setting -> Models

Click on Manage Models.

Past in `qwen2.5-coder:7b-base` in the pull model from ollama.com

## 3. Setup VS Code continue.dev extension

Open vscode clicl on Extentions

Search for `Continue - open-source AI code agent` from the extentions marketplace.

Install it and restart your VS Code instance.

Copy the config to your config folder.

`cp config.yaml ~/.continue/config.yaml`

