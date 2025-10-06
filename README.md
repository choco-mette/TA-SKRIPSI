# STRUKTUR FOLDER
rag_backend/


│ 
├── app/
│   ├── __init__.py
│   ├── main.py                      # Entry point FastAPI
│   │
│   ├── api/                         # Layer endpoint REST API
│   │   ├── v1
│   │       ├── __init__.py 
│   │       ├── routes_users.py
│   │       ├── routes_chat.py
│   │       └── routes_auth.py       
│   │
│   │
│   │
│   ├── core/                        # Core config & utilitas global
│   │   ├── __init__.py
│   │   ├── config.py                # Konfigurasi env, API key, db URL, dll
│   │   ├── security.py              # JWT, hashing password, middleware
│   │   └── logger.py                # Custom logging system
│   │
│   ├── db/                          # Database ORM & koneksi
│   │   ├── __init__.py
│   │   ├── base.py                  # Base declarative SQLAlchemy
│   │   ├── models/                  # Model ORM dari ERD
│   │   │   ├── __init__.py
│   │   │   ├── user_model.py
│   │   │   ├── session_model.py
│   │   │   ├── ai_personality_model.py
│   │   │   ├── knowledge_model.py
│   │   │   ├── chat_model.py
│   │   │   └── response_model.py
│   │   ├── crud/                    # Query logic (Create, Read, Update, Delete)
│   │   │   ├── __init__.py
│   │   │   ├── crud_user.py
│   │   │   ├── crud_chat.py
│   │   │   ├── crud_knowledge.py
│   │   │   └── crud_response.py
│   │   └── database.py              # engine, session local, Base import
│   │
│   ├── rag/                         # Modul RAG (LangChain, Ollama, pgvector)
│   │   ├── __init__.py
│   │   ├── document_loader.py       # Loader PDF/txt ke dalam dokumen
│   │   ├── embeddings.py            # Model embedding (HuggingFace)
│   │   ├── vectorstore.py           # Simpan/ambil data ke pgvector
│   │   ├── retrieval_chain.py       # Setup chain RetrievalQA LangChain
│   │   ├── llm_ollama.py            # Interface LLM DeepSeek (Ollama)
│   │   └── rag_service.py           # Endpoint-level service untuk query user
│   │
│   ├── sentiment/                   # Modul analisis sentimen IndoBERTweet
│   │   ├── __init__.py
│   │   ├── model_loader.py          # Load IndoBERTweet model & tokenizer
│   │   ├── predict_sentiment.py     # Fungsi analisis teks (positive/neutral/negative)
│   │   └── utils.py                 # Preprocessing teks (regex, stopword, dsb)
│   │
│   ├── schemas/                     # Pydantic schema (validasi request/response)
│   │   ├── __init__.py
│   │   ├── user_schema.py
│   │   ├── chat_schema.py
│   │   ├── rag_schema.py
│   │   └── sentiment_schema.py
│   │
│   └── services/                    # Layanan tambahan (background job, caching)
│       ├── __init__.py
│       ├── ai_response_service.py
│       └── history_service.py
│
├── data/
│   ├── documents/                   # PDF/txt sebelum diembedding
│   └── embeddings/                  # Cache embedding lokal (opsional)
│
├── models/                          # Model ter-train (jika disimpan lokal)
│   └── indobertweet/                # Folder IndoBERTweet (tokenizer + config)
│
├── tests/
│   ├── test_api.py
│   ├── test_rag.py
│   └── test_sentiment.py
│
├── .env                             # Environment variable (DB_URL, API_KEY, MODEL_PATH)
├── requirements.txt                 # Daftar library
├── README.md
└── run.sh                           # Script startup otomatis (uvicorn + setup db)