import os, uuid, logging, requests, boto3
from flask import Flask, render_template, request, Response
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv('API_URL', '').rstrip('/')
S3_BUCKET = os.getenv('S3_BUCKET')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
LOG_PATH = os.getenv('LOG_PATH', '/mnt/efs/log/app.log')

handlers = [logging.StreamHandler()]
try:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    handlers.append(logging.FileHandler(LOG_PATH))
except OSError:
    pass  # EFS belum ter-mount: log hanya ke stdout
logging.basicConfig(level=logging.INFO, handlers=handlers,
                    format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('lks-app')

app = Flask(__name__)
s3 = boto3.client('s3', region_name=AWS_REGION)
FIELDS = ('name', 'email', 'institution', 'position', 'phone')


def payload():
    image = request.form.get('old_image', '')
    f = request.files.get('image_file')
    if f and f.filename:
        key = 'uploads/' + uuid.uuid4().hex + '_' + secure_filename(f.filename)
        s3.upload_fileobj(f, S3_BUCKET, key, ExtraArgs={'ContentType': f.content_type})
        image = 'https://' + S3_BUCKET + '.s3.amazonaws.com/' + key
        log.info('Image uploaded: %s', key)
    data = {k: request.form.get(k, '') for k in FIELDS}
    data['image'] = image
    return data


def relay(method, path, **kw):
    try:
        r = requests.request(method, API_URL + path, timeout=20, **kw)
        return Response(r.content, status=r.status_code, content_type='application/json')
    except requests.RequestException as e:
        log.error('API error: %s', e)
        return Response('{"message": "API unreachable"}', status=502, content_type='application/json')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health')
def health():
    return 'ok'


@app.route('/api/users', methods=['GET'])
def list_users():
    return relay('GET', '/users')


@app.route('/api/users', methods=['POST'])
def create_user():
    log.info('Create user')
    return relay('POST', '/users', json=payload())


@app.route('/api/users/<int:uid>', methods=['PUT'])
def update_user(uid):
    log.info('Update user %s', uid)
    return relay('PUT', '/users/%d' % uid, json=payload())


@app.route('/api/users/<int:uid>', methods=['DELETE'])
def delete_user(uid):
    log.info('Delete user %s', uid)
    return relay('DELETE', '/users/%d' % uid)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
