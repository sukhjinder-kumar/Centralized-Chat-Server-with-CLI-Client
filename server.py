import socket
import threading

# List to store all active client connections
clients = []

# Broadcast message to all clients
def broadcast(message, client_socket):
    for client in clients:
        if client != client_socket:
            try:
                client.send(message)
            except:
                # Handle client disconnection
                clients.remove(client)

# Handle communication with a client
def handle_client(client_socket):
    # Add the client to the list of active clients
    clients.append(client_socket)
    
    try:
        while True:
            # Receive message from the client
            message = client_socket.recv(1024)
            if not message:
                break  # Client disconnected
            # Broadcast the message to all other clients
            broadcast(message, client_socket)
    except:
        pass
    finally:
        # Remove the client from the list and close the connection
        clients.remove(client_socket)
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
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    host = "127.0.0.1"  # Localhost
    port = 12345  # Port for the server
    start_server(host, port)
