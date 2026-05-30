# Media Library Video Downloader

A Flask + yt-dlp web app with a Poppins UI, Font Awesome icons, live download progress, downloaded-video list, and ZIP export.

## Setup

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open: http://127.0.0.1:5000

## Notes

- Put your URLs in `course_urls` inside `app.py`.
- Downloaded files are saved in the `downloads/` folder.
- Click **Download ZIP** after videos have been downloaded.
- Install FFmpeg if merged MP4 output fails: https://ffmpeg.org/download.html
- Only download videos you own or have permission to save. This app does not bypass DRM or access controls.
