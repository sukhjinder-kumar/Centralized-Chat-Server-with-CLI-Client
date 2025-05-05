import socket
import threading
import datetime

clients = []  # List of client sockets
channels = {}  # channel_name -> list of client sockets
client_channels = {}  # client_socket -> channel_name
user_names = {}  # client_socket -> username
name_to_socket = {}  # username -> client_socket
clients_lock = threading.Lock()


def remove_client(client_socket):
    """Remove a client from all tracking structures and log the event."""
    uname = user_names.get(client_socket, '<unknown>')
    with clients_lock:
        if client_socket in clients:
            clients.remove(client_socket)
    old_chan = client_channels.pop(client_socket, None)
    if old_chan and client_socket in channels.get(old_chan, []):
        channels[old_chan].remove(client_socket)
    if client_socket in user_names:
        user_names.pop(client_socket)
    if uname in name_to_socket:
        name_to_socket.pop(uname)
    # Log removal
    print(f"[Server] {uname} removed from channel '{old_chan}' and disconnected.")


def broadcast_to_channel(channel, message, sender=None):
    """Send message to all clients in a channel, except optional sender."""
    for client in list(channels.get(channel, [])):
        if client != sender:
            try:
                client.send(message)
            except:
                remove_client(client)


def send_private(sender_sock, target_name, message):
    """Send a private message to target user."""
    target_sock = name_to_socket.get(target_name)
    if target_sock:
        try:
            target_sock.send(message)
            return True
        except:
            remove_client(target_sock)
    return False


def handle_join(sock, new_chan):
    """Move client to a new channel and log the event."""
    uname = user_names.get(sock, '<unknown>')
    old = client_channels.get(sock)
    if old and sock in channels.get(old, []):
        channels[old].remove(sock)
        msg = f"{uname} left {old}\n".encode()
        broadcast_to_channel(old, msg)
        print(f"[Server] {uname} left channel '{old}'")
    channels.setdefault(new_chan, []).append(sock)
    client_channels[sock] = new_chan
    sock.send(f"Switched to channel {new_chan}\n".encode())
    broadcast_to_channel(new_chan, f"{uname} joined {new_chan}\n".encode(), sender=sock)
    print(f"[Server] {uname} joined channel '{new_chan}'")


def handle_client(client_socket, client_address):
    """Per-client thread: handshake, commands, messaging."""
    with clients_lock:
        clients.append(client_socket)

    # Handshake: get username
    try:
        client_socket.send(b"Enter username: ")
        uname = client_socket.recv(1024).decode('utf-8').strip()
        user_names[client_socket] = uname
        name_to_socket[uname] = client_socket
        print(f"[Server] {uname} connected from {client_address}")
    except:
        client_socket.close()
        return

    # Join default channel
    client_channels[client_socket] = 'general'
    channels.setdefault('general', []).append(client_socket)
    client_socket.send(b"Welcome to #general! Use /join <channel>, /msg <user> <msg>, /quit\n")
    broadcast_to_channel('general', f"{uname} joined general\n".encode(), sender=client_socket)
    print(f"[Server] {uname} joined channel 'general'")

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                text = '/quit'
            else:
                text = data.decode('utf-8').strip()

            if text == '/quit':
                ch = client_channels.get(client_socket, 'general')
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                leave_msg = f"[{timestamp}] {uname} disconnected\n".encode()
                remove_client(client_socket)
                broadcast_to_channel(ch, leave_msg)
                break

            if text.startswith('/join '):
                _, chan = text.split(maxsplit=1)
                handle_join(client_socket, chan)
                continue
            if text.startswith('/msg '):
                parts = text.split(maxsplit=2)
                if len(parts) < 3:
                    client_socket.send(b"Usage: /msg <username> <message>\n")
                else:
                    _, tgt, msg = parts
                    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    full = f"[PM {ts}] {uname} -> {tgt}: {msg}\n".encode()
                    if not send_private(client_socket, tgt, full):
                        client_socket.send(f"User {tgt} not found or offline.\n".encode())
                continue
            chan = client_channels.get(client_socket, 'general')
            ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            msg = f"[{ts}] {uname}: {text}\n".encode()
            broadcast_to_channel(chan, msg, sender=client_socket)
    except Exception as e:
        print(f"Error with {client_address}: {e}")
    finally:
        if client_socket in clients:
            ch = client_channels.get(client_socket, 'general')
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            leave_msg = f"[{timestamp}] {uname} disconnected\n".encode()
            remove_client(client_socket)
            broadcast_to_channel(ch, leave_msg)
        client_socket.close()


def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[Server] Running on {host}:{port}")
    while True:
        sock, addr = server.accept()
        threading.Thread(target=handle_client, args=(sock, addr), daemon=True).start()


if __name__ == '__main__':
    start_server('127.0.0.1', 12345)
