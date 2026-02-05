# User Acceptance Testing (UAT) - Wellness AI Chatbot

Dokumen ini berisi daftar skenario pengujian untuk memverifikasi fungsionalitas sistem Chatbot Kesehatan Mental (Wellness AI) sebelum dirilis ke pengguna akhir.

**Tanggal:** 5 Februari 2026  
**Status:** Draft

---

## 1. Authentication & User Management

| ID | Skenario | Langkah Pengujian | Ekspektasi Hasil | Status |
| :--- | :--- | :--- | :--- | :--- |
| **AUTH-01** | Login dengan kredensial valid | 1. Buka halaman `/login`; 2. Masukkan username dan password valid; 3. Klik tombol Login | Pengguna berhasil masuk dan diarahkan ke halaman `/chat` atau Dashboard. | |
| **AUTH-02** | Login dengan kredensial invalid | 1. Buka halaman `/login`; 2. Masukkan username/password salah; 3. Klik tombol Login | Muncul pesan error "Invalid credentials" atau sejenisnya. Tidak masuk ke sistem. | |
| **AUTH-03** | Logout dari sistem | 1. Login ke sistem; 2. Klik profil user di sidebar; 3. Pilih "Logout" | Pengguna keluar dari sesi dan diarahkan kembali ke halaman Login. | |
| **AUTH-04** | Unauthorized Access Check | 1. Logout dari sistem; 2. Coba akses URL `/chat` atau `/admin` secara langsung di browser | Sistem me-redirect pengguna ke halaman `/login`. | |

## 2. Admin Panel (Content & Configuration)

| ID | Skenario | Langkah Pengujian | Ekspektasi Hasil | Status |
| :--- | :--- | :--- | :--- | :--- |
| **ADM-01** | Akses Admin Panel | 1. Login sebagai user dengan role `admin`; 2. Buka menu Admin Panel | Halaman Admin terbuka dan menampilkan daftar menu (Knowledge Base, Rules, Personality, Environment). | |
| **ADM-02** | Lihat Daftar Dokumen (Knowledge) | 1. Masuk menu "Base Knowledge"; 2. Cek tabel dokumen | Data ditampilkan dengan kolom yang benar (No, Title, Content, dll). Pagination berfungsi. | |
| **ADM-03** | View Content Modal | 1. Klik tombol "View" pada salah satu row dokumen yang kontennya panjang | Modal popup muncul menampilkan isi teks lengkap agar mudah dibaca. | |
| **ADM-04** | Upload/Tambah Dokumen Baru | 1. Klik "Add Document"; 2. Upload file PDF atau masukkan teks manual; 3. Simpan | Dokumen berhasil disimpan dan muncul di daftar. Pipeline embedding berjalan (validasi backend). | |
| **ADM-05** | CRUD Rules (Aturan Bot) | 1. Masuk menu "Rules"; 2. Tambah rule baru (Create); 3. Edit rule yang ada (Update); 4. Hapus rule (Delete) | - Data baru tersimpan; - Perubahan terupdate di UI; - Data terhapus hilang dari list; - Bot merespon sesuai aturan baru (validasi di Chat). | |
| **ADM-06** | CRUD Personality (Kepribadian AI) | 1. Masuk menu "Personality"; 2. Edit prompt/intruksi kepribadian utama sistem; 3. Simpan konfigurasi | - Konfigurasi tersimpan; - Gaya bicara bot berubah sesuai personality baru saat dites di Chat. | |
| **ADM-07** | CRUD Environment | 1. Masuk menu "Environment"; 2. Tambah/Edit variabel environment khusus (jika ada); 3. Simpan | - Konfigurasi environment tersimpan di database; - Pengaturan baru efektif digunakan oleh sistem. | |

## 3. Chat Interface & Core Functionality

| ID | Skenario | Langkah Pengujian | Ekspektasi Hasil | Status |
| :--- | :--- | :--- | :--- | :--- |
| **CHAT-01** | Tampilan Awal (Welcome Screen) | 1. Login dan buka `/chat`; 2. Pastikan belum ada chat yang dipilih | Tampilan "Welcome Screen" muncul di tengah (Logo & teks "Start a conversation"). Input message disable/enable sesuai logika awal. | |
| **CHAT-02** | Lazy Conversation Creation | 1. Klik tombol "New Chat" (Halaman reset); 2. Ketik pesan "Halo, saya cemas"; 3. Kirim pesan | Conversation baru dibuat **setelah** pesan dikirim. Judul conversation di sidebar otomatis menjadi "Halo, saya cemas..." (potongan pesan). | |
| **CHAT-03** | Interface Locking saat Loading | 1. Kirim pesan ke bot; 2. Coba ketik di input atau klik tombol kirim saat bot "Loading..." | Input field dan tombol kirim **disabled** sampai bot selesai menjawab. Indikator loading muncul. | |
| **CHAT-04** | Penerimaan Respon AI | 1. Kirim pertanyaan terkait kesehatan mental; 2. Tunggu balasan | Bot membalas dengan teks yang relevan. Bubble chat Bot berwarna abu-abu soft (tidak mencolok), User berwarna hijau. | |
| **CHAT-05** | Chat History Navigation | 1. Klik salah satu item history di sidebar | Area chat memuat pesan-pesan lama dari percakapan tersebut. URL browser berubah sesuai ID conversation. | |
| **CHAT-06** | Hamburger Menu (Sidebar Toggle) | 1. Buka di layar besar (Desktop); 2. Klik ikon hamburger di pojok kiri atas | Sidebar history menyembunyikan diri (Hide) agar area chat lebih luas. Klik lagi untuk menampilkan (Show). | |
| **CHAT-07** | Delete Conversation | 1. Hover pada salah satu list conversation di sidebar; 2. Klik ikon sampah (Delete); 3. Konfirmasi "Yes" pada alert | Conversation hilang dari list. Jika conversation yang dihapus sedang aktif, tampilan kembali ke Welcome Screen. | |

## 4. RAG & AI Accuracy (Functional)

| ID | Skenario | Langkah Pengujian | Ekspektasi Hasil | Status |
| :--- | :--- | :--- | :--- | :--- |
| **RAG-01** | Pertanyaan Kontekstual | 1. Upload dokumen tentang "Anxiety" di Admin; 2. Tanya bot "Apa gejala anxiety?" | Bot menjawab berdasarkan dokumen yang diupload, bukan halusinasi random. | |

## 5. UI/UX & Responsive Design

| ID | Skenario | Langkah Pengujian | Ekspektasi Hasil | Status |
| :--- | :--- | :--- | :--- | :--- |
| **UI-01** | Responsive Mobile | 1. Buka aplikasi menggunakan mode mobile (atau resize browser); 2. Cek Sidebar | Sidebar tersembunyi secara default (Drawer). Tombol hamburger membuka sidebar sebagai overlay. | |
| **UI-02** | Styling Bubble Chat | 1. Perhatikan warna bubble | User: Hijau (Primary). Bot: Abu-abu Soft (`#f3f4f6`). Teks mudah dibaca. | |

---

**Catatan Penguji:**
- Gunakan checklist ini untuk setiap iterasi rilis.
- Laporkan bug dengan screenshot dan langkah reproduksi yang jelas.
