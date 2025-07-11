from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO
import pytesseract

app = Flask(__name__)

@app.route('/extract-texts', methods=['GET'])
def extract_texts_from_all_images():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Please provide a URL using ?url= parameter"}), 400

    try:
        # Get webpage content
        page_response = requests.get(url)
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

                    # Open and OCR the image
                    img = Image.open(BytesIO(img_response.content))
                    text = pytesseract.image_to_string(img).strip()

                    results.append({
                        "image_url": full_img_url,
                        "extracted_text": text
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
