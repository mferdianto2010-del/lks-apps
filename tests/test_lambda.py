import os, json, importlib.util
os.environ.update(DB_HOST='127.0.0.1', DB_USER='admin', DB_PASSWORD='Technobrain2025!', DB_NAME='techno-rds')

def load(name):
    spec = importlib.util.spec_from_file_location(name, f'lambda/{name}.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def call(mod, body=None, uid=None):
    ev = {'body': json.dumps(body) if body is not None else None,
          'pathParameters': {'id': str(uid)} if uid else None}
    r = mod.lambda_handler(ev, None)
    assert set(r) >= {'statusCode', 'headers', 'body'} and isinstance(r['body'], str), r
    return r['statusCode'], json.loads(r['body'])

print('init_db   ->', load('init_db').lambda_handler({}, None))
print('init_db again (idempotent) ->', load('init_db').lambda_handler({}, None))
M = {n: load(n) for n in ['get_users','create_user','get_user','update_user','delete_user']}

s, b = call(M['create_user'], {'name':'Budi','email':'b@mail.com','institution':'SMKN 1','position':'Siswa','phone':'0812','image':''})
print('POST /users      ->', s, b); assert s == 201; uid = b['id']
print('POST no name     ->', call(M['create_user'], {'email':'x'})); 
s, b = call(M['get_users']); print('GET /users       ->', s, len(b), 'row(s)'); assert s == 200 and any(r['id']==uid for r in b)
s, b = call(M['get_user'], uid=uid); print('GET /users/id    ->', s, b); assert s == 200 and b['name']=='Budi'
print('GET missing      ->', call(M['get_user'], uid=99999)); 
s, b = call(M['update_user'], {'name':'Budi Santoso','email':'b@mail.com','institution':'SMKN 1','position':'Guru','phone':'0812','image':''}, uid); print('PUT /users/id    ->', s, b); assert s == 200
print('after PUT        ->', call(M['get_user'], uid=uid)[1]['name'])
print('PUT missing      ->', call(M['update_user'], {'name':'x'}, 99999)[0])
s, b = call(M['delete_user'], uid=uid); print('DELETE /users/id ->', s, b); assert s == 200
print('DELETE again     ->', call(M['delete_user'], uid=uid)[0])
print('ALL LAMBDA TESTS PASSED')
