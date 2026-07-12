"""
Improved AI Image Colorization Web App
Higher quality output using OpenCV DNN + Caffe model
"""

import os
import sys
import cv2
import numpy as np
import contextlib
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
import urllib.request
from io import StringIO

app = Flask(__name__)


@contextlib.contextmanager
def suppress_stderr():
    """Suppress OpenCV and other library warnings from reaching the client."""
    stderr = sys.stderr
    sys.stderr = StringIO()
    try:
        yield
    finally:
        sys.stderr = stderr


@contextlib.contextmanager
def suppress_stdout():
    """Suppress stdout during model operations."""
    stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        yield
    finally:
        sys.stdout = stdout

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"
MODEL_FOLDER = "model"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["RESULT_FOLDER"] = RESULT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
os.makedirs(MODEL_FOLDER, exist_ok=True)

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


@app.route("/upload", methods=["OPTIONS"])
def upload_options():
    return jsonify({}), 200

net = None
pts_in_hull = None


# ------------------------------------------------------------
# Utility
# ------------------------------------------------------------

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ------------------------------------------------------------
# Download Model
# ------------------------------------------------------------

def download_model_files():

    files = {
        "colorization_deploy_v2.prototxt": "https://raw.githubusercontent.com/richzhang/colorization/caffe/colorization/models/colorization_deploy_v2.prototxt",
        "colorization_release_v2.caffemodel": "https://storage.openvinotoolkit.org/repositories/datumaro/models/colorization/colorization_release_v2.caffemodel",
        "pts_in_hull.npy": "https://raw.githubusercontent.com/richzhang/colorization/caffe/colorization/resources/pts_in_hull.npy",
    }

    for name, url in files.items():
        path = os.path.join(MODEL_FOLDER, name)

        if not os.path.exists(path):
            print("Downloading:", name)
            # Use a custom user agent to avoid any potential block by servers
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(url, path)

    print("Model files ready.")


# ------------------------------------------------------------
# Load Model
# ------------------------------------------------------------

def load_model():

    global net, pts_in_hull

    download_model_files()

    proto = os.path.join(MODEL_FOLDER, "colorization_deploy_v2.prototxt")
    model = os.path.join(MODEL_FOLDER, "colorization_release_v2.caffemodel")
    pts = os.path.join(MODEL_FOLDER, "pts_in_hull.npy")

    with suppress_stdout(), suppress_stderr():
        net = cv2.dnn.readNetFromCaffe(proto, model)

        pts_in_hull = np.load(pts)
        pts_in_hull = pts_in_hull.transpose().reshape(2, 313, 1, 1)

        class8 = net.getLayerId("class8_ab")
        conv8 = net.getLayerId("conv8_313_rh")

        net.getLayer(class8).blobs = [pts_in_hull.astype(np.float32)]
        net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype=np.float32)]

    print("Colorization model loaded.")


# ------------------------------------------------------------
# Image Enhancement (NEW)
# ------------------------------------------------------------

def enhance_image(img):
    """
    Improve final image quality by boosting saturation and contrast.
    """
    img = img.astype(np.float32) / 255.0

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    s = np.clip(s * 1.35, 0, 1)
    v = np.clip(v * 1.05, 0, 1)
    hsv = cv2.merge([h, s, v])
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    img = np.clip(img * 255, 0, 255).astype(np.uint8)
    return img


# ------------------------------------------------------------
# Colorization Pipeline
# ------------------------------------------------------------

def colorize_image(path):

    global net

    with suppress_stdout(), suppress_stderr():
        img = cv2.imread(path, cv2.IMREAD_COLOR)

    if img is None:
        raise Exception("Image not readable")

    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif img.shape[2] == 4:
        img = img[:, :, :3]

    original_h, original_w = img.shape[:2]

    scaled = img.astype("float32") / 255.0
    lab = cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB)

    L_orig = lab[:, :, 0]

    if max(original_h, original_w) <= 224:
        net_size = 224
    elif max(original_h, original_w) <= 448:
        net_size = 448
    elif max(original_h, original_w) <= 672:
        net_size = 672
    else:
        net_size = 448

    L_resized = cv2.resize(L_orig, (net_size, net_size))
    L_resized -= 50

    blob = cv2.dnn.blobFromImage(
        L_resized,
        scalefactor=1.0,
        size=(net_size, net_size),
        mean=(0, 0, 0),
        swapRB=False,
        crop=False
    )

    with suppress_stdout(), suppress_stderr():
        net.setInput(blob)
        ab = net.forward()[0, :, :, :].transpose((1, 2, 0))

    ab = cv2.resize(ab, (original_w, original_h), interpolation=cv2.INTER_CUBIC)

    colorized = np.concatenate((L_orig[:, :, np.newaxis], ab), axis=2)

    with suppress_stdout(), suppress_stderr():
        colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
    colorized = np.clip(colorized, 0, 1)
    colorized = (255 * colorized).astype("uint8")

    colorized = enhance_image(colorized)

    return colorized


# ------------------------------------------------------------
# Flask Routes
# ------------------------------------------------------------

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"})

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"})

    if file and allowed_file(file.filename):

        import uuid
        # Secure the filename
        original_secure = secure_filename(file.filename)
        base_name, ext = os.path.splitext(original_secure)
        
        # If secure_filename returns empty (e.g. for non-ASCII characters)
        if not base_name:
            base_name = "upload"
            ext = "." + file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else ".jpg"
            
        # Append a short UUID to guarantee uniqueness
        filename = f"{base_name}_{uuid.uuid4().hex[:8]}{ext}"

        upload_path = os.path.join(UPLOAD_FOLDER, filename)

        file.save(upload_path)

        try:
            with suppress_stdout(), suppress_stderr():
                output = colorize_image(upload_path)

            result_name = "colorized_" + base_name + ".jpg"
            result_path = os.path.join(RESULT_FOLDER, result_name)

            cv2.imwrite(result_path, output)

            return jsonify({
                "success": True,
                "original": f"/uploads/{filename}",
                "colorized": f"/results/{result_name}"
            })

        except Exception as e:
            error_msg = str(e)
            if "model" in error_msg.lower() or "unsupported" in error_msg.lower() or "cannot read" in error_msg.lower():
                error_msg = "The image format is not supported by the model. Please try a standard JPG or PNG image."
            return jsonify({"error": error_msg})

    return jsonify({"error": "Invalid file type"})


@app.route("/uploads/<filename>")
def get_upload(filename):
    response = send_file(os.path.join(UPLOAD_FOLDER, filename))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response


@app.route("/results/<filename>")
def get_result(filename):
    response = send_file(os.path.join(RESULT_FOLDER, filename))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response


@app.route("/download/<filename>")
def download(filename):

    return send_file(
        os.path.join(RESULT_FOLDER, filename),
        as_attachment=True
    )


# ------------------------------------------------------------
# Run
# ------------------------------------------------------------

if __name__ == "__main__":

    print("Loading model...")
    load_model()

    app.run(debug=True, host='0.0.0.0', port=5000)
