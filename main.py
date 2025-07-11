from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO
from paddleocr import PaddleOCR

app = Flask(__name__)

# Initialize PaddleOCR once (do this globally to avoid reloading every time)
ocr = PaddleOCR(use_angle_cls=True, lang='en')  # You can add more languages if needed

@app.route('/extract-texts', methods=['GET'])
def extract_texts_from_all_images():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Please provide a URL using ?url= parameter"}), 400

    try:
        # Get webpage content
        page_response = requests.get(url, timeout=10)
        page_response.raise_for_status()
        soup = BeautifulSoup(page_response.text, 'html.parser')

        # Find all image URLs
        image_tags = soup.find_all('img')
        results = []

        for img_tag in image_tags:
            img_src = img_tag.get('src')
            if img_src:
                full_img_url = urljoin(url, img_src)

                try:
                    # Download image
                    img_response = requests.get(full_img_url, timeout=10)
                    img_response.raise_for_status()

                    # Read image into PIL
                    img = Image.open(BytesIO(img_response.content)).convert('RGB')

                    # Save to memory for PaddleOCR (needs file path or numpy array)
                    img_array = img

                    # OCR using PaddleOCR
                    result = ocr.ocr(img_array, cls=True)
                    extracted_text = []

                    for line in result[0]:
                        extracted_text.append(line[1][0])  # line[1][0] contains the recognized text

                    full_text = "\n".join(extracted_text)

                    results.append({
                        "image_url": full_img_url,
                        "extracted_text": full_text
                    })

                except Exception as img_error:
                    results.append({
                        "image_url": full_img_url,
                        "error": str(img_error)
                    })

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

