from flask import Flask, jsonify
from flask import send_from_directory

import boto3
import os

app = Flask(__name__)

# Configure AWS S3
S3_BUCKET = "more-portfolio"
S3_REGION = "us-east-2"
S3_BASE_URL = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com"

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory('.', path)
    
@app.route('/images/<category>', methods=['GET'])
def get_images(category):
    """Fetch image URLs from an S3 folder."""
    s3 = boto3.client('s3')
    prefix = f"portfolio_images/{category}/"

    try:
        response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
        if 'Contents' in response:
            images = [
                f"{S3_BASE_URL}/{item['Key']}"
                for item in response['Contents']
                if item['Key'].endswith(('.jpg', '.png', '.jpeg'))
            ]
            return jsonify(images=images)
        else:
            return jsonify(error="No images found in this category"), 404
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
