# 🐍 How to Install Python 3.11.9

This guide explains how to install **Python 3.11.9** on **Windows**, **macOS**, and **Linux** systems.

---

## 🪟 Windows Installation

### Step 1: Download

Go to the official Python release page:
👉 [https://www.python.org/downloads/release/python-3119/](https://www.python.org/downloads/release/python-3119/)

### Step 2: Choose Installer

Download the **Windows installer (64-bit)** — usually named `python-3.11.9-amd64.exe`.

### Step 3: Run Installer

1. Double-click the installer.
2. ✅ Check **"Add Python to PATH"** at the bottom.
3. Click **Install Now**.

### Step 4: Verify Installation

Open **Command Prompt (cmd)** and run:

```bash
python --version
```

If successful, you’ll see:

```
Python 3.11.9
```

---

## 🍎 macOS Installation

### Step 1: Download

Go to:
👉 [https://www.python.org/downloads/release/python-3119/](https://www.python.org/downloads/release/python-3119/)

### Step 2: Choose Installer

Download the **macOS 64-bit universal2 installer** (for both Intel and Apple Silicon Macs).

### Step 3: Run Installer

1. Open the downloaded `.pkg` file.
2. Follow the installation prompts.

### Step 4: Verify Installation

Open **Terminal** and run:

```bash
python3 --version
```

Expected output:

```
Python 3.11.9
```

---

## 🐧 Linux Installation

### Option 1: Using Package Manager

For **Ubuntu / Debian-based systems**:

```bash
sudo apt update
sudo apt install python3.11 -y
```

For **Fedora / CentOS / RHEL**:

```bash
sudo dnf install python3.11 -y
```

For **Arch / Manjaro**:

```bash
sudo pacman -S python
```

### Option 2: Building from Source

If your package manager doesn’t have Python 3.11.9 yet:

```bash
sudo apt update
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev curl -y
curl -O https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz
tar -xf Python-3.11.9.tgz
cd Python-3.11.9
./configure --enable-optimizations
make -j$(nproc)
sudo make altinstall
```

### Step 3: Verify Installation

```bash
python3.11 --version
```

Should return:

```
Python 3.11.9
```

---

✅ **Done!** You now have Python 3.11.9 installed on your system.

To confirm `pip` is installed, run:

```bash
pip --version
```

If not, install it with:

```bash
python -m ensurepip --upgrade
```

---

### 💡 Tip

To upgrade all installed packages later:

```bash
python -m pip install --upgrade pip setuptools wheel
```

---

**Created by:** Jeff (Bubbles) — FNBubbles420 Org 💚
