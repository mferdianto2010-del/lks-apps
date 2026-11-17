# Simulasi API Gateway REST + Lambda Proxy Integration (stage: production)
import os, json, importlib.util, re
from flask import Flask, request, Response
os.environ.update(DB_HOST='127.0.0.1', DB_USER='admin', DB_PASSWORD='Technobrain2025!', DB_NAME='techno-rds')

def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lambda', name + '.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

ROUTES = [('GET', r'^/users$', 'get_users'), ('POST', r'^/users$', 'create_user'),
          ('GET', r'^/users/(?P<id>[^/]+)$', 'get_user'), ('PUT', r'^/users/(?P<id>[^/]+)$', 'update_user'),
          ('DELETE', r'^/users/(?P<id>[^/]+)$', 'delete_user')]
MODS = {n: load(n) for _, _, n in ROUTES}
app = Flask(__name__)

@app.route('/production/<path:p>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def gw(p):
    path = '/' + p
    for method, pat, fn in ROUTES:
        m = re.match(pat, path)
        if m and method == request.method:
            ev = {'httpMethod': method, 'path': path, 'pathParameters': m.groupdict() or None,
                  'body': request.get_data(as_text=True) or None, 'headers': dict(request.headers)}
            r = MODS[fn].lambda_handler(ev, None)
            return Response(r['body'], status=r['statusCode'], headers=r['headers'])
    return Response(json.dumps({'message': 'Missing Authentication Token'}), status=403)

if __name__ == '__main__':
    app.run(port=8080)
