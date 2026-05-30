from flask import Flask, jsonify, render_template, send_file
import yt_dlp
import threading
import os
import re
import zipfile
import time
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_FOLDER = BASE_DIR / "downloads"
ZIP_FOLDER = BASE_DIR / "zips"
DOWNLOAD_FOLDER.mkdir(exist_ok=True)
ZIP_FOLDER.mkdir(exist_ok=True)

# Add/remove your course URLs here.
course_urls = [
    "https://iframe.mediadelivery.net/embed/120349/912419c9-1708-4ccc-9374-c2fb7db5f41f?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/6edd7e24-53e3-4f36-b313-ebed51b03320?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/a86c5479-121e-4a28-ab13-f4289a1d8138?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/0adf5835-c3b2-4555-8f5c-266c97acb613?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/d10ad843-46e8-4eed-a3ff-b46334c6f3d3?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/4a922d1b-8f0c-40e9-b322-ecd6c87bc17e?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/2af58874-a612-477a-8908-2899de267b5b?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/ab630fab-3bfa-488d-a76f-988a8b6ed2f0?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/6a2b5f34-41fc-48b8-be2f-22b3d06ce7d9?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/2942a7e8-572a-4355-9736-3ecffda77851?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/3bd22ed7-47c0-458f-bc7f-e46b651a2163?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/5ec80b1e-2113-417d-a7c3-a558c1dc751c?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/df242853-63e1-4e06-8304-b94e4d404305?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/08bb0150-d187-430f-97c9-6caa9d41d735?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/bfc45b90-745b-49aa-b903-90faca2714e8?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/63bac239-7bd0-4bfb-8394-25ee4927f382?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/7abf0120-c22f-48e2-8161-63a6d646fd55?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/94bcb9aa-33a4-4115-9548-fc48019eb899?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/4343a057-a87d-4cad-ad7c-3caac57046b0?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/f84f70db-195b-4921-bad3-cd66e2ca0248?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/82f70a85-bc02-48bb-879a-09a844c2ad29?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/b48bb638-0d5e-4d7a-9960-17229e9e6a66?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://player.mediadelivery.net/embed/120349/5013003e-e055-4ae7-bd2c-cddf8b16afa6?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://player.mediadelivery.net/embed/120349/c0bc179e-b230-4647-9f46-89d6586138e8?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/29e1c317-a28b-4b6e-bc7b-bd03205fbbb4?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/9eddc01b-9fe3-40bd-bcb9-d7061b4258e8?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/9862372f-8184-4a9f-927b-5bfbdec24c3a?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/cb82e66f-c1c7-409e-9a55-2bc0277d418b?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/bff6e951-a2b4-4f7d-a82a-2799c759bb9f?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/64bb362b-953b-42c1-bb27-7d878add355e?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/eed4c07f-ceff-47f9-bf99-2c072526f6a6?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/f476877e-23d4-43b6-9cc6-aca167fb56c3?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/52c7d1db-ffe1-4301-99ec-1d954344f7ac?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/eccc0e5e-2ec7-4b92-9efe-ebf6a882de84?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/1e8d024a-92f9-458c-88a2-e3caf4b8470b?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/002b0146-277b-4eb5-a7f3-0b1a8ae2d0cd?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/c8dcfe17-e57f-4387-894a-a4c8543081f4?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/cd26a6a7-7aa7-4258-996c-dd5830eb6ffc?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/5ccfe342-a491-4057-96f9-b2c44c1a3669?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/c217d9f2-c011-41c9-ad9f-674adbd031e8?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/8a4dce1a-3c86-47b2-859d-30d857190434?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/5bf0b940-b458-4a07-b6c4-6176286ab151?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/88c70297-4339-4aad-bdab-ae68c27e78d6?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/c8e2c003-23b7-4aa1-b18d-b02c396e210e?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/b656bdba-9cfa-4d46-bb58-6755a8d129e9?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/62992ba6-6e84-41c3-85e4-66fd6b4226ac?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/1d556941-dcc8-4727-88b4-c2b148728cb6?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/587d30fe-c86a-4a9b-b508-d382670c0154?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/192a43c7-d276-4852-9406-9fba7fa0511b?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/0d69b370-8532-4d1b-b1dd-5ddbb0f96f7d?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://player.mediadelivery.net/embed/120349/dbb46ee7-3bca-4894-99c0-d315674dfcb8?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/92516f2d-6a15-457e-b0f5-0fb5bd516fbd?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/640a25a7-6acb-4c85-ba4a-6e685c97558a?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/45f8d1bb-e616-4609-8fd5-25bfa4caa296?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/e260659c-ef35-4961-ba82-9f7451c577b3?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/69303c08-97f3-4bda-9572-2c864ce6e534?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/42d82a30-eb93-4312-8c40-456ea2cc4cb7?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/3fc4f2e7-1943-4448-8feb-b6ca8057c4ba?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/b04ea7fc-9d26-4521-b0e8-77a6195275b0?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/261e1631-6c51-4fbf-a419-27df63a5dcff?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/1fdf2bab-f58e-4d73-9250-851115c6db11?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/b497094a-ee7e-4cfb-a33a-3cb28212e620?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/91afdb45-4256-4a52-9f32-dfa60ab9d22e?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/81caf3aa-8333-485c-9d7c-88a4165c2670?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/5ef97122-da99-4efe-ab48-9663bd95865d?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/8ca90308-392e-435e-9650-57ff8541735d?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/e603892c-15f7-455b-9bcb-d7c0bd56197d?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/816cb1ed-53eb-45fd-8b6c-ffef47d14967?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/d5881360-ce43-4f96-8869-2111ce0794ef?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/9f07650c-574b-4bc2-b2f8-1dd24777a311?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/841f12b6-2368-4b52-9b7e-0d6df40a6364?autoplay=false&preload=true",
    "https://www.youtube.com/embed/z9eAiGF2Rx8",
    "https://iframe.mediadelivery.net/embed/120349/0a768925-b79d-4b8a-8481-b45148ae59a0?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/30cd0119-7e56-49a4-a917-136ca44be5a5?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/25cdc580-6658-4d73-8f3f-1e61de01c4eb?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/eb34fb69-b58b-49d9-99d8-257b60ba6f18?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/f6ec3b20-838d-47e7-9b26-569463b7f687?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/0aca34a1-2168-460a-9dca-852800ea76d7?autoplay=false&preload=true",
    "https://www.youtube-nocookie.com/embed/hOL8p6KDwM8",
    "https://player.mediadelivery.net/embed/120349/47333431-9422-4586-b748-c44da910e0b6?autoplay=false&loop=false&muted=false&preload=true&responsive=true",
    "https://iframe.mediadelivery.net/embed/120349/83b0bd49-4f71-401e-aebc-54b94d8ee90e?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/f97c1d86-1d12-4da6-8140-df57843342bb?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/49f026b9-6118-45b7-84b3-54ee35a0ab93?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/263ffb1d-5231-4055-a2f2-f15f102be0e6?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/f3fa4d2f-4ce0-4bb6-8a91-4c56b198df02?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/cc34e3b3-6d28-474f-a10c-cfbf4b929d4b?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/1e0fecf7-6a78-433a-84e7-fd9202e230f9?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/e9335619-acb9-47f2-9e7a-25b5a097556a?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/6481057f-815e-484f-bdda-5bdbce7db64a?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/5f9ab25d-a50c-4868-801a-3eff17e9f8f6?autoplay=false&preload=true",
    "https://iframe.mediadelivery.net/embed/120349/a6849875-d668-41e5-96b6-a69700e0ceff?autoplay=false&preload=true",
]

