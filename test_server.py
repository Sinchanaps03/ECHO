from flask import Flask, send_from_directory, send_file
import os

app = Flask(__name__, static_folder='frontend/build/static', static_url_path='/static')

@app.route('/')
def serve_index():
    return send_file('frontend/build/index.html')

@app.route('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    print("Starting test server...")
    app.run(host='0.0.0.0', port=5000, debug=False)