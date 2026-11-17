import os, json, pymysql
from pymysql.constants import CLIENT

def conn():
    return pymysql.connect(host=os.environ['DB_HOST'], user=os.environ['DB_USER'],
                           password=os.environ['DB_PASSWORD'], database=os.environ['DB_NAME'],
                           cursorclass=pymysql.cursors.DictCursor, connect_timeout=10,
                           client_flag=CLIENT.FOUND_ROWS)

def resp(code, body):
    return {'statusCode': code,
            'headers': {'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(body, default=str)}

def get_body(event):
    try:
        return json.loads(event.get('body') or '{}')
    except ValueError:
        return {}

def lambda_handler(event, context):
    b = get_body(event)
    if not b.get('name'):
        return resp(400, {'message': 'name is required'})
    c = conn()
    with c.cursor() as cur:
        cur.execute('INSERT INTO users (name,email,institution,position,phone,image) VALUES (%s,%s,%s,%s,%s,%s)',
                    (b.get('name'), b.get('email'), b.get('institution'),
                     b.get('position'), b.get('phone'), b.get('image')))
        new_id = cur.lastrowid
    c.commit()
    c.close()
    return resp(201, {'id': new_id, 'message': 'User created'})
