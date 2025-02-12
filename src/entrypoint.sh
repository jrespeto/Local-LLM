
# Check if file does not exist
if [ ! -f "/app/custom_nodes/no_init" ] ; then

    touch /app/custom_nodes/no_init
    git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Manager.git /app/custom_nodes/ComfyUI-Manager && \
    pip install -r /app/custom_nodes/ComfyUI-Manager/requirements.txt

# Clone and install GGUF support for ComfyUI
    git clone --depth 1 https://github.com/city96/ComfyUI-GGUF.git /app/custom_nodes/ComfyUI-GGUF && \
    pip install --upgrade gguf

fi

# Run ComfyUI with the server binding to 0.0.0.0
python3 main.py --listen 0.0.0.0
