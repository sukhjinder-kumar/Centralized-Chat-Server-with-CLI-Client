import socket
import threading
import sys
import select

# Function to handle receiving messages from the server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if message:
                print(f"\n{message}")
            else:
                break
        except:
            break

# Function to handle sending messages to the server
def send_messages(client_socket):
    while True:
        # Use select to allow non-blocking input
        ready_to_read, _, _ = select.select([sys.stdin], [], [], 0.1)
        if ready_to_read:
            message = sys.stdin.readline().strip()
            if message == "/quit":
                client_socket.send("Client disconnected.".encode('utf-8'))
                break
            client_socket.send(message.encode('utf-8'))

def start_client(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print(f"Connected to server at {host}:{port}")

    # Start thread for receiving messages
    threading.Thread(target=receive_messages, args=(client_socket,)).start()

    # Start thread for sending messages
    send_messages(client_socket)

    client_socket.close()

if __name__ == "__main__":
    host = "127.0.0.1"  # Server address
    port = 12345  # Server port
    start_client(host, port)
