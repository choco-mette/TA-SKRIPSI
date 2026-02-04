mental-health-chatbot/
│
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── rule.py
│   │   ├── personality.py
│   │   ├── document.py
│   │   ├── base_knowledge.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   └── environment.py
│   │
│   ├── schemas/
│   │   ├── user.py
│   │   ├── auth.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   ├── rule.py
│   │   ├── personality.py
│   │   ├── document.py
│   │   └── environment.py
│   │
│   ├── repositories/
│   │   ├── user_repo.py
│   │   ├── conversation_repo.py
│   │   ├── message_repo.py
│   │   ├── rule_repo.py
│   │   ├── document_repo.py
│   │   └── environment_repo.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── chat_service.py
│   │   ├── conversation_service.py
│   │   ├── rag_service.py
│   │   ├── embedding_service.py
│   │   └── admin_service.py
│   │
│   ├── ai/
│   │   ├── llm.py
│   │   ├── prompt_builder.py
│   │   ├── memory.py
│   │   └── rag_pipeline.py
│   │
│   ├── routes/
│   │   ├── deps.py
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── conversation.py
│   │   ├── admin/
│   │   │   ├── rules.py
│   │   │   ├── personality.py
│   │   │   ├── documents.py
│   │   │   └── environment.py
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── chat.html
│   │   └── admin/
│   │       ├── dashboard.html
│   │       ├── rules.html
│   │       ├── personality.html
│   │       └── documents.html
│   │
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   ├── images/
│   │   └── docs/ 
│   │
│   └── utils/
│       ├── logger.py
│       ├── helpers.py
│       └── constants.py
│
├── migrations/
│   └── versions/
│
├── tests/
│   ├── test_auth.py
│   ├── test_conversation.py
│   └── test_chat.py
│
├── .env
├── requirements.txt
├── alembic.ini
├── README.md
└── run.py

# 📁 Penjelasan Struktur Project

## Root Project

`mental-health-chatbot/`

Folder utama yang berisi seluruh source code, konfigurasi, dan dependensi aplikasi chatbot kesehatan mental.

---

## 📂 `app/`

Folder inti aplikasi yang berisi seluruh logic backend, AI, API, dan tampilan web.

---

## 📄 `app/main.py`

**Fungsi:**

- Entry point aplikasi FastAPI
    
- Inisialisasi objek FastAPI
    
- Registrasi router API
    
- Konfigurasi middleware (CORS, error handler)
    

📌 _File pertama yang dijalankan oleh aplikasi._

---

## 📂 `app/core/`

Berisi konfigurasi dan komponen global sistem.

### 📄 `config.py`

- Mengelola environment variable
    
- Konfigurasi aplikasi (DB URL, secret key, dsb)
    
- Centralized configuration
    

---

### 📄 `security.py`

- Password hashing & verification
    
- JWT token generation & validation
    
- Logic keamanan autentikasi
    

---

### 📄 `database.py`

- Konfigurasi koneksi database PostgreSQL
    
- Inisialisasi SQLAlchemy engine & session
    
- Dependency database untuk FastAPI
    

---

## 📂 `app/models/`

Berisi **ORM model (SQLAlchemy)** yang merepresentasikan tabel pada database.

📌 _Setiap file = satu tabel pada ERD._

### Contoh:

- `user.py` → tabel `users`
    
- `conversation.py` → tabel `conversation`
    
- `message.py` → tabel `messages`
    
- `base_knowledge.py` → tabel vector untuk RAG
    
- `environment.py` → konfigurasi model AI
    

📌 Digunakan untuk:

- Mapping object ↔ database
    
- Relasi antar tabel
    

---

## 📂 `app/schemas/`

Berisi **Pydantic schema** untuk validasi data request dan response API.

**Fungsi utama:**

- Validasi input user
    
- Menentukan format output API
    
- Mencegah data sensitif terkirim ke client
    

📌 _Memisahkan data API dari struktur database._

---

## 📂 `app/repositories/`

Layer akses database (Data Access Layer).

**Fungsi:**

- CRUD operation ke database
    
