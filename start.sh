#!/usr/bin/env bash
# ---------------------------------------------------------------------------- #
#                          Function Definitions                                #
# ---------------------------------------------------------------------------- #

# (Unmodified functions from the original start.sh)
check_cuda_version() {
    echo "Checking CUDA version using nvidia-smi..."
    CURRENT_CUDA_VERSION=$(nvidia-smi | grep -oP "CUDA Version: \K[0-9.]+")
    if [[ -z "${CURRENT_CUDA_VERSION}" ]]; then
        echo "CUDA version not found. Make sure that CUDA is properly installed and 'nvidia-smi' is available."
        exit 1
    fi
    echo "Detected CUDA version using nvidia-smi: ${CURRENT_CUDA_VERSION}"
    IFS='.' read -r -a CURRENT_CUDA_VERSION_ARRAY <<< "${CURRENT_CUDA_VERSION}"
    CURRENT_CUDA_VERSION_MAJOR="${CURRENT_CUDA_VERSION_ARRAY[0]}"
    CURRENT_CUDA_VERSION_MINOR="${CURRENT_CUDA_VERSION_ARRAY[1]}"
    IFS='.' read -r -a REQUIRED_CUDA_VERSION_ARRAY <<< "${REQUIRED_CUDA_VERSION}"
    REQUIRED_CUDA_VERSION_MAJOR="${REQUIRED_CUDA_VERSION_ARRAY[0]}"
    REQUIRED_CUDA_VERSION_MINOR="${REQUIRED_CUDA_VERSION_ARRAY[1]}"
    if [[ "${CURRENT_CUDA_VERSION_MAJOR}" -lt "${REQUIRED_CUDA_VERSION_MAJOR}" || ( "${CURRENT_CUDA_VERSION_MAJOR}" -eq "${REQUIRED_CUDA_VERSION_MAJOR}" && "${CURRENT_CUDA_VERSION_MINOR}" -lt "${REQUIRED_CUDA_VERSION_MINOR}" ) ]]; then
        echo "Current CUDA version (${CURRENT_CUDA_VERSION}) is older than required (${REQUIRED_CUDA_VERSION})."
        echo "Please switch to a pod with CUDA version ${REQUIRED_CUDA_VERSION} or higher by selecting the appropriate filter on Pod deploy."
        exit 1
    else
        echo "CUDA version from nvidia-smi seems sufficient: ${CURRENT_CUDA_VERSION}"
    fi
}

test_pytorch_cuda() {
    echo "Performing a simple CUDA functionality test using PyTorch..."
    python3 - <<END
import sys
import torch
try:
    if not torch.cuda.is_available():
        print("CUDA is not available on this system.")
        sys.exit(1)
    cuda_version = torch.version.cuda
    if cuda_version is None:
        print("Could not determine CUDA version using PyTorch.")
        sys.exit(1)
    print(f"From PyTorch test, your CUDA version meets the requirement: {cuda_version}")
    num_gpus = torch.cuda.device_count()
    print(f"Number of CUDA-capable devices: {num_gpus}")
    for i in range(num_gpus):
        print(f"Device {i}: {torch.cuda.get_device_name(i)}")
except RuntimeError as e:
    print(f"Runtime error: {e}")
    sys.exit(2)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit(1)
END
    if [[ $? -ne 0 ]]; then
        echo "PyTorch CUDA test failed. Please switch to a pod with a proper CUDA setup."
        exit 1
    else
        echo "CUDA version is sufficient and functional."
    fi
}

start_nginx() {
    echo "NGINX: Starting Nginx service..."
    service nginx start
}

execute_script() {
    local script_path=$1
    local script_msg=$2
    if [[ -f ${script_path} ]]; then
        echo "${script_msg}"
        bash ${script_path}
    fi
}

generate_ssh_host_keys() {
    if [ ! -f /etc/ssh/ssh_host_rsa_key ]; then
        ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -q -N ''
    fi
    if [ ! -f /etc/ssh/ssh_host_dsa_key ]; then
        ssh-keygen -t dsa -f /etc/ssh/ssh_host_dsa_key -q -N ''
    fi
    if [ ! -f /etc/ssh/ssh_host_ecdsa_key ]; then
        ssh-keygen -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key -q -N ''
    fi
    if [ ! -f /etc/ssh/ssh_host_ed25519_key ]; then
        ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -q -N ''
    fi
}

