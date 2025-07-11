from flask import Flask, request, Response
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/', methods=['GET'])
def fetch_and_clean_html():
    url = request.args.get('url')
    if not url:
        return Response("Please provide a URL using ?url= parameter", status=400, mimetype='text/plain')
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

       
        cleaned_html = soup.prettify() 
        # cleaned_html = soup.get_text() 

        return Response(cleaned_html, mimetype='text/html')
    
    except Exception as e:
        return Response(f"Error fetching or parsing URL: {e}", status=500, mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
