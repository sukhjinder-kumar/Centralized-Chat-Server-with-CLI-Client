import socket
import threading
import sys
import select


def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024)
            if not msg:
                print("Disconnected from server.")
                break
            print(msg.decode('utf-8'), end='')
        except:
            break


def send_messages(sock, user_name):
    while True:
        ready, _, _ = select.select([sys.stdin], [], [], 0.1)
        if ready:
            line = sys.stdin.readline().strip()
            if line == '/quit':
                sock.send(f"{user_name} has disconnected.".encode('utf-8'))
                break
            # Handle local command for join
            if line.startswith('/join '):
                sock.send(line.encode('utf-8'))
                continue
            # Normal message
            sock.send(f"{user_name}: {line}".encode('utf-8'))


def start_client(host, port, user_name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print(f"Connected to {host}:{port} as {user_name}")

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()
    send_messages(sock, user_name)
    sock.close()


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 12345
    name = input("Username: ")
    start_client(host, port, name)
