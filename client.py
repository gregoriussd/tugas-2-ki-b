import sys
import socket
import logging
import threading
import subprocess

# Set basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# DES encryption key (16 hex characters) - KEEP THIS SECRET!
DES_KEY = "133457799BBCDFF1"

def encrypt_message(message):
    """Encrypt message using compiled DES program"""
    try:
        result = subprocess.run(
            ['des-encrypt.exe', message, DES_KEY],  # Windows
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Encryption error: {e}")
        return None

def decrypt_message(encrypted_hex):
    """Decrypt message using compiled DES program"""
    try:
        result = subprocess.run(
            ['des-decrypt.exe', encrypted_hex, DES_KEY],  # Pass as command line args
            capture_output=True,
            text=True,
            check=True
        )
        # The C++ program outputs the decrypted text directly
        return result.stdout.strip()
    except Exception as e:
        logging.error(f"Decryption error: {e}")
        return "[Decryption failed]"

def receive_messages(sock):
    """Thread untuk menerima pesan dari server"""
    while True:
        try:
            data = sock.recv(1024)
            if data:
                message = data.decode('utf-8').strip()
                
                # Check if it's an encrypted message from another client
                if message.startswith('[') and ']:' in message:
                    # Extract sender info and encrypted data
                    parts = message.split(']:', 1)
                    if len(parts) == 2:
                        sender = parts[0] + ']'
                        encrypted_hex = parts[1].strip()
                        
                        # Decrypt the message
                        decrypted = decrypt_message(encrypted_hex)
                        print(f"\n{sender} {decrypted}")
                    else:
                        print(f"\n{message}")
                else:
                    # Server message (welcome, etc.)
                    print(f"\n{message}")
                
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
    print("Connected to encrypted chat server!")
    print(f"Using DES encryption with key: {DES_KEY}")
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
            # Encrypt before sending
            encrypted = encrypt_message(message)
            if encrypted:
                logging.info(f"Sending encrypted message (length: {len(encrypted)})")
                sock.sendall(encrypted.encode('utf-8'))
            else:
                print("[ERROR] Failed to encrypt message")
        
except KeyboardInterrupt:
    print("\n\nDisconnecting from chat...")
except Exception as ee:
    logging.info(f"ERROR: {str(ee)}")
finally:
    logging.info("closing")
    sock.close()
