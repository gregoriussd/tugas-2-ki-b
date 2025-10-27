# DES Encrypted Chat Application

## Identitas
- **Nama**: Gregorius Setiadharma
- **NRP**: 5025231268

---

> **Disclaimer**: Konten README di bawah ini dibuat dengan bantuan AI (GitHub Copilot) sebagai alat bantu dokumentasi. Implementasi kode dan konsep tetap merupakan hasil pembelajaran dan pemahaman sendiri.

---

## Deskripsi Proyek
Aplikasi chat client-server dengan enkripsi DES (Data Encryption Standard) yang diimplementasikan menggunakan Python untuk networking dan C++ untuk algoritma enkripsi/dekripsi. Server berfungsi sebagai relay untuk pesan terenkripsi, sementara client bertanggung jawab untuk enkripsi dan dekripsi pesan.

**Platform**: Windows (client menggunakan executable `.exe` untuk enkripsi/dekripsi)

## Fitur Utama
- ✅ **End-to-End Encryption**: Pesan dienkripsi di client sebelum dikirim
- ✅ **Custom DES Key**: Setiap client dapat menggunakan kunci DES sendiri (16 karakter heksadesimal)
- ✅ **Multi-Client Support**: Server dapat menangani multiple client secara bersamaan
- ✅ **Relay Server**: Server hanya meneruskan pesan terenkripsi tanpa membaca isinya
- ✅ **Windows Compatible**: Dirancang khusus untuk Windows dengan executable `.exe`

## Struktur File
```
tugas-2/
├── client.py           # Client chat dengan enkripsi/dekripsi
├── server.py           # Server relay untuk broadcasting pesan
├── des-encrypt.cpp     # Program enkripsi DES (C++)
├── des-decrypt.cpp     # Program dekripsi DES (C++)
├── socket_info.py      # Informasi konfigurasi socket (opsional)
└── README.md           # Dokumentasi proyek
```

## Cara Instalasi

### 1. Persyaratan Sistem
- **OS**: Windows 10/11
- **Python**: Python 3.x
- **Compiler**: G++ (MinGW-w64)
- **Library Python**: `socket`, `threading`, `subprocess`, `logging` (sudah termasuk dalam Python standard library)

### 2. Install MinGW (jika belum ada)
Download dan install MinGW dari: https://www.mingw-w64.org/

Atau install via chocolatey:
```powershell
choco install mingw
```

### 3. Kompilasi Program C++
Kompilasi program enkripsi dan dekripsi DES di Windows:

```powershell
g++ des-encrypt.cpp -o des-encrypt.exe
g++ des-decrypt.cpp -o des-decrypt.exe
```

Pastikan file `des-encrypt.exe` dan `des-decrypt.exe` berada di direktori yang sama dengan `client.py`.

## Cara Penggunaan

### 1. Menjalankan Server
```bash
python server.py
```

Server akan berjalan pada:
- Host: `0.0.0.0` (semua interface)
- Port: `10000`

Output:
```
INFO:root:starting up on ('0.0.0.0', 10000)
```

### 2. Menjalankan Client
```bash
python client.py
```

Saat client dijalankan, Anda akan diminta memasukkan DES key:
```
==================================================
DES Encrypted Chat Client
==================================================
Enter your DES key (16 hex characters): 133457799BBCDFF1

Key accepted: 133457799BBCDFF1
Connecting to server...
==================================================
Connected to encrypted chat server!
Using DES encryption with key: 133457799BBCDFF1
Type your messages and press Enter to send
Press Ctrl+C to exit
==================================================
You: 
```

### 3. Format DES Key
- Panjang: **16 karakter**
- Format: **Heksadesimal** (0-9, A-F, a-f)
- Contoh: `133457799BBCDFF1`, `AABBCCDDEEFF0011`

### 4. Berkomunikasi
- Client dengan **key yang sama** dapat membaca pesan satu sama lain
- Client dengan **key yang berbeda** akan menerima pesan terenkripsi (gibberish)

## Cara Kerja

### Arsitektur
```
Client A (Key: AAA...)  ──┐
                          │
Client B (Key: AAA...)  ──┼──> Server (Relay) ──┐
                          │                      │
Client C (Key: BBB...)  ──┘                      │
                                                 │
                    ┌────────────────────────────┘
                    │
                    └──> Broadcast ke semua client
```

### Proses Enkripsi/Dekripsi
1. **Mengirim Pesan** (Windows):
   ```
   Plaintext → des-encrypt.exe (subprocess) → Hex Ciphertext → Server
   ```

2. **Menerima Pesan** (Windows):
   ```
   Server → Hex Ciphertext → des-decrypt.exe (subprocess) → Plaintext
   ```

3. **Server**:
   - Hanya menerima dan meneruskan data terenkripsi
   - Tidak melakukan enkripsi/dekripsi
   - Format: `[IP:Port]:HexCiphertext`

**Catatan**: Client menggunakan `subprocess.run()` untuk memanggil executable `.exe` di Windows.

