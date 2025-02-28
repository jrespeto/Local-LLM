
# Check if file does not exist

cd /app

rm -rf /app/output
rm -rf /app/models
rm -rf /app/custom_nodes
rm -rf /app/styles
rm -rf /app/user

mkdir -p /comfyui/output /comfyui/models /comfyui/custom_nodes /comfyui/styles /comfyui/user

ln -s /comfyui/output /app/output
ln -s /comfyui/models /app/models
ln -s /comfyui/custom_nodes /app/custom_nodes
ln -s /comfyui/styles /app/styles
ln -s /comfyui/user /app/user

mv /app/styles.csv /app/styles/

# Clone or update
if [ ! -d "/app/custom_nodes/ComfyUI-Manager" ]; then
    git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Manager.git /app/custom_nodes/ComfyUI-Manager
else
    cd /app/custom_nodes/ComfyUI-Manager
    git pull
    cd -
fi

pip install -r /app/custom_nodes/ComfyUI-Manager/requirements.txt

# Clone and install GGUF support for ComfyUI

if [ ! -d "/app/custom_nodes/ComfyUI-GGUF" ]; then
    git clone --depth 1 https://github.com/city96/ComfyUI-GGUF.git /app/custom_nodes/ComfyUI-GGUF
else
    cd /app/custom_nodes/ComfyUI-GGUF
    git pull
    cd -
fi

pip install --upgrade gguf

if [ ! -d "/app/custom_nodes/was-node-suite-comfyui" ]; then
    git clone --depth 1 https://github.com/WASasquatch/was-node-suite-comfyui.git /app/custom_nodes/was-node-suite-comfyui
else
    cd /app/custom_nodes/was-node-suite-comfyui
    git pull
    cd -
fi

pip install -r /app/custom_nodes/was-node-suite-comfyui/requirements.txt
sed -i 's~null~/app/styles/styles.csv~' /app/custom_nodes/was-node-suite-comfyui/was_suite_config.json
sed -i 's~/path/to/ffmpeg~/usr/bin/ffmpeg~' /app/custom_nodes/was-node-suite-comfyui/was_suite_config.json

if [ ! -d "/app/custom_nodes/ComfyUI-Easy-Use" ]; then
    git clone --depth 1 https://github.com/yolain/ComfyUI-Easy-Use.git /app/custom_nodes/ComfyUI-Easy-Use
else
    cd /app/custom_nodes/ComfyUI-Easy-Use
    git pull
    cd -
fi

pip install -r /app/custom_nodes/ComfyUI-Easy-Use/requirements.txt

if [ ! -d "/app/custom_nodes/comfyui-ollama" ]; then
    git clone --depth 1 https://github.com/stavsap/comfyui-ollama.git /app/custom_nodes/comfyui-ollama
else
    cd /app/custom_nodes/comfyui-ollama
    git pull
    cd -
fi

pip install -r /app/custom_nodes/comfyui-ollama/requirements.txt

if [ ! -d "/app/custom_nodes/ComfyUI-Crystools" ]; then
    git clone --depth 1 https://github.com/crystian/ComfyUI-Crystools.git /app/custom_nodes/ComfyUI-Crystools
else
    cd /app/custom_nodes/ComfyUI-Crystools
    git pull
    cd -
fi
pip install -r /app/custom_nodes/ComfyUI-Crystools/requirements.txt

if [ ! -d "/app/custom_nodes/rgthree-comfy" ]; then
    git clone --depth 1 https://github.com/rgthree/rgthree-comfy.git /app/custom_nodes/rgthree-comfy
else
    cd /app/custom_nodes/rgthree-comfy
    git pull
    cd -
fi

pip install -r /app/custom_nodes/rgthree-comfy/requirements.txt

if [ ! -d "/app/custom_nodes/ComfyUI_UltimateSDUpscale" ]; then
    git clone https://github.com/ssitu/ComfyUI_UltimateSDUpscale --recursive /app/custom_nodes/ComfyUI_UltimateSDUpscale
else
    cd /app/custom_nodes/ComfyUI_UltimateSDUpscale
    git pull
    cd -
fi

if [ ! -d "/app/custom_nodes/comfyui_controlnet_aux" ]; then
    git clone --depth 1 https://github.com/Fannovel16/comfyui_controlnet_aux.git /app/custom_nodes/comfyui_controlnet_aux
else
    cd /app/custom_nodes/comfyui_controlnet_aux
    git pull
    cd -
fi

pip install -r /app/custom_nodes/comfyui_controlnet_aux/requirements.txt

if [ ! -d "/app/custom_nodes/ComfyUI_Comfyroll_CustomNodes" ]; then
    git clone --depth 1 https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes.git /app/custom_nodes/ComfyUI_Comfyroll_CustomNodes
else
    cd /app/custom_nodes/ComfyUI_Comfyroll_CustomNodes
    git pull
    cd -
fi

# Run ComfyUI with the server binding to 0.0.0.0
python3 main.py --listen 0.0.0.0
