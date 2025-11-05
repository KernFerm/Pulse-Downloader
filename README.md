


# 🎬 Professional Video Downloader

**Version: 0.0.23UdL36**

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Downloads](https://img.shields.io/github/downloads/KernFerm/video-downloader/total.svg)](https://github.com/KernFerm/video-downloader)
[![Security](https://img.shields.io/badge/security-verified-important.svg)](SECURITY.md)

<p align="center">
	<img src="https://github.com/KernFerm/video-downloader/blob/main/icons/video_downloader_main.png" alt="Video Downloader" width="320" />
</p>

<p align="center">
	<b>Fast, secure, and user-friendly video downloader for direct links and streaming sites.</b><br>
	<i>Download with resume, progress bar, and a beautiful GUI. Powered by <a href="https://github.com/yt-dlp/yt-dlp">yt-dlp</a> for advanced sites.</i>
</p>

---

## 🚀 Features


✅ <b>Direct file download</b> with resume (HTTP Range header)<br>
✅ <b>Automatic fallback to yt-dlp</b> for streaming/video sites (if installed)<br>
✅ <b>Progress bar</b> for direct downloads (tqdm)<br>
✅ <b>Safe filenames and paths</b> (sanitization for security)<br>
✅ <b>Informative logging</b> for download status and errors<br>
✅ <b>Threaded downloads in GUI</b> (non-blocking UI)<br>
✅ <b>Error handling</b> with status messages in GUI and CLI<br>
✅ <b>System tray support</b> (minimize, restore, exit from tray menu, Windows only)<br>
✅ <b>Filename extraction</b> and sanitization from URLs<br>
✅ <b>Resume support</b> for interrupted downloads<br>
✅ <b>Content-Length/Range handling</b> for partial downloads and progress calculation<br>
✅ <b>Modern PyQt5 GUI</b> with custom fonts, colors, and styled buttons<br>
✅ <b>Input validation</b> for URLs and output folders in both CLI and GUI<br>
✅ <b>Multiple download methods</b>: direct first, yt-dlp fallback<br>
✅ <b>Custom download location</b>: browse and select output folder in GUI<br>
✅ <b>Exit button</b> for clean GUI exit<br>
✅ <b>Copyright reminder</b> in both CLI and GUI<br>
✅ <b>CLI support</b> (no GUI required)
✅ <b>Custom output directory</b> for downloads (via -o or GUI)
✅ <b>No GUI option</b> for automation (--no-gui)
✅ <b>Auto fallback and no prompt</b> options (--auto-fallback, --no-prompt)
✅ <b>Cross-platform</b> (Windows, macOS, Linux)
✅ <b>Security</b>: All user inputs sanitized to prevent path traversal and injection attacks

---


## 📦 Requirements

- Python 3.11+
- [requests](https://pypi.org/project/requests/)
- [tqdm](https://pypi.org/project/tqdm/)
- [PyQt5](https://pypi.org/project/PyQt5/) (for GUI)
- [yt-dlp](https://pypi.org/project/yt-dlp/) (optional, for fallback)

<details>
<summary><b>Install dependencies</b></summary>

```bash
pip install -r requirements.txt
```
</details>

---


---

## 🖥️ Usage



### 💻 Command Line

Download a video directly:
```bash
python video_downloader.py <url> [-o OUT_DIR]
```

Options:
- `--no-gui` : Run in CLI mode only (no GUI)
- `--auto-fallback` : Automatically use yt-dlp if direct download fails
- `--no-prompt` : Do not prompt for yt-dlp fallback (for automation)

Example output (CLI):
```
[2025-11-04 12:34:56] INFO: Detected direct media file URL. Downloading to: myvideo.mp4
[2025-11-04 12:34:56] INFO: Download complete: myvideo.mp4
```

### 🪟 Graphical Interface

Launch the GUI:
```bash
python video_downloader.py
```

Features:
- Enter video URL and output folder
- Progress bar and status messages
- System tray support (Windows)
- Exit and browse buttons

Example screenshot (GUI):
<p align="center">
	<img src="https://github.com/KernFerm/video-downloader/blob/main/icons/video_downloader_main.png" alt="Video Downloader GUI" width="320" />
</p>

---


---

## 🔒 Security

- All user inputs are sanitized to prevent injection and path traversal attacks.
- Only download content you have permission to access.
- Filenames and output paths are validated and sanitized.

---


---

## ❓ FAQ

**Q: Why does my download fail?**
A: The URL may be invalid, the server may not support direct downloads, or you may not have permission. Try using yt-dlp fallback.

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

- **yt-dlp not found:** Install with `pip install yt-dlp` and ensure it's on your PATH.
- **PyQt5 errors:** Install with `pip install PyQt5`.
- **Permission errors:** Make sure you have write access to the output folder.
- **Network issues:** Check your internet connection and URL validity.
- **Resume not working:** Not all servers support HTTP Range requests.

---

## 🤝 Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements, bug fixes, or new features.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for full terms, global disclaimers, indemnification, jurisdiction, and educational use restrictions.

**Key points:**
- You may use, modify, and distribute this software under the MIT License.
- The developer is not liable for any damages or misuse.
- You must comply with all applicable laws and copyright regulations.
- Use is permitted for educational and non-commercial purposes; see LICENSE for details.
- The LICENSE file includes global disclaimers, indemnification clauses, and jurisdiction information for legal protection.

---

## ⚠️ Disclaimer


> **WARNING:** Only download content you have permission to download. Respect copyright and site Terms of Service.




