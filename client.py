import socket
import threading
import sys
import select


def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("Disconnected.")
                break
            print(data.decode('utf-8'), end='')
        except:
            break


def send_messages(sock):
    while True:
        ready, _, _ = select.select([sys.stdin], [], [], 0.1)
        if ready:
            line = sys.stdin.readline().strip()
            if line.startswith('/quit'):
                sock.send(b'/quit')
                break
            sock.send(line.encode('utf-8'))


def start_client(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    # Receive and display username prompt from server
    resp = sock.recv(1024).decode('utf-8')
    print(resp, end='', flush=True)
    uname = sys.stdin.readline().strip()
    sock.send(uname.encode('utf-8'))

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()
    send_messages(sock)
    sock.close()


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 12345
    start_client(host, port)
