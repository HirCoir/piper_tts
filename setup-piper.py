import importlib
import subprocess
import sys
import os
import urllib.request
import tarfile
import platform

def install_tqdm():
    try:
        importlib.import_module('tqdm')
        print("tqdm is already installed.")
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "tqdm"])
            print("tqdm has been installed successfully.")
        except subprocess.CalledProcessError:
            print("An error occurred while installing tqdm. Make sure you have pip installed on your system.")
install_tqdm()
from tqdm import tqdm

work_dir = os.path.dirname(os.path.abspath(__file__))
model_dir = os.path.join(work_dir, "model")
DOWNLOAD_URL_BASE = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/"

def download_with_progress(url, target_path):
    response = urllib.request.urlopen(url)
    total_size = int(response.info().get("Content-Length", -1))
    block_size = 1024
    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
    with open(target_path, 'wb') as file:
        while True:
            buffer = response.read(block_size)
            if not buffer:
                break
            file.write(buffer)
            progress_bar.update(len(buffer))
    progress_bar.close()

arch = platform.machine()
if arch == "x86_64":
    DOWNLOAD_URL = DOWNLOAD_URL_BASE + "piper_linux_x86_64.tar.gz"
elif arch == "armv7l":
    DOWNLOAD_URL = DOWNLOAD_URL_BASE + "piper_linux_armv7l.tar.gz"
elif arch == "aarch64":
    DOWNLOAD_URL = DOWNLOAD_URL_BASE + "piper_linux_aarch64.tar.gz"
else:
    print("Unsupported architecture:", arch)
    exit(1)

file_name = "piper.tar.gz"
file_path = os.path.join(work_dir, file_name)
download_with_progress(DOWNLOAD_URL, file_path)

with tarfile.open(file_path, "r:gz") as tar:
    tar.extractall(path=work_dir)

os.remove(file_path)
print("Piper has been downloaded and extracted successfully.")

download_models = input("Do you want to download a default voice model? (yes/no): ").strip().lower() == "yes"
if download_models:
    models_dir = model_dir
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    print("Available models: es_MX (Spanish Mexico), en_US (English US)")
    model_choice = input("Enter the language of the voice model you want to download: ").strip()
    models = {
    "es_MX": {
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_MX/claude/high/es_MX-claude-high.onnx",
        "url_json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_MX/claude/high/es_MX-claude-high.onnx.json"
            },
    "en_US": {
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/high/en_US-lessac-high.onnx",
        "url_json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/high/en_US-lessac-high.onnx.json"
        }
    }
    if model_choice in models:
        for file_key in ["url", "url_json"]:
            file_url = models[model_choice][file_key]
            file_name = file_url.split("/")[-1]
            file_save_path = os.path.join(models_dir, file_name)
            urllib.request.urlretrieve(file_url, file_save_path)
        print(f"Model {model_choice} downloaded successfully to {models_dir}")
    else:
        print("Invalid model choice.")
