import sys
import socket
import logging
import threading
import subprocess

# Set basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# DES_KEY will be set by user input
DES_KEY = ""

def validate_key(key):
    if len(key) != 16:
        return False
    for char in key:
        if char not in '0123456789ABCDEFabcdef':
            return False
    return True

def encrypt_message(message):
    try:
        result = subprocess.run(
            ['des-encrypt.exe', message, DES_KEY],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Encryption error: {e}")
        return None

def decrypt_message(encrypted_hex):
    try:
        result = subprocess.run(
            ['des-decrypt.exe', encrypted_hex, DES_KEY],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception as e:
        logging.error(f"Decryption error: {e}")
        return "[Decryption failed]"

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if data:
                message = data.decode('utf-8').strip()
                
                # Periksa apakah ini pesan terenkripsi dari client lain
                if message.startswith('[') and ']:' in message:
                    # Ekstrak informasi pengirim dan data terenkripsi
                    parts = message.split(']:', 1)
                    if len(parts) == 2:
                        sender = parts[0] + ']'
                        encrypted_hex = parts[1].strip()
                        
                        # Decrypt pesan
                        decrypted = decrypt_message(encrypted_hex)
                        print(f"\r{sender} {decrypted}\nYou: ", end='', flush=True)
                    else:
                        print(f"\r{message}\nYou: ", end='', flush=True)
                else:
                    # Pesan lain dari server (welcome, dll)
                    print(f"\r{message}\nYou: ", end='', flush=True)
            else:
                # Server menutup koneksi
                print("\n[Server closed the connection]")
                break
        except Exception as e:
            print(f"\n[Error receiving message: {e}]")
            break

try:
    # Get and validate DES key from user
    print("="*50)
    print("DES Encrypted Chat Client")
    print("="*50)
    
    while True:
        DES_KEY = input("Enter your DES key (16 hex characters): ").strip()
        if validate_key(DES_KEY):
            break
        else:
            print("Invalid key! Must be exactly 16 hexadecimal characters.")
            print("Example: 133457799BBCDFF1")
    
    print(f"\nKey accepted: {DES_KEY}")
    print("Connecting to server...")
    
    # Create TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Koneksikan socket ke port dimana server mendengarkan
    server_address = ('localhost', 10000)
    logging.info(f"connecting to {server_address}")
    sock.connect(server_address)
    
    print("="*50)
    print("Connected to encrypted chat server!")
    print(f"Using DES encryption with key: {DES_KEY}")
    print("Type your messages and press Enter to send")
    print("Press Ctrl+C to exit")
    print("="*50)
    print("You: ", end='', flush=True)
    
    # Start thread untuk menerima pesan
    receive_thread = threading.Thread(target=receive_messages, args=(sock,))
    receive_thread.daemon = True
    receive_thread.start()
    
    # Main loop untuk mengirim pesan
    while True:
        message = input()
        if message.strip():  # Hanya kirim jika ada isi
            # Encrypt sebelum mengirim
            encrypted = encrypt_message(message)
            if encrypted:
                logging.info(f"Sending encrypted message (length: {len(encrypted)})")
                sock.sendall(encrypted.encode('utf-8'))
                print("You: ", end='', flush=True)
            else:
                print("[ERROR] Failed to encrypt message")
                print("You: ", end='', flush=True)
        else:
            print("You: ", end='', flush=True)
        
except KeyboardInterrupt:
    print("\n\nDisconnecting from chat...")
except Exception as ee:
    logging.info(f"ERROR: {str(ee)}")
finally:
    logging.info("closing")
    sock.close()
