# Raspberry Pi Voice Assistant Setup

This guide will help you set up the **Voice Assistant project** on a Raspberry Pi. Follow the steps carefully—Pi setups can be tricky, especially with Python dependencies.

---

## 1. Raspberry Pi Setup

- Use the **latest Raspberry Pi OS (PIOS)**.
- **Important:** The project requires **Python 3.9**. Install it manually if your Pi comes with a different version.

---

## 2. Install Python 3.9

```bash
cd /tmp
wget https://www.python.org/ftp/python/3.9.17/Python-3.9.17.tgz
tar -xf Python-3.9.17.tgz
cd Python-3.9.17
./configure --enable-optimizations --with-ensurepip=install
make -j4       # Use all cores
sudo make altinstall
python3.9 --version
```

- Create a virtual environment and activate it:

```bash
python3.9 -m venv venv39
source venv39/bin/activate
```

- **Tip:** Update the `start.sh` script to point to this virtual environment.

---

## 3. Install System Dependencies

Some Python packages (like `simpleaudio`) require system libraries:

```bash
sudo apt update
sudo apt install -y build-essential libasound2-dev libportaudio2 libportaudiocpp0 portaudio19-dev
```

---

## 4. Install Python Packages

### Step 1: Install requirements without dependencies

```bash
pip install --no-deps -r requirements.txt
```

### Step 2: Upgrade pip and build tools

```bash
pip install --upgrade pip setuptools wheel
```

### Step 3: Install requirements using the legacy resolver

```bash
pip install -r requirements.txt --use-deprecated=legacy-resolver
```

### Step 4: Install Rasa and Rasa SDK first

```bash
pip install "rasa==3.6.21" "rasa-sdk==3.6.2" --use-deprecated=legacy-resolver
```

> IMP : Rasa often throws dependency errors. Be ready to manually install missing packages.

### Step 5: Manually install additional packages if errors appear

```bash
pip install simpleaudio paho-mqtt aiohttp pluggy PyYAML piper porcupine
```

---

## 5. Environment File

- Create a `.env` file in the project root with your environment variables.  
- The project reads this file on startup.

---

## 6. SSH and Networking

- Find your Pi’s IP:

```bash
hostname -I
```

- SSH into the Pi:

```bash
ssh username@IP_address
```

- If you get warnings about host changes:

```bash
ssh-keygen -f "/home/your_path/.ssh/known_hosts" -R "192.168.1.17"
```

- Transfer files/folders:

```bash
# Single file
scp local_file username@IP_address:/remote/path

# Folder
scp -r local_folder username@IP_address:/remote/path
```

---

## 7. Project Folder Setup

- **TTS models:**  
  Create: `voice_assistant/app/modules/tts/models`  
  Place Piper TTS models + JSON files here.

- **Rasa models:**  
  Create: `voice_assistant/app/modules/intent/rasa_models`  
  Train your Rasa model (use `exp_files/rasa` folder for training) and put it here.

---

## 8. Running the Project

- Activate virtual environment:

```bash
source venv39/bin/activate
```

- Start the server:

```bash
python run_server.py
```

- Some packages may require `--no-cache-dir` if installation fails due to Pi’s limited memory.

---

## 9. Quick Tips

- Always activate your virtual environment before running scripts.  
- Expect a few dependency issues; patience and manual installs are normal.  
- Keep your `.env` file and model folders organized.  
- Update `start.sh` with your venv path to make startup seamless.

---

### Basic Setup
```bash
# Quick setup
./setup.sh

# Start server
./start.sh
```

### Switching Modules
```yaml
# config.yaml
tts: "tts.elevenlabs_tts.ElevenLabsTTS"
stt: "stt.vosk_stt.VoskSTT"
intent: "intent.rasa_intent.RasaIntent"
```
