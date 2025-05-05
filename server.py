# server.py
import socket
import threading
import datetime

clients = []  # List to store connected client sockets
channels = {}  # Dictionary: channel_name -> list of client sockets
client_channels = {}  # Dictionary: client_socket -> current channel
clients_lock = threading.Lock()  # Lock for thread-safety


def remove_client(client_socket):
    """Remove client from global list and its channel."""
    with clients_lock:
        if client_socket in clients:
            clients.remove(client_socket)
    prev_channel = client_channels.pop(client_socket, None)
    if prev_channel and client_socket in channels.get(prev_channel, []):
        channels[prev_channel].remove(client_socket)


def broadcast_to_channel(channel_name, message, sender_socket=None):
    """Send message to all clients in a channel (except sender if provided)."""
    for client in list(channels.get(channel_name, [])):
        if client != sender_socket:
            try:
                client.send(message)
            except:
                remove_client(client)


def handle_join(client_socket, new_channel):
    """Handle a /join command: move client to new channel."""
    old = client_channels.get(client_socket)
    # Remove from old channel
    if old and client_socket in channels.get(old, []):
        channels[old].remove(client_socket)
        leave_msg = f"{client_socket.getpeername()} left channel {old}\n"
        broadcast_to_channel(old, leave_msg.encode('utf-8'))
    # Add to new channel
    if new_channel not in channels:
        channels[new_channel] = []
    channels[new_channel].append(client_socket)
    client_channels[client_socket] = new_channel
    join_msg = f"{client_socket.getpeername()} joined channel {new_channel}\n"
    broadcast_to_channel(new_channel, join_msg.encode('utf-8'), sender_socket=client_socket)
    # Confirm to client
    client_socket.send(f"Switched to channel {new_channel}\n".encode('utf-8'))


def handle_client(client_socket, client_address):
    """Main client thread: manages join, messages, and commands."""
    # Register client
    with clients_lock:
        clients.append(client_socket)
    client_channels[client_socket] = 'general'
    # Ensure channel exists
    channels.setdefault('general', []).append(client_socket)

    # Notify
    welcome = f"{client_address} joined general channel\n"
    broadcast_to_channel('general', welcome.encode('utf-8'), sender_socket=client_socket)
    client_socket.send(b"Welcome to #general! Use /join <channel> to switch.\n")

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            text = data.decode('utf-8').strip()
            if text.startswith('/join '):
                # Command to switch channel
                _, chan = text.split(maxsplit=1)
                handle_join(client_socket, chan)
            else:
                # Broadcast normal message with timestamp and user
                channel = client_channels.get(client_socket, 'general')
                ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                msg = f"[{ts}] {client_address}: {text}\n".encode('utf-8')
                broadcast_to_channel(channel, msg, sender_socket=client_socket)
    except Exception as e:
        print(f"Error with {client_address}: {e}")
    finally:
        # Cleanup on disconnect
        remove_client(client_socket)
        channel = client_channels.get(client_socket, 'general')
        leave = f"{client_address} disconnected from {channel}\n".encode('utf-8')
        broadcast_to_channel(channel, leave)
        client_socket.close()


def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Server listening on {host}:{port}...")

    while True:
        client_sock, addr = server.accept()
        print(f"Connection from {addr}")
        threading.Thread(target=handle_client, args=(client_sock, addr), daemon=True).start()


if __name__ == '__main__':
    start_server('127.0.0.1', 12345)
