import socket
import threading

clients = []
clients_lock = threading.Lock()

# Broadcast message to all clients except the sender
def broadcast(message, sender_socket):
    with clients_lock:
        for client in clients:
            if client != sender_socket:
                try:
                    client.send(message)
                except:
                    # Handle client disconnection
                    remove_client(client)

# Add a client to the list of clients
def add_client(client_socket):
    with clients_lock:
        clients.append(client_socket)

# Remove a client from the list of clients
def remove_client(client_socket):
    with clients_lock:
        if client_socket in clients:
            clients.remove(client_socket)

# Handle communication with a client
def handle_client(client_socket, client_address):
    try:
        add_client(client_socket)
        welcome_message = f"Welcome! {client_address} has joined the chat.\n"
        broadcast(welcome_message.encode('utf-8'), client_socket)

        while True:
            message = client_socket.recv(1024)
            if not message:
                break  # Client disconnected
            broadcast(message, client_socket)

    except Exception as e:
        print(f"Error with client {client_address}: {e}")
    finally:
        # Remove client and notify others
        remove_client(client_socket)
        leave_message = f"{client_address} has left the chat.\n"
        broadcast(leave_message.encode('utf-8'), client_socket)
        client_socket.close()

# Main server function
def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server started on {host}:{port}...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"New connection from {client_address}")
        
        # Create a new thread for each client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    host = "127.0.0.1"  # Localhost
    port = 12345  # Port for the server
    start_server(host, port)
