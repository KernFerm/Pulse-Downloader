
# 🎬 PulseDownloader

**Version: 0.0.23UdL36**

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Security](https://img.shields.io/badge/security-verified-important.svg)](SECURITY.md)

<p align="center">
	<img src="https://user-images.githubusercontent.com/76848676/236683021-2e7e7e7e-7e7e-4e7e-8e7e-7e7e7e7e7e7e.gif" alt="PulseDownloader" width="320" />
</p>

<p align="center">
	<b>Fast, secure, and user-friendly video/audio downloader for direct links and streaming platforms.</b><br>
	<i>PulseDownloader always uses <a href="https://github.com/yt-dlp/yt-dlp">yt-dlp</a> for supported platforms, and direct download for media files.</i>
</p>

---

## 🚀 Features

- ✅ **Always uses yt-dlp for supported platforms** (YouTube, Vimeo, SoundCloud, etc.)
- ✅ **Direct download for direct media file links** (MP4, MP3, etc.)
- ✅ **Automatic detection of platform type**
- ✅ **Dedicated folders for video and music downloads**
- ✅ **Progress bar for direct downloads** (tqdm)
- ✅ **Safe filenames and paths** (sanitization for security)
- ✅ **Informative logging for download status and errors**
- ✅ **Threaded downloads in GUI** (non-blocking UI)
- ✅ **Error handling with status messages in GUI and CLI**
- ✅ **System tray support** (Windows only)
- ✅ **Filename extraction and sanitization from URLs**
- ✅ **Resume support for interrupted downloads**
- ✅ **Content-Length/Range handling for partial downloads and progress calculation**
- ✅ **Modern PyQt5 GUI** with custom fonts, colors, and styled buttons
- ✅ **Input validation for URLs and output folders in both CLI and GUI**
- ✅ **Custom download location:** browse and select output folder in GUI
- ✅ **Exit button for clean GUI exit**
- ✅ **Copyright reminder in both CLI and GUI**
- ✅ **CLI support** (no GUI required)
- ✅ **Custom output directory for downloads** (via -o or GUI)
- ✅ **No GUI option for automation** (--no-gui)
- ✅ **Auto fallback and no prompt options** (--auto-fallback, --no-prompt)
- ✅ **Cross-platform** (Windows, macOS, Linux)
- ✅ **Security:** All user inputs sanitized to prevent path traversal and injection attacks

---

## 📦 Requirements

- Python 3.11+
- requests
- tqdm
- PyQt5 (for GUI)
- yt-dlp (required for platform support)

```bash
pip install -r requirements.txt
```

---

## 🖥️ Usage

### Command Line

Download from a supported platform or direct media file:
```bash
python Pulse_Downloader.py <url> [-o OUT_DIR]
```

Options:
- `--no-gui` : Run in CLI mode only (no GUI)
- `--auto-fallback` : Automatically use yt-dlp for supported platforms
- `--no-prompt` : Do not prompt for yt-dlp fallback (for automation)

Example output (CLI):
```
[2025-11-04 12:34:56] INFO: Detected YouTube link. Downloading with yt-dlp to: video.mp4
[2025-11-04 12:34:56] INFO: Download complete: video.mp4
```

### Graphical Interface

Launch the GUI:
```bash
python Pulse_Downloader.py
```

Features:
- Enter video/audio URL and output folder
- Progress bar and status messages
- System tray support (Windows)
- Exit and browse buttons

---

## 🔒 Security

- All user inputs are sanitized to prevent injection and path traversal attacks.
- Only download content you have permission to access.
- Filenames and output paths are validated and sanitized.

---

## ❓ FAQ

**Q: Why does my download fail?**
A: The URL may be invalid, the platform may not be supported, or you may not have permission. Check the SUPPORTED_PLATFORMS.md for current platform support.

**Q: How do I resume a download?**
A: If the file already exists, the downloader will attempt to resume using HTTP Range headers (if supported by the server).

**Q: How do I install yt-dlp?**
A: Run `pip install yt-dlp` in your terminal.

**Q: The GUI won't start!**
A: Make sure you have PyQt5 installed: `pip install PyQt5`.

**Q: Can I use this on macOS or Linux?**
A: Yes, but system tray features are Windows-only.

---

## 🛠️ Troubleshooting

- yt-dlp not found: Install with `pip install yt-dlp` and ensure it's on your PATH.
- PyQt5 errors: Install with `pip install PyQt5`.
- Permission errors: Make sure you have write access to the output folder.
- Network issues: Check your internet connection and URL validity.
- Resume not working: Not all servers support HTTP Range requests.

---

## 🤝 Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements, bug fixes, or new features.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for full terms, global disclaimers, indemnification, jurisdiction, and educational use restrictions.

**Key points:**
- You may use, modify, and distribute PulseDownloader under the MIT License.
- The developer is not liable for any damages or misuse.
- You must comply with all applicable laws and copyright regulations.
- Use is permitted for educational and non-commercial purposes; see LICENSE for details.
- The LICENSE file includes global disclaimers, indemnification clauses, and jurisdiction information for legal protection.

---

## ⚠️ Disclaimer

> **WARNING:** Only download content you have permission to download. Respect copyright and site Terms of Service.

