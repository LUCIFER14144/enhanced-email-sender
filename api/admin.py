from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

def application(environ, start_response):
    if environ['PATH_INFO'].startswith('/admin'):
        # Serve admin interface
        path = os.path.join(os.path.dirname(__file__), '../admin/templates/admin_login.html')
        with open(path, 'rb') as f:
            response_body = f.read()
        status = '200 OK'
        response_headers = [
            ('Content-Type', 'text/html'),
            ('Content-Length', str(len(response_body)))
        ]
    else:
        # Default response
        response_body = b'{"status": "error", "message": "Not Found"}'
        status = '404 Not Found'
        response_headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response_body)))
        ]
    
    start_response(status, response_headers)
    return [response_body]

# For local testing
if __name__ == '__main__':
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('../admin/templates/admin_login.html', 'rb') as f:
                self.wfile.write(f.read())

    httpd = HTTPServer(('localhost', 8000), Handler)
    print("Server running on port 8000")
    httpd.serve_forever()