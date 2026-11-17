import os, pymysql

def lambda_handler(event, context):
    conn = pymysql.connect(host=os.environ['DB_HOST'], user=os.environ['DB_USER'],
                           password=os.environ['DB_PASSWORD'], connect_timeout=10)
    with conn.cursor() as cur:
        cur.execute('CREATE DATABASE IF NOT EXISTS `techno-rds`')
        cur.execute('USE `techno-rds`')
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            institution VARCHAR(100),
            position VARCHAR(100),
            phone VARCHAR(30),
            image VARCHAR(255)
        )''')
    conn.commit()
    conn.close()
    return {'status': 'ok'}
