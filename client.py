import sys
import socket
import logging
import threading

# Set basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def receive_messages(sock):
    """Thread untuk menerima pesan dari server"""
    while True:
        try:
            data = sock.recv(1024)
            if data:
                message = data.decode('utf-8')
                print(f"\n{message}", end='')
                print("You: ", end='', flush=True)
            else:
                # Server closed connection
                print("\n[Server closed the connection]")
                break
        except Exception as e:
            print(f"\n[Error receiving message: {e}]")
            break

try:
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ('localhost', 10000)
    logging.info(f"connecting to {server_address}")
    sock.connect(server_address)
    
    print("="*50)
    print("Connected to chat server!")
    print("Type your messages and press Enter to send")
    print("Press Ctrl+C to exit")
    print("="*50)
    
    # Start thread untuk menerima pesan
    receive_thread = threading.Thread(target=receive_messages, args=(sock,))
    receive_thread.daemon = True
    receive_thread.start()
    
    # Main loop untuk mengirim pesan
    while True:
        message = input("You: ")
        if message.strip():  # Hanya kirim jika ada isi
            sock.sendall(message.encode('utf-8'))
        
except KeyboardInterrupt:
    print("\n\nDisconnecting from chat...")
except Exception as ee:
    logging.info(f"ERROR: {str(ee)}")
finally:
    logging.info("closing")
    sock.close()