setup_ssh() {
    echo "SSH: Setting up SSH..."
    mkdir -p ~/.ssh
    if [[ ${PUBLIC_KEY} ]]; then
        echo -e "${PUBLIC_KEY}\n" >> ~/.ssh/authorized_keys
    fi
    chmod 700 -R ~/.ssh
    generate_ssh_host_keys
    service ssh start
    echo "SSH: Host keys:"
    cat /etc/ssh/*.pub
}

export_env_vars() {
    echo "ENV: Exporting environment variables..."
    printenv | grep -E '^RUNPOD_|^PATH=|^_=' | awk -F = '{ print "export " $1 "=\"" $2 "\"" }' >> /etc/rp_environment
    echo 'source /etc/rp_environment' >> ~/.bashrc
}

start_jupyter() {
    JUPYTER_PASSWORD=""
    if [[ ${JUPYTER_LAB_PASSWORD} ]]; then
        JUPYTER_PASSWORD=${JUPYTER_LAB_PASSWORD}
    fi
    echo "JUPYTER: Starting Jupyter Lab..."
    mkdir -p /workspace/logs
    cd / && \
    nohup jupyter lab --allow-root \
      --no-browser \
      --port=8888 \
      --ip=* \
      --FileContentsManager.delete_to_trash=False \
      --ContentsManager.allow_hidden=True \
      --ServerApp.terminado_settings='{"shell_command":["/bin/bash"]}' \
      --ServerApp.token=${JUPYTER_PASSWORD} \
      --ServerApp.allow_origin=* \
      --ServerApp.preferred_dir=/workspace &> /workspace/logs/jupyter.log &
    echo "JUPYTER: Jupyter Lab started"
}

start_code_server() {
    echo "CODE-SERVER: Starting Code Server..."
    mkdir -p /workspace/logs
    nohup code-server \
        --bind-addr 0.0.0.0:7777 \
        --auth none \
        --enable-proposed-api true \
        --disable-telemetry \
        /workspace &> /workspace/logs/code-server.log &
    echo "CODE-SERVER: Code Server started"
}

start_runpod_uploader() {
    echo "RUNPOD-UPLOADER: Starting RunPod Uploader..."
    nohup /usr/local/bin/runpod-uploader &> /workspace/logs/runpod-uploader.log &
    echo "RUNPOD-UPLOADER: RunPod Uploader started"
}

configure_filezilla() {
    if [[ ! -z "${RUNPOD_PUBLIC_IP}" ]]; then
        hostname="${RUNPOD_PUBLIC_IP}"
        port="${RUNPOD_TCP_PORT_22}"
        password=$(openssl rand -base64 12)
        echo "root:${password}" | chpasswd
        ssh_config="/etc/ssh/sshd_config"
        grep -q "^PasswordAuthentication" ${ssh_config} && \
          sed -i "s/^PasswordAuthentication.*/PasswordAuthentication yes/" ${ssh_config} || \
          echo "PasswordAuthentication yes" >> ${ssh_config}
        grep -q "^PermitRootLogin" ${ssh_config} && \
          sed -i "s/^PermitRootLogin.*/PermitRootLogin yes/" ${ssh_config} || \
          echo "PermitRootLogin yes" >> ${ssh_config}
        service ssh restart
        filezilla_config_file="/workspace/filezilla_sftp_config.xml"
        cat > ${filezilla_config_file} << EOF
<?xml version="1.0" encoding="UTF-8"?>
<FileZilla3 version="3.66.1" platform="linux">
    <Servers>
        <Server>
            <Host>${hostname}</Host>
            <Port>${port}</Port>
            <Protocol>1</Protocol>
            <Type>0</Type>
            <User>root</User>
            <Pass encoding="base64">$(echo -n ${password} | base64)</Pass>
            <Logontype>1</Logontype>
            <EncodingType>Auto</EncodingType>
            <BypassProxy>0</BypassProxy>
            <Name>Generated Server</Name>
            <RemoteDir>/workspace</RemoteDir>
            <SyncBrowsing>0</SyncBrowsing>
            <DirectoryComparison>0</DirectoryComparison>
        </Server>
    </Servers>
</FileZilla3>
EOF
        echo "FILEZILLA: FileZilla SFTP configuration file created at: ${filezilla_config_file}"
    else
        echo "FILEZILLA: RUNPOD_PUBLIC_IP is not set. Skipping FileZilla configuration."
    fi
}

update_rclone() {
    echo "RCLONE: Updating rclone..."
    rclone selfupdate
}

start_cron() {
    echo "CRON: Starting Cron service..."
    service cron start
}

