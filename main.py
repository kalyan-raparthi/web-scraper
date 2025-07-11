from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup, NavigableString, Tag

app = Flask(__name__)

OCR_SPACE_KEY = "K88985616888957"
OCR_SPACE_URL = "https://api.ocr.space/parse/imageurl"

def ocr_image(url):
    try:
        r = requests.get(
            OCR_SPACE_URL,
            params={
                "apikey": OCR_SPACE_KEY,
                "url": url,
                "language": "eng",
                "isOverlayRequired": False
            },
            timeout=15,
        )
        r.raise_for_status()
        j = r.json()
        if j.get("IsErroredOnProcessing"):
            return ""
        pr = j.get("ParsedResults")
        return pr[0].get("ParsedText", "").strip() if pr else ""
    except:
        return ""

@app.route("/extract-ocr", methods=["GET"])
def extract_ocr():
    page_url = request.args.get("url", "").strip()
    if not page_url:
        return jsonify(error="Use /extract-ocr?url=PAGE_URL"), 400

    try:
        resp = requests.get(page_url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        return jsonify(error=f"Failed to fetch page: {e}"), 502

    soup = BeautifulSoup(resp.text, "html.parser")
    body = soup.body
    if not body:
        return jsonify(error="No <body> found"), 500

    parts = []
    for node in body.descendants:
        # skip layout and script/style sections
        if isinstance(node, (NavigableString, Tag)):
            if node.find_parent(("header", "footer", "nav", "aside", "script", "style")):
                continue

        # plain text
        if isinstance(node, NavigableString):
            text = node.strip()
            if text:
                parts.append(text)

        # image → OCR
        elif isinstance(node, Tag) and node.name.lower() == "img":
            src = node.get("src")
            if src:
                img_url = requests.compat.urljoin(page_url, src)
                ocr_text = ocr_image(img_url)
                if ocr_text:
                    parts.append(ocr_text)

    return jsonify(text="\n".join(parts)), 200

if __name__ == "__main__":
    app.run(port=5000)
