import http.server
import socketserver
import json
import sqlite3
import os
import urllib.parse

PORT = 3000
DB_FILE = 'database.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            name TEXT,
            role TEXT,
            salary TEXT,
            performance TEXT
        )
    ''')
    
    # Insert dummy data if table is empty
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        users_data = [
            ('admin', 'admin123', 'مدير النظام الأمني', 'admin', '$15,000', 'Excellent'),
            ('admin2', 'admin123', 'مدير الموارد البشرية', 'admin', '$12,500', 'Excellent'),
            ('user1', 'user123', 'أحمد عبدالله', 'user', '$4,000', 'Good'),
            ('user2', 'user123', 'سارة محمد', 'user', '$4,500', 'Average'),
            ('user3', 'user123', 'خالد عبدالرحمن', 'user', '$3,800', 'Good'),
            ('user4', 'user123', 'فاطمة علي', 'user', '$5,200', 'Excellent'),
            ('user5', 'user123', 'عمر حسن', 'user', '$3,200', 'Needs Improvement'),
            ('user6', 'user123', 'نورة السالم', 'user', '$4,100', 'Good'),
            ('user7', 'user123', 'عبدالعزيز الفهد', 'user', '$6,000', 'Excellent'),
            ('user8', 'user123', 'مريم الدوسري', 'user', '$3,900', 'Average'),
            ('user9', 'user123', 'طارق صالح', 'user', '$4,800', 'Good'),
            ('user10', 'user123', 'هند القحطاني', 'user', '$5,500', 'Excellent'),
            ('user11', 'user123', 'ماجد العتيبي', 'user', '$3,500', 'Needs Improvement'),
            ('user12', 'user123', 'ريم المطيري', 'user', '$4,300', 'Good'),
            ('user13', 'user123', 'فيصل القحطاني', 'user', '$4,700', 'Excellent'),
            ('user14', 'user123', 'نواف الشمري', 'user', '$3,600', 'Average'),
            ('user15', 'user123', 'جواهر السبيعي', 'user', '$5,800', 'Excellent')
        ]
        c.executemany("INSERT INTO users (username, password, name, role, salary, performance) VALUES (?, ?, ?, ?, ?, ?)", users_data)
        conn.commit()
    conn.close()

class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="public", **kwargs)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        if self.path == '/api/login':
            self.handle_login(post_data)
        elif self.path == '/api/update_profile':
            self.handle_update_profile(post_data)
        elif self.path == '/api/reset_db':
            self.handle_reset_db()
        else:
            self.send_error(404)

    def do_GET(self):
        if self.path == '/api/users':
            self.handle_get_users()
        else:
            super().do_GET()

    def handle_login(self, post_data):
        data = json.loads(post_data.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')
        
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(dict(user)).encode('utf-8'))
        else:
            self.send_error(401, 'Invalid credentials')

    def handle_update_profile(self, post_data):
        data = json.loads(post_data.decode('utf-8'))
        user_id = data.get('id')
        is_secure_mode = data.get('secure_mode', False)
        
        if not user_id:
            self.send_error(400, 'User ID is required')
            return

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        if is_secure_mode:
            # SECURE MODE: Whitelisting fields
            # Only allow 'name' to be updated
            new_name = data.get('name')
            if new_name:
                c.execute("UPDATE users SET name=? WHERE id=?", (new_name, user_id))
        else:
            # VULNERABLE MODE: Mass Assignment / No Whitelisting
            # We dynamically build the query based on input JSON keys (Very dangerous!)
            for key, value in data.items():
                if key not in ['id', 'secure_mode']:
                    # VULNERABILITY: Directly using user input to update database fields including 'role'
                    c.execute(f"UPDATE users SET {key}=? WHERE id=?", (value, user_id))
        
        conn.commit()
        
        # Fetch updated user
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=?", (user_id,))
        updated_user = c.fetchone()
        conn.close()

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(dict(updated_user)).encode('utf-8'))

    def handle_reset_db(self):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS users")
        conn.commit()
        conn.close()
        init_db()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))

    def handle_get_users(self):
        # We assume the client sends their role in headers for demo purposes
        # In a real app, this should be verified via a secure session token
        role = self.headers.get('X-User-Role')
        
        if role != 'admin':
            self.send_error(403, 'Forbidden: Admins only')
            return
            
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT id, username, name, role, salary, performance FROM users")
        users = [dict(row) for row in c.fetchall()]
        conn.close()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(users).encode('utf-8'))

if __name__ == "__main__":
    init_db()
    if not os.path.exists("public"):
        os.makedirs("public")
    
    handler = MyRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Serving at port {PORT} - http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
