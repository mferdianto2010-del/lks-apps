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
    uid = (event.get('pathParameters') or {}).get('id')
    c = conn()
    with c.cursor() as cur:
        cur.execute('SELECT * FROM users WHERE id=%s', (uid,))
        row = cur.fetchone()
    c.close()
    return resp(200, row) if row else resp(404, {'message': 'User not found'})