progress = {
    "status": "idle",
    "current": "",
    "percent": 0.0,
    "speed": "0",
    "eta": "0",
    "done": 0,
    "total": 0,
    "completed": [],
    "failed": [],
    "message": "Ready to download",
}

progress_lock = threading.Lock()
ansi_re = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
non_numeric_re = re.compile(r"[^0-9.]")

def clean_text(value, default=""):
    if value is None:
        return default
    text = ansi_re.sub("", str(value)).strip()
    return text or default

def clean_percent(value):
    text = non_numeric_re.sub("", clean_text(value, "0"))
    try:
        return float(text)
    except Exception:
        return 0.0

def reset_progress():
    with progress_lock:
        progress.update({
            "status": "idle",
            "current": "",
            "percent": 0.0,
            "speed": "0",
            "eta": "0",
            "done": 0,
            "total": 0,
            "completed": [],
            "failed": [],
            "message": "Ready to download",
        })

def normalize_url(url: str) -> str:
    """Convert common embed URLs to URLs yt-dlp can usually understand."""
    url = url.strip()
    youtube_match = re.search(r"(?:youtube(?:-nocookie)?\.com/embed/)([A-Za-z0-9_-]+)", url)
    if youtube_match:
        return f"https://www.youtube.com/watch?v={youtube_match.group(1)}"
    return url

