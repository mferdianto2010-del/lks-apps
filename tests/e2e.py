import requests, io, boto3, os, json
B = 'http://127.0.0.1:5000'
os.environ.update(AWS_ACCESS_KEY_ID='test', AWS_SECRET_ACCESS_KEY='test', AWS_ENDPOINT_URL='http://127.0.0.1:5001')
ok = lambda c, m: print(('PASS ' if c else 'FAIL ') + m) or (c or exit(1))

r = requests.get(B + '/'); ok(r.status_code == 200 and 'User Management' in r.text and 'ADD USER' in r.text, 'GET / -> halaman User Management + ADD USER')
for col in ['ID','NAME','EMAIL','INSTITUTION','POSITION','PHONE','IMAGE','ACTIONS']: ok(f'>{col}<' in r.text.replace('</th><th>', '><').replace('<th class=\'p-2\'>', '>') or col in r.text, f'kolom {col} ada')
ok(requests.get(B + '/health').text == 'ok', 'GET /health')

png = b'\x89PNG\r\n\x1a\n' + b'0' * 64
form = {'name': 'Siti', 'email': 's@mail.com', 'institution': 'SMKN 2', 'position': 'Siswa', 'phone': '0899', 'old_image': ''}
r = requests.post(B + '/api/users', data=form, files={'image_file': ('foto siti.png', io.BytesIO(png), 'image/png')})
ok(r.status_code == 201, f'POST /api/users (dengan gambar) -> {r.status_code} {r.text.strip()}'); uid = r.json()['id']

r = requests.get(B + '/api/users'); rows = r.json()
row = [x for x in rows if x['id'] == uid][0]
ok(row['image'].startswith('https://lks-kotamalang-test-25.s3.amazonaws.com/uploads/') and row['image'].endswith('foto_siti.png'), f"URL gambar tersimpan di DB: {row['image']}")
key = row['image'].split('.amazonaws.com/')[1]
obj = boto3.client('s3').get_object(Bucket='lks-kotamalang-test-25', Key=key)
ok(obj['Body'].read().startswith(b'\x89PNG') and obj['ContentType'] == 'image/png', 'objek gambar benar-benar ada di S3 (ContentType image/png)')

r = requests.put(f'{B}/api/users/{uid}', data={**form, 'position': 'Guru', 'old_image': row['image']})
ok(r.status_code == 200, 'PUT (ubah posisi, gambar lama dipertahankan)')
row = requests.get(B + '/api/users').json()[-1]; ok(row['position'] == 'Guru' and row['image'].endswith('foto_siti.png'), 'data berubah, gambar tetap')
r = requests.put(f'{B}/api/users/{uid}', data={**form, 'position': 'Guru', 'old_image': row['image']}); ok(r.status_code == 200, 'PUT tanpa perubahan data -> 200 (bukan 404)')

x = requests.post(B + '/api/users', data={'name': '<script>alert(1)</script>', 'old_image': ''}); xid = x.json()['id']
ok('<script>alert(1)</script>' in json.dumps(requests.get(B + '/api/users').json()), 'data XSS tersimpan apa adanya (di-escape saat render oleh esc())')
ok(requests.delete(f'{B}/api/users/{xid}').status_code == 200, 'DELETE user XSS')
ok(requests.delete(f'{B}/api/users/{uid}').status_code == 200, 'DELETE user Siti')
ok(requests.delete(f'{B}/api/users/{uid}').status_code == 404, 'DELETE lagi -> 404')
ok(requests.put(f'{B}/api/users/abc', data=form).status_code == 404, 'id non-angka -> 404 dari Flask')
print('E2E SEMUA LULUS')
