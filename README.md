# AI-Based Image Colorization

## Overview

AI-Based Image Colorization is a deep learning project that automatically converts grayscale (black-and-white) images into realistic color images. The project uses a pre-trained Convolutional Neural Network (CNN) model through OpenCV's Deep Neural Network (DNN) module to predict the missing color information in an image.

The model has been trained on a large dataset of color images, allowing it to generate natural-looking colors without any manual editing.

---

## Features

- Automatically colorizes grayscale images.
- Uses a pre-trained deep learning model.
- Generates realistic and visually appealing results.
- Supports common image formats such as JPG, JPEG, and PNG.
- Simple implementation using Python and OpenCV.

---

## Technologies Used

- Python
- OpenCV
- NumPy
- Deep Learning (CNN)
- Caffe Pre-trained Model

---

## Project Workflow

1. The user provides a grayscale image as input.
2. The image is loaded using OpenCV.
3. The pre-trained AI colorization model is loaded.
4. The input image is converted to the LAB color space.
5. The L (Lightness) channel is extracted and passed to the neural network.
6. The model predicts the A and B color channels.
7. The predicted channels are combined with the original L channel.
8. The LAB image is converted back to RGB.
9. The final colorized image is displayed and saved.

---

## Project Structure

```
AI-Image-Colorization/
│
├── model.py
├── colorization_release_v2.caffemodel
├── colorization_deploy_v2.prototxt
├── pts_in_hull.npy
├── images/
│   ├── input.jpg
│   └── output.jpg
├── README.md
└── requirements.txt
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/AI-Image-Colorization.git
```

Move to the project directory:

```bash
cd AI-Image-Colorization
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

Run the project using:

```bash
python model.py
```

After execution, the colorized image will be generated and saved automatically.

---

## Input

- Grayscale Image (.jpg, .jpeg, .png)

## Output

- AI Colorized Image

---

## Future Enhancements

- Video colorization
- Real-time webcam colorization
- High-resolution image support
- Web application using Streamlit
- GPU acceleration for faster processing

---

## Applications

- Restoring old photographs
- Historical image restoration
- Photo editing
- Computer Vision research
- Digital media enhancement

---

## Author

**Vedant Niture**

GitHub: https://github.com/your-username

---

## License

This project is intended for educational and learning purposes.
- These folders are ignored by git and recommended to ignore manually as well

## Author

**Evedant Nitur**