def list_downloaded_files():
    files = []
    for path in DOWNLOAD_FOLDER.glob("*"):
        if path.is_file():
            files.append({
                "name": path.name,
                "size": round(path.stat().st_size / (1024 * 1024), 2),
                "modified": int(path.stat().st_mtime),
            })
    return sorted(files, key=lambda item: item["modified"], reverse=True)

def download():
    reset_progress()
    urls = [normalize_url(url) for url in course_urls if url.strip()]

    with progress_lock:
        progress["status"] = "downloading"
        progress["total"] = len(urls)
        progress["message"] = "Downloading started"

    def hook(d):
        status = d.get("status")

        if status == "downloading":
            downloaded = d.get("downloaded_bytes", 0) or 0
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            percent = (downloaded / total * 100.0) if total else clean_percent(d.get("_percent_str", "0%"))
            percent = max(0.0, min(100.0, percent))

            with progress_lock:
                progress["percent"] = percent
                progress["current"] = clean_text(d.get("filename", progress["current"]))
                progress["speed"] = clean_text(d.get("_speed_str", "0"), "0")
                progress["eta"] = clean_text(d.get("_eta_str", "0"), "0")
                progress["message"] = "Downloading video"

        elif status == "finished":
            filename = clean_text(d.get("filename", ""))
            with progress_lock:
                progress["percent"] = 100.0
                progress["done"] += 1
                if filename:
                    progress["completed"].append(filename)
                progress["speed"] = "0"
                progress["eta"] = "0"
                progress["message"] = "Video downloaded, processing next"

    ydl_opts = {
        "outtmpl": str(DOWNLOAD_FOLDER / "%(playlist_index|00)s-%(title).180B.%(ext)s"),
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "progress_hooks": [hook],
        "noprogress": True,
        "quiet": True,
        "ignoreerrors": True,
        "continuedl": True,
        "retries": 5,
        "fragment_retries": 5,
        "windowsfilenames": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for index, url in enumerate(urls, start=1):
            try:
                with progress_lock:
                    progress["percent"] = 0.0
                    progress["current"] = f"{index}/{len(urls)} - {url}"
                    progress["speed"] = "0"
                    progress["eta"] = "0"
                    progress["message"] = "Preparing video"
                ydl.download([url])
            except Exception as exc:
                with progress_lock:
                    progress["failed"].append({"url": url, "error": str(exc)})
                    progress["message"] = "Some videos failed"

    with progress_lock:
        progress["status"] = "completed"
        progress["percent"] = 100.0 if progress["total"] and progress["done"] == progress["total"] else progress["percent"]
        progress["speed"] = "0"
        progress["eta"] = "0"
        progress["message"] = "All available downloads finished"

@app.route("/")
def home():
    return render_template("index.html", total_urls=len(course_urls))

@app.route("/start", methods=["POST", "GET"])
def start():
    with progress_lock:
        if progress["status"] == "downloading":
            return jsonify({"ok": False, "message": "Download already running"}), 409
    threading.Thread(target=download, daemon=True).start()
    return jsonify({"ok": True, "message": "Download started"})

@app.route("/progress")
def get_progress():
    with progress_lock:
        data = progress.copy()
    data["downloaded_files"] = list_downloaded_files()
    return jsonify(data)

@app.route("/files")
def files():
    return jsonify({"files": list_downloaded_files()})

@app.route("/zip")
def download_zip():
    files = [path for path in DOWNLOAD_FOLDER.glob("*") if path.is_file()]
    if not files:
        return jsonify({"ok": False, "message": "No downloaded videos found yet"}), 404

    zip_path = ZIP_FOLDER / f"downloaded_videos_{int(time.time())}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files:
            zipf.write(file_path, arcname=file_path.name)

    return send_file(zip_path, as_attachment=True, download_name="downloaded_videos.zip")

if __name__ == "__main__":
    app.run(debug=True)
