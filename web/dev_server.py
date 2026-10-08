from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json

BACKEND = "http://127.0.0.1:5000"

class Handler(SimpleHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)

        try:
            req = Request(
                BACKEND + "/api/chat",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urlopen(req, timeout=30) as response:
                result = response.read()
                status = response.status

        except HTTPError as e:
            result = e.read()
            status = e.code

        except URLError as e:
            result = json.dumps({
                "error": "Backend connection failed",
                "details": str(e.reason)
            }).encode()
            status = 502

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(result)

    def log_message(self, format, *args):
        print("[WEB]", format % args)

if __name__ == "__main__":
    print("ZOROX Frontend Server: http://127.0.0.1:8080")
    print("Chat proxy: /api/chat -> http://127.0.0.1:5000/api/chat")
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
