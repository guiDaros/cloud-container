from flask import Flask, render_template, request, jsonify
import boto3
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'mock-access-key')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'mock-secret-key')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME', 'cloud-portfolio-demo')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# Initialize S3 client
try:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    print(f"S3 client initialized for bucket: {AWS_BUCKET_NAME}")
except Exception as e:
    print(f"Error initializing S3 client: {e}")
    s3_client = None

@app.route('/')
def index():
    """Main page showing application info"""
    return render_template('index.html', bucket_name=AWS_BUCKET_NAME)

@app.route('/health')
def health():
    """Health check endpoint for Kubernetes liveness probe"""
    return jsonify({
        'status': 'healthy',
        'service': 'cloud-portfolio-app'
    }), 200

@app.route('/ready')
def ready():
    """Readiness check endpoint for Kubernetes readiness probe"""
    if s3_client is None:
        return jsonify({
            'status': 'not ready',
            'reason': 'S3 client not initialized'
        }), 503
    
    return jsonify({
        'status': 'ready',
        'service': 'cloud-portfolio-app'
    }), 200

@app.route('/files', methods=['GET'])
def list_files():
    """List files in S3 bucket"""
    if s3_client is None:
        return jsonify({
            'error': 'S3 client not available',
            'files': []
        }), 500
    
    try:
        response = s3_client.list_objects_v2(Bucket=AWS_BUCKET_NAME)
        
        if 'Contents' not in response:
            return jsonify({'files': []})
        
        files = [
            {
                'name': obj['Key'],
                'size': obj['Size'],
                'last_modified': obj['LastModified'].isoformat()
            }
            for obj in response['Contents']
        ]
        
        return jsonify({'files': files})
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            return jsonify({
                'error': f'Bucket {AWS_BUCKET_NAME} does not exist',
                'message': 'This is a demo application. Configure AWS credentials to use real S3.',
                'files': []
            }), 200
        return jsonify({'error': str(e), 'files': []}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload file to S3 bucket"""
    if s3_client is None:
        return jsonify({'error': 'S3 client not available'}), 500
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        s3_client.upload_fileobj(
            file,
            AWS_BUCKET_NAME,
            file.filename
        )
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': file.filename
        }), 200
    
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/info')
def info():
    """Return application and AWS configuration info"""
    return jsonify({
        'application': 'Cloud Container Portfolio',
        'version': '1.0.0',
        'aws_region': AWS_REGION,
        'bucket_name': AWS_BUCKET_NAME,
        's3_configured': s3_client is not None
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)