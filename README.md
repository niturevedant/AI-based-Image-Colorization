# AI-Based Image Colorization

Transform black and white images into vibrant colored images using deep learning and OpenCV.

## Features

- Upload grayscale or color images
- Real AI-based colorization using OpenCV DNN and the Caffe colorization model
- Preview images before processing
- Download colorized results
- Works on desktop and mobile (same WiFi)
- Demo mode available when Flask backend is not running

## How to Run

### 1. Install Dependencies

```bash
pip install -r AI-Colorization/requirements.txt
```

### 2. Start the Flask Backend

```bash
python AI-Colorization/app.py
```

The server starts at:
- `http://127.0.0.1:5000` on your computer
- `http://<your-local-ip>:5000` on other devices on the same WiFi

### 3. Open in Browser

Go to `http://127.0.0.1:5000/` to use the full AI version.

### Demo Mode

If you just open `index.html` directly or use VS Code Live Server, the app works in **Demo Mode** using client-side simulation — no backend required.

## Tech Stack

- **Backend:** Flask (Python)
- **AI Model:** OpenCV DNN with Caffe colorization model
- **Frontend:** HTML, CSS, JavaScript
- **Processing:** OpenCV, NumPy

## Project Structure

- `index.html` — Unified frontend (works with Flask and Live Server)
- `script.js` — Frontend logic with backend detection
- `style.css` — Styling
- `AI-Colorization/app.py` — Flask backend
- `AI-Colorization/requirements.txt` — Python dependencies
- `AI-Colorization/templates/index.html` — Flask template
- `AI-Colorization/static/` — CSS and JS served by Flask

## Notes

- The AI model (~123 MB) is downloaded automatically on first run and stored in `AI-Colorization/model/`
- Uploaded images and results are stored temporarily in `uploads/` and `results/`
- These folders are ignored by git and recommended to ignore manually as well

## Author

**Evedant Nitur**
