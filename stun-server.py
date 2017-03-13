#!/usr/bin/env python3

import json
from collections import deque
from http.server import BaseHTTPRequestHandler, HTTPServer

peer_queue = deque(
    [
        {
            'remote_ip': 'UNDEFINED',
            'local_ip': 'UNDEFINED',
            'port': -1
        }, {
            'remote_ip': 'UNDEFINED',
            'local_ip': 'UNDEFINED',
            'port': -1
        }
    ],
    maxlen=2
)


class STUNRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.end_headers()

        message = json.dumps([peer_queue[0], peer_queue[1]]).encode('utf-8')
        self.wfile.write(message)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        stun_request = json.loads(self.rfile.read(content_length).decode('utf-8'))

        peer_queue.append({
            'remote_ip': self.client_address[0],
            'local_ip': stun_request.get('server_ip'),
            'port': stun_request.get('server_port'),
        })

        self.send_response(200)
        self.end_headers()


def main():
    stun_server = HTTPServer(('0.0.0.0', 8080), STUNRequestHandler)
    stun_server.serve_forever()


if __name__ == '__main__':
    main()
