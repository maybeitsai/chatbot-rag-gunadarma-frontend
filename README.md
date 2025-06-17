# Chatbot Akademik Universitas Gunadarma

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![Built with Chainlit](https://img.shields.io/badge/built%20with-Chainlit-blueviolet)](https://chainlit.io)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Repositori ini berisi kode sumber untuk Chatbot Akademik Universitas Gunadarma, sebuah aplikasi web berbasis AI yang dirancang untuk menjawab pertanyaan seputar lingkungan akademik Gunadarma menggunakan arsitektur RAG (Retrieval-Augmented Generation).

## 📝 Deskripsi Proyek

Proyek ini bertujuan untuk menyediakan asisten virtual yang dapat diakses oleh mahasiswa dan dosen untuk mendapatkan informasi secara cepat dan akurat. Chatbot ini memanfaatkan model bahasa canggih (LLM) yang diperkaya dengan konteks dari basis data pengetahuan internal universitas, yang disimpan dalam sebuah vector database.

## ✨ Fitur Utama

- **Antarmuka Percakapan**: UI yang bersih dan interaktif dibangun dengan **Chainlit**.
- **Arsitektur RAG**: Jawaban tidak hanya berasal dari LLM, tetapi diperkaya dengan informasi relevan yang diambil dari dokumen internal untuk akurasi yang lebih tinggi.
- **Kutipan Sumber**: Setiap jawaban menyertakan referensi ke dokumen sumber, memungkinkan pengguna untuk memverifikasi informasi.
- **Backend Skalabel**: Dibangun di atas **FastAPI** untuk performa tinggi dan kemudahan pengembangan API.
- **Pencarian Vektor Efisien**: Menggunakan **PGVector** untuk menyimpan dan mencari embedding dokumen dengan cepat.
- **Caching System**: Sistem cache untuk mengurangi API calls dan meningkatkan response time.
- **Error Handling**: Penanganan error yang robust dengan retry mechanism dan exponential backoff.
- **Modular Architecture**: Struktur kode yang terorganisir dengan separation of concerns.
- **Type Safety**: Type hints lengkap untuk better development experience.
- **Mudah Dijalankan**: Disederhanakan untuk pengembangan lokal menggunakan `uv`.

## 🏗️ Arsitektur

Proyek ini memiliki arsitektur yang terpisah antara frontend dan backend, yang berkomunikasi melalui API.

- **Frontend**: **Chainlit** bertanggung jawab untuk menangani UI, mengelola state percakapan, dan berkomunikasi dengan backend.
- **Backend**: **FastAPI** menyediakan endpoint API yang dipanggil oleh Chainlit. Endpoint ini menangani logika inti dari RAG.
- **Orkestrasi AI**: **LangChain** digunakan sebagai penghubung yang mengorkestrasi alur RAG: memproses input pengguna, mengambil dokumen relevan dari vector store, menyusun prompt, dan memanggil LLM.
- **Large Language Model (LLM)**: **Google Gemini** digunakan sebagai model dasar untuk memahami pertanyaan dan menghasilkan jawaban.
- **Vector Database**: **PGVector** NeonDB digunakan untuk menyimpan embedding dari dokumen pengetahuan dan melakukan pencarian kemiripan (similarity search).

Alur Sederhana:
`User Input -> Chainlit UI -> FastAPI Endpoint -> LangChain -> PGVector (Retrieve) -> Gemini (Generate) -> FastAPI -> Chainlit UI -> User`

## 🚀 Instalasi & Menjalankan Lokal

Pastikan Anda memiliki Python 3.10+ dan Git terinstal. Proyek ini menggunakan `uv` untuk manajemen environment dan package.

1.  **Clone Repositori**

    ```bash
    git clone https://github.com/maybeitsai/chatbot-rag-gunadarma-frontend.git
    cd chatbot-rag-gunadarma-frontend
    ```

2.  **Instal `uv`** (jika belum punya)

    ```bash
    powershell -c "irm https://astral.sh/uv/install.ps1 | more"
    ```

3.  **Buat Virtual Environment dan Instal Dependensi**

    ```bash
    # Membuat venv di folder .venv
    uv venv

    # Menginstal semua package dari pyproject.toml
    uv sync

    # Menginstall tool chainlit
    uv tool install chainlit
    ```

4.  **Jalankan Aplikasi**
    Aplikasi ini terdiri dari dua bagian yang perlu dijalankan secara terpisah di terminal yang berbeda.

    - **Terminal 1: Jalankan Backend FastAPI**
      Bagian backend memiliki repository yang berbeda. Silahkan lihat panduan [berikut](https://github.com/maybeitsai/chatbot-rag-gunadarma-backend).

      - **Terminal 2: Jalankan Frontend Chainlit**

      ```bash
      # Aktifkan venv jika belum
      source .venv/bin/activate  # Linux/Mac
      # atau untuk Windows:
      .venv\Scripts\activate

      # Jalankan UI Chainlit dengan auto-reload
      chainlit run app.py -w
      ```

    Sekarang, buka browser Anda dan akses `http://localhost:8080`.

## ⚙️ Konfigurasi Lanjutan

### **Environment Variables**

Buat file `.env` untuk konfigurasi environment:

```bash
# Backend API Configuration
FASTAPI_BACKEND_URL=http://localhost:8000

# Optional: Logging level
LOG_LEVEL=INFO
```

### **Custom API Configuration**

```python
from api_client import RAGApiClient, ApiConfig

# Custom configuration
config = ApiConfig(
    base_url="https://your-api.example.com",
    timeout=30.0,
    max_retries=5,
    retry_delay=2.0
)

client = RAGApiClient(config)
```

### **Cache Management**

```python
# Membersihkan cache
client.get_rag_response.cache_clear()

# Cleanup expired entries
client.get_rag_response.cache_cleanup()
```

## 🛠️ Development & Testing

### **Code Quality**

Proyek ini mengikuti best practices:

- **PEP 8 compliance** untuk style consistency
- **Type hints** di semua functions dan methods
- **Comprehensive docstrings** untuk dokumentasi
- **Error handling** yang robust di setiap layer

### **Testing Ready Architecture**

- **Dependency injection** ready untuk unit testing
- **Mock-friendly design** dengan clear abstractions
- **Isolated components** untuk focused testing
- **Configuration externalization** untuk easy mocking

### **Development Tools**

```bash
# Format kode dengan black
uv run black .

# Type checking dengan mypy (opsional)
uv add --dev mypy
uv run mypy .

# Linting dengan ruff (opsional)
uv add --dev ruff
uv run ruff check .
```

### **Performance Monitoring**

- Monitor response times melalui Chainlit UI
- Cache hit rates dapat ditrack melalui logs
- Error rates visible dalam terminal output

## 🔧 Troubleshooting

### **Port Conflicts**

Jika port 8080 sudah digunakan:

```bash
# Gunakan port lain
chainlit run app.py -w --port 8081
```

### **Backend Connection Issues**

```bash
# Cek apakah backend berjalan
curl http://localhost:8000/health

# Update environment variable jika perlu
echo "FASTAPI_BACKEND_URL=http://localhost:8001" >> .env
```

### **Cache Issues**

```python
# Reset cache jika ada masalah
from utils.cache import app_cache
app_cache.clear()
```

### **Common Import Errors**

```bash
# Pastikan virtual environment aktif
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Reinstall dependencies jika perlu
uv sync --reinstall
```

## 📁 Struktur Proyek

```
frontend/
├── .chainlit/              # Konfigurasi Chainlit internal
│   ├──config.toml
├── config/                 # 🆕 Modul konfigurasi
│   ├── __init__.py
│   └── starter_questions.py  # Pertanyaan starter yang terorganisir
├── utils/                  # 🆕 Utilitas dan helper functions
│   ├── __init__.py
│   └── cache.py           # Sistem caching dan utility functions
├── public/                # Asset statis
│   ├── favicon.png
│   ├── idea.svg
│   ├── learn.svg
│   ├── question.svg
│   └── write.svg
├── .env                   # Environment variables
├── .gitignore
├── app.py                 # 🔄 Main Chainlit application (refactored)
├── api_client.py          # 🔄 HTTP client untuk backend (enhanced)
├── chainlit.md           # Halaman welcome Chainlit
├── chainlit.toml         # Konfigurasi Chainlit (port 8080)
├── LICENSE
├── README.md
├── REFACTORING_SUMMARY.md # 🆕 Dokumentasi refactoring
├── pyproject.toml        # Dependensi dan metadata proyek
├── .python-version
└── uv.lock              # Lock file untuk dependensi
```

## 🤝 Kontribusi

Kami menyambut kontribusi dari siapa saja! Jika Anda ingin membantu, silahkan ikuti langkah-langkah berikut:

### **Cara Berkontribusi:**

1.  **Fork** repositori ini.
2.  Buat **branch** baru untuk fitur atau perbaikan Anda (`git checkout -b fitur/nama-fitur`).
3.  Lakukan perubahan dan **commit** (`git commit -m 'feat: Menambahkan fitur X'`).
4.  **Push** ke branch Anda (`git push origin fitur/nama-fitur`).
5.  Buka **Pull Request** ke branch `main` dari repositori ini.

### **Development Guidelines:**

- Ikuti **PEP 8** style guidelines
- Tambahkan **type hints** untuk semua functions
- Tulis **docstrings** untuk dokumentasi
- Test changes thoroughly sebelum submit PR
- Update dokumentasi jika diperlukan

### **Areas for Contribution:**

- **Testing**: Unit tests untuk semua components
- **Performance**: Optimisasi caching dan response time
- **Features**: Fitur baru seperti chat history, user preferences
- **Security**: Input validation dan security enhancements
- **Documentation**: Perbaikan dokumentasi dan examples

Jika Anda menemukan bug atau memiliki ide fitur, silakan buat **Issue** baru dengan template yang sesuai.

## 📚 Referensi & Dokumentasi

- **[Chainlit Documentation](https://docs.chainlit.io)** - Framework untuk chat applications
- **[FastAPI Documentation](https://fastapi.tiangolo.com)** - Backend API framework
- **[LangChain Documentation](https://python.langchain.com)** - LLM orchestration
- **[REFACTORING_SUMMARY.md](./REFACTORING_SUMMARY.md)** - Detail lengkap perubahan refactoring

## 📜 Lisensi

Proyek ini dilisensikan di bawah **Lisensi MIT**. Lihat file [LICENSE](LICENSE) untuk detail lebih lanjut.