## Algoritma DES
Program ini mengimplementasikan DES (Data Encryption Standard) dengan:
- **Block size**: 64 bit
- **Key size**: 64 bit (56 bit efektif + 8 bit parity)
- **Rounds**: 16 rounds
- **Mode**: ECB (Electronic Codebook)
- **Padding**: Zero padding untuk data yang tidak kelipatan 64 bit

### Komponen DES yang Diimplementasikan
- Initial Permutation (IP)
- Permuted Choice 1 & 2 (PC-1, PC-2)
- Expansion (E-table)
- Substitution Boxes (S-boxes)
- Permutation (P-table)
- Final Permutation (IP⁻¹)
- Key Schedule Generation

## Keamanan

### Kelebihan
- ✅ End-to-end encryption: Server tidak dapat membaca pesan
- ✅ Client control: Setiap client memilih key sendiri
- ✅ Isolated decryption: Dekripsi gagal tidak mempengaruhi client lain

### Keterbatasan
- ⚠️ DES sudah dianggap tidak aman untuk aplikasi modern (gunakan AES untuk produksi)
- ⚠️ Tidak ada key exchange protocol (key harus dibagikan secara manual)
- ⚠️ Tidak ada authentication (tidak ada verifikasi identitas client)
- ⚠️ Rentan terhadap replay attacks
- ⚠️ ECB mode rentan terhadap pattern analysis

### Rekomendasi untuk Produksi
- Gunakan **AES-256** atau **ChaCha20**
- Implementasikan **Diffie-Hellman** atau **ECDH** untuk key exchange
- Tambahkan **HMAC** atau **digital signature** untuk authentication
- Gunakan mode **GCM** atau **CBC** dengan IV yang unik
- Implementasikan **TLS/SSL** untuk transport layer security

## Testing

### Test Case 1: Client dengan Key yang Sama
```
Client A (Key: 133457799BBCDFF1): "Hello World"
Client B (Key: 133457799BBCDFF1): Menerima "Hello World" ✅
```

### Test Case 2: Client dengan Key yang Berbeda
```
Client A (Key: 133457799BBCDFF1): "Secret Message"
Client C (Key: AABBCCDDEEFF0011): Menerima gibberish ✅
```

### Test Case 3: Multiple Clients
```
Server dapat menangani 5+ client secara bersamaan ✅
```

## Troubleshooting

### Error: "des-encrypt.exe not found" atau "FileNotFoundError"
**Solusi**: 
- Pastikan file `des-encrypt.exe` dan `des-decrypt.exe` berada di direktori yang sama dengan `client.py`
- Verifikasi kompilasi berhasil dengan menjalankan `dir *.exe` di PowerShell
- Jika menggunakan path berbeda, ubah path di `client.py`

### Error: "Invalid key!"
**Solusi**: Pastikan key memiliki tepat 16 karakter heksadesimal (0-9, A-F).

### Error: "g++ is not recognized"
**Solusi**: 
- Install MinGW-w64 dan tambahkan ke PATH Windows
- Restart PowerShell/Command Prompt setelah instalasi
- Verifikasi dengan command `g++ --version`

### Server tidak bisa di-interrupt (Ctrl+C)
**Solusi**: Server sudah dikonfigurasi dengan timeout 1 detik untuk mendukung graceful shutdown di Windows.

### Pesan tidak terdekripsi dengan benar
**Solusi**: 
- Pastikan semua client menggunakan key yang sama
- Verifikasi program C++ dikompilasi tanpa error
- Test enkripsi/dekripsi manual: `des-encrypt.exe "test" 133457799BBCDFF1`

### Client Python tidak bisa menjalankan .exe
**Solusi**: 
- Jalankan PowerShell/Command Prompt sebagai Administrator
- Periksa antivirus tidak memblokir executable
- Pastikan Python memiliki permission untuk menjalankan subprocess

## Sistem Operasi
**Platform yang Didukung**: Windows (10/11)

Client menggunakan executable Windows (`.exe`) untuk enkripsi/dekripsi, sehingga **hanya berfungsi di Windows**. Server dapat dijalankan di platform lain, namun untuk fungsionalitas penuh (termasuk client), gunakan Windows.

## Kontribusi
Proyek ini dibuat untuk tugas mata kuliah Keamanan Informasi.

## Lisensi
Educational purposes only.

## Kontak
- **Nama**: Gregorius Setiadharma
- **NRP**: 5025231268
- **Repository**: [tugas-2-ki-b](https://github.com/gregoriussd/tugas-2-ki-b)

---

**Catatan Penting**: 
- Proyek ini dibuat untuk tujuan pembelajaran dan **dirancang khusus untuk Windows**
- Client memerlukan executable `.exe` yang dikompilasi untuk Windows
- Untuk implementasi real-world, gunakan library kriptografi yang sudah teruji seperti OpenSSL, PyCryptodome, atau NaCl
- Untuk cross-platform, implementasi enkripsi/dekripsi perlu diubah dari executable menjadi library Python