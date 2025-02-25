
# Check if file does not exist

mv /app/styles.csv /app/styles/

git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Manager.git /app/custom_nodes/ComfyUI-Manager
pip install -r /app/custom_nodes/ComfyUI-Manager/requirements.txt

# Clone and install GGUF support for ComfyUI
git clone --depth 1 https://github.com/city96/ComfyUI-GGUF.git /app/custom_nodes/ComfyUI-GGUF
pip install --upgrade gguf

git clone --depth 1 https://github.com/WASasquatch/was-node-suite-comfyui.git /app/custom_nodes/was-node-suite-comfyui
pip install -r /app/custom_nodes/was-node-suite-comfyui/requirements.txt
sed -i 's~null~/app/styles/styles.csv~' /app/custom_nodes/was-node-suite-comfyui/was_suite_config.json
sed -i 's~/path/to/ffmpeg~/usr/bin/ffmpeg~' /app/custom_nodes/was-node-suite-comfyui/was_suite_config.json

git clone --depth 1 https://github.com/yolain/ComfyUI-Easy-Use.git /app/custom_nodes/ComfyUI-Easy-Use
pip install -r /app/custom_nodes/ComfyUI-Easy-Use/requirements.txt

git clone --depth 1 https://github.com/stavsap/comfyui-ollama.git /app/custom_nodes/comfyui-ollama
pip install -r /app/custom_nodes/comfyui-ollama/requirements.txt

git clone --depth 1 https://github.com/crystian/ComfyUI-Crystools.git /app/custom_nodes/ComfyUI-Crystools
pip install -r /app/custom_nodes/ComfyUI-Crystools/requirements.txt

git clone --depth 1 https://github.com/rgthree/rgthree-comfy.git /app/custom_nodes/rgthree-comfy
pip install -r /app/custom_nodes/rgthree-comfy/requirements.txt

git clone --depth 1 https://github.com/ssitu/ComfyUI_UltimateSDUpscale.git /app/custom_nodes/ComfyUI_UltimateSDUpscale
pip install -r /app/custom_nodes/ComfyUI_UltimateSDUpscale/requirements.txt

git clone --depth 1 https://github.com/Fannovel16/comfyui_controlnet_aux.git /app/custom_nodes/comfyui_controlnet_aux
pip install -r /app/custom_nodes/comfyui_controlnet_aux/requirements.txt

git clone --depth 1 https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes.git /app/custom_nodes/ComfyUI_Comfyroll_CustomNodes


# Run ComfyUI with the server binding to 0.0.0.0
python3 main.py --listen 0.0.0.0
