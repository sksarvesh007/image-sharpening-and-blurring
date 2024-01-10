import gunicorn
from flask import Flask, render_template, request, send_file
import cv2
import numpy as np
from io import BytesIO

app = Flask(__name__)

def blur_image(image):
    blurred = cv2.GaussianBlur(image, (25, 25), 0)
    return blurred

def sharpen_image(image):
    gaussian_blur = cv2.GaussianBlur(image, (25, 25), 0)
    sharpened = cv2.addWeighted(image, 1.5, gaussian_blur, -0.5, 0)
    return sharpened

def water_art(image):
    img_cleared = cv2.medianBlur(image, 5)
    img_cleared=cv2.medianBlur(img_cleared, 5)
    img_cleared=cv2.medianBlur(img_cleared, 5)
    
    img_cleared = cv2.edgePreservingFilter(img_cleared, flags=2, sigma_s=50, sigma_r=0.4)
    
    img_filtered = cv2.bilateralFilter(img_cleared, 3, 10, 5)
    for i in range(2):
        img_filtered = cv2.bilateralFilter(img_filtered, 3, 10, 5)
        
    for i in range(3):
        img_filtered = cv2.bilateralFilter(img_filtered, 5 , 30 , 10)
        
    gaussian_mask = cv2.GaussianBlur(img_filtered, (7,7), 2)
    image_sharp = cv2.addWeighted(img_filtered, 1.5, gaussian_mask, -0.5, 0)
    image_sharp = cv2.addWeighted(image_sharp, 1.4, gaussian_mask, -0.2, 0)
    return image_sharp

def process_image(image, operation):
    if operation == 'blur':
        return blur_image(image)
    elif operation == 'sharpen':
        return sharpen_image(image)
    elif operation == 'water':
        return water_art(image)
    else:
        return image
    

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['image']
        image = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_COLOR)
        operation = request.form.get('operation')
        processed_image = process_image(image, operation)
        _, buffer = cv2.imencode('.png', processed_image)
        buffer = BytesIO(buffer)

        return send_file(buffer, mimetype='image/png', as_attachment=True, download_name='processed_image.png')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
