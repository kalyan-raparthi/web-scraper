from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)

@app.route('/images', methods=['GET'])
def get_images():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Please provide a URL using ?url= parameter"}), 400

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        images = []
        for img in soup.find_all('img'):
            img_src = img.get('src')
            if img_src:
                # Handle relative URLs by joining with base URL
                full_url = urljoin(url, img_src)
                images.append(full_url)

        return jsonify({"images": images})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