check_python_version() {
    echo "PYTHON: Checking Python version..."
    python3 -V
}

# ---------------------------------------------------------------------------- #
#                               Main Program                                   #
# ---------------------------------------------------------------------------- #

echo "Container Started, configuration in progress..."

start_nginx
setup_ssh
start_cron
start_jupyter
start_code_server
# Optionally, uncomment these lines if you need CUDA validation:
# check_cuda_version
# test_pytorch_cuda
start_runpod_uploader

execute_script "/pre_start.sh" "PRE-START: Running pre-start script..."

# --- [CUSTOM CHANGE IN SPINX] Merge custom nodes BEFORE post-start hooks ---
echo "Merging custom nodes into /workspace/ComfyUI/custom_nodes..."
rsync -av --ignore-existing /sphinxfiles/comfyUI/custom_nodes/ /workspace/ComfyUI/custom_nodes/ && \
  echo "Custom nodes successfully merged." || \
  echo "Failed to merge custom nodes."
# --- End CUSTOM CHANGE ---

# --- Add our custom app setup ---
# Create required directories
mkdir -p /workspace/app/client
mkdir -p /workspace/app/workflows  # Add directory for custom workflows
mkdir -p /workspace/ComfyUI/custom_nodes

# Copy files only if they don't exist
if [ ! -f "/workspace/app/app.py" ]; then
    cp /sphinxfiles/app/app.py /workspace/app/
    echo "Copied app.py to workspace"
fi

if [ ! -f "/workspace/app/workflow_manager.py" ]; then
    cp /sphinxfiles/app/workflow_manager.py /workspace/app/
    echo "Copied workflow_manager.py to workspace"
fi

if [ ! -f "/workspace/app/workflow.json" ]; then
    cp /sphinxfiles/app/workflow.json /workspace/app/
    echo "Copied workflow.json to workspace"
fi

if [ ! -f "/workspace/app/run_video_workflow.py" ]; then
    cp /sphinxfiles/app/run_video_workflow.py /workspace/app/ 2>/dev/null || echo "No run_video_workflow.py in sphinxfiles"
fi

if [ ! -f "/workspace/app/sabins_workflow_api.json" ]; then
    cp /sphinxfiles/app/sabins_workflow_api.json /workspace/app/ 2>/dev/null || echo "No sabins_workflow_api.json in sphinxfiles"
fi

# Copy client files individually to prevent overwriting
if [ ! -f "/workspace/app/client/index.html" ]; then
    cp /sphinxfiles/app/client/index.html /workspace/app/client/ 2>/dev/null || echo "No index.html in sphinxfiles"
fi

if [ ! -f "/workspace/app/client/gui.html" ]; then
    cp /sphinxfiles/app/client/gui.html /workspace/app/client/ 2>/dev/null || echo "No gui.html in sphinxfiles"
fi

if [ ! -f "/workspace/app/client/projection.html" ]; then
    cp /sphinxfiles/app/client/projection.html /workspace/app/client/ 2>/dev/null || echo "No projection.html in sphinxfiles"
fi

if [ ! -f "/workspace/app/client/script.js" ]; then
    cp /sphinxfiles/app/client/script.js /workspace/app/client/ 2>/dev/null || echo "No script.js in sphinxfiles"
fi

if [ ! -f "/workspace/app/client/style.css" ]; then
    cp /sphinxfiles/app/client/style.css /workspace/app/client/ 2>/dev/null || echo "No style.css in sphinxfiles"
fi

# Copy custom nodes only if they don't exist
for node_file in /sphinxfiles/ComfyUI/custom_nodes/*; do
    if [ -f "$node_file" ]; then
        basename=$(basename "$node_file")
        if [ ! -f "/workspace/ComfyUI/custom_nodes/$basename" ]; then
            cp "$node_file" /workspace/ComfyUI/custom_nodes/
            echo "Copied custom node $basename to workspace"
        fi
    fi
done

# Start ComfyUI in the background
cd /workspace/ComfyUI && python main.py --listen 0.0.0.0 --port 3020 &

# Wait for ComfyUI to start
sleep 5

# Start Flask app
cd /workspace/app && python app.py

execute_script "/post_start.sh" "POST-START: Running post-start script..."

echo "Container is READY!"

# start your custom Sphinx API in the background
nohup python3 /workspace/app/app.py &> /workspace/logs/fastapi.log &
echo "Custom API started in background."

# Keep the container alive
exec sleep infinity