- Query SQLAlchemy
    
- Tidak berisi logic bisnis
    

📌 _Membuat kode lebih rapi dan mudah diuji._

Contoh:

- `user_repo.py` → query user
    
- `conversation_repo.py` → query conversation
    
- `message_repo.py` → query chat
    

---

## 📂 `app/services/`

Layer **business logic** aplikasi.

**Fungsi:**

- Mengatur alur proses sistem
    
- Menghubungkan repository, AI, dan API
    
- Tidak berhubungan langsung dengan HTTP
    

### Contoh:

- `auth_service.py` → login & register
    
- `chat_service.py` → alur chat user–AI
    
- `rag_service.py` → logic RAG
    
- `embedding_service.py` → proses embedding dokumen
    
- `admin_service.py` → logic admin
    

📌 _Ini adalah “otak” aplikasi._

---

## 📂 `app/ai/`

Layer khusus untuk **AI & LangChain**.

### 📄 `llm.py`

- Wrapper koneksi ke OpenAI API
    
- Mengambil konfigurasi model dari database
    

---

### 📄 `prompt_builder.py`

- Menyusun prompt AI
    
- Menggabungkan rules, personality, dan context
    

---

### 📄 `memory.py`

- Mengelola memory percakapan per conversation
    
- Mengambil riwayat chat untuk konteks AI
    

---

### 📄 `rag_pipeline.py`

- Implementasi Retrieval Augmented Generation
    
- Vector search ke pgvector
    
- Menyusun knowledge context
    

📌 _Bagian inti AI untuk skripsi._

---

## 📂 `app/routes/`

Berisi **router FastAPI** (HTTP layer).

### 📄 `deps.py`

- Dependency injection FastAPI
    
- Validasi user login
    
- Role-based access control
    

---

### 📄 `auth.py`

- Endpoint login & register
    
- Token authentication
    

---

### 📄 `chat.py`

- Endpoint chat user dengan AI
    
- Mengirim pesan dan menerima respon AI
    

---

### 📄 `conversation.py`

- Endpoint create & retrieve conversation
    
- Mengelola sesi percakapan
    

---

### 📂 `app/routes/admin/`

Endpoint khusus **admin**.

- `rules.py` → kelola rules AI
    
- `personality.py` → kelola personality AI
    
- `documents.py` → kelola knowledge base
    
- `environment.py` → kelola model AI
    

📌 _Diproteksi role admin._

---

## 📂 `app/templates/`

Template HTML untuk web interface (Jinja2).

### File utama:

- `base.html` → layout dasar
    
- `login.html` → halaman login
    
- `register.html` → halaman register
    
- `chat.html` → halaman chat user
    

### Folder `admin/`

- Dashboard admin
    
- UI manajemen AI & dokumen
    

📌 _Fungsional, bukan UI heavy._

---

## 📂 `app/static/`

Asset statis frontend.

- `css/` → styling
    
- `js/` → JavaScript
    
- `images/` → gambar
    
- `docs/` → file dokumen (knowledge base)
    

---

## 📂 `app/utils/`

Helper dan utilitas umum.

### 📄 `logger.py`

- Logging aplikasi
    

### 📄 `helpers.py`

- Fungsi bantu umum
    

### 📄 `constants.py`

- Konstanta sistem
    

---

## 📂 `migrations/`

- Database migration (Alembic)
    
- Versioning schema database
    

---

## 📂 `tests/`

Unit test dan integration test.

- `test_auth.py`
    
- `test_conversation.py`
    
- `test_chat.py`
    

📌 _Opsional tapi nilai plus._

---

## 📄 `.env`

- Environment variable
    
- Credential dan secret (tidak di-commit)
    

---

## 📄 `requirements.txt`

- Daftar dependency Python
    

---

## 📄 `alembic.ini`

- Konfigurasi Alembic migration
    

---

## 📄 `README.md`

- Dokumentasi project
    
- Cara setup & run aplikasi
    

---

## 📄 `run.py`

- Script untuk menjalankan aplikasi
    
- Alternatif entry point selain `uvicorn`