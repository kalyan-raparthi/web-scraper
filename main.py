from flask import Flask, request, jsonify
import requests
from PIL import Image
from io import BytesIO
from paddleocr import PaddleOCR

app = Flask(__name__)

# Initialize PaddleOCR globally
ocr = PaddleOCR(use_angle_cls=True, lang='en')

@app.route('/extract-image-text', methods=['GET'])
def extract_text_from_image_url():
    image_url = request.args.get('url')
    if not image_url:
        return jsonify({"error": "Please provide an image URL using ?url= parameter"}), 400

    try:
        # Download image from URL
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()

        # Open image using PIL
        img = Image.open(BytesIO(response.content)).convert('RGB')

        # OCR using PaddleOCR
        result = ocr.ocr(img, cls=True)

        extracted_text = []
        for line in result[0]:
            extracted_text.append(line[1][0])  # Extract text part only

        return jsonify({
            "image_url": image_url,
            "extracted_text": "\n".join(extracted_text)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
