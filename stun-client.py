#!/usr/bin/env python3

import http.client
import json
import socket


def main():
    socket_own = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_own.bind(("0.0.0.0", 0))

    server_port = socket_own.getsockname()[1]

    stun_server_connection = http.client.HTTPConnection('localhost', 8080)
    stun_server_connection.connect()
    server_ip = stun_server_connection.sock.getsockname()[0]

    params = json.dumps({
        'server_ip': server_ip,
        'server_port': server_port
    }).encode('utf-8')

    headers = {
        "Content-type": "text/json",
        "Accept": "text/json"
    }

    stun_server_connection.request("POST", "", params, headers)
    stun_server_connection.getresponse()

    stun_server_connection.request('GET', '/')
    response = stun_server_connection.getresponse()

    response_data = json.loads(response.read().decode('utf-8'))

    peer = response_data[0]
    own = response_data[1]

    if peer.get('remote_ip') == "UNDEFINED":
        # the peer has not registered yet, so keep your server open, and wait
        data, addr = socket_own.recvfrom(1024)
        print(data)
        socket_own.sendto("Hello!".encode('utf-8'), addr)
        socket_own.close()

    else:
        socket_peer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if peer.get('local_ip') == peer.get('remote_ip'):
            # peer not under NAT
            addr = ((peer.get('local_ip'), peer.get('port')))
        elif peer.get('remote_ip') == own.get('remote_ip'):
            # peer under common NAT
            addr = ((peer.get('local_ip'), peer.get('port')))
        else:
            # peer is under NAT, so try the remote IP and pray
            addr = ((peer.get('remote_ip'), peer.get('port')))

        socket_peer.sendto("Hello!".encode('utf-8'), addr)
        data, _ = socket_peer.recvfrom(1024)
        print(data)
        socket_peer.close()


if __name__ == '__main__':
    main()
