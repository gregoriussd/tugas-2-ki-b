import sys
import socket
import logging
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# List untuk menyimpan semua client yang terhubung
clients = []
clients_lock = threading.Lock()

def broadcast(message, sender_connection):
    with clients_lock:
        for client in clients:
            if client != sender_connection:
                try:
                    client.sendall(message)
                except Exception as e:
                    logging.error(f"Error sending to client: {e}")

def handle_client(connection, client_address):
    logging.info(f"Client connected from {client_address}")
    
    # Tambahkan client ke list
    with clients_lock:
        clients.append(connection)
    
    try:
        # Kirim welcome message
        welcome = f"Welcome to chat! You are connected from {client_address}\n".encode()
        connection.sendall(welcome)
        
        # Loop untuk menerima pesan dari client
        while True:
            data = connection.recv(1024)
            if data:
                message = data.decode('utf-8').strip()
                logging.info(f"Received from {client_address}: {message}")
                
                # Format pesan dengan alamat pengirim dan broadcast ke client lain
                formatted_message = f"[{client_address[0]}:{client_address[1]}]: {message}\n".encode()
                broadcast(formatted_message, connection)
            else:
                # Client disconnect
                logging.info(f"Client {client_address} disconnected")
                break
    except Exception as e:
        logging.error(f"Error handling client {client_address}: {e}")
    finally:
        # Hapus client dari list dan tutup koneksi
        with clients_lock:
            if connection in clients:
                clients.remove(connection)
        connection.close()
        logging.info(f"Connection closed for {client_address}")

try:
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #sock.settimeout(10)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1 )
    
    # Tambahkan timeout untuk membuat socket dapat diinterupsi
    sock.settimeout(1.0)

    # Bind socket ke port
    server_address = ('0.0.0.0', 10000) #--> gunakan 0.0.0.0 agar binding ke seluruh ip yang tersedia

    logging.info(f"starting up on {server_address}")
    sock.bind(server_address)
    # Listen koneksi masuk
    sock.listen(5)
    #1 = backlog, merupakan jumlah dari koneksi yang belum teraccept/dilayani yang bisa ditampung, diluar jumlah
    #             tsb, koneks akan direfuse
    while True:
        try:
            # Tunggu koneksi dari client
            connection, client_address = sock.accept()
            connection.settimeout(None)
            
            # Buat thread baru untuk handle client ini
            client_thread = threading.Thread(target=handle_client, args=(connection, client_address))
            client_thread.daemon = True
            client_thread.start()
        except socket.timeout:
            continue
        
except KeyboardInterrupt:
    logging.info("\nServer shutting down...")
except Exception as ee:
    logging.info(f"ERROR: {str(ee)}")
finally:
    # Close semua client connections
    with clients_lock:
        for client in clients:
            try:
                client.close()
            except:
                pass
    logging.info('closing')
    sock.close()
