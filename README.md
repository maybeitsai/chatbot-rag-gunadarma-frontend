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
      source .venv/bin/activate

      # Jalankan UI Chainlit dengan auto-reload
      chainlit run app.py -w
      ```

    Sekarang, buka browser Anda dan akses `http://localhost:8080` (atau port default Chainlit lainnya).

## 📁 Struktur Proyek

```
.
├── .chainlit/
│   ├── config.toml
├── public/
│   ├── favicon.png
│   ├── idea.svg
│   ├── ...
├── .env
├── .gitignore
├── app.py                
├── api_client.py         
├── chainlit.md           
├── LICENSE               
├── README.md
├── pyproject.toml
├── .python-version
└── uv.lock
```

## 🤝 Kontribusi

Kami menyambut kontribusi dari siapa saja! Jika Anda ingin membantu, silakan ikuti langkah-langkah berikut:

1.  **Fork** repositori ini.
2.  Buat **branch** baru untuk fitur atau perbaikan Anda (`git checkout -b fitur/nama-fitur`).
3.  Lakukan perubahan dan **commit** (`git commit -m 'feat: Menambahkan fitur X'`).
4.  **Push** ke branch Anda (`git push origin fitur/nama-fitur`).
5.  Buka **Pull Request** ke branch `main` dari repositori ini.

Jika Anda menemukan bug atau memiliki ide fitur, silakan buat **Issue** baru.

## 📜 Lisensi

Proyek ini dilisensikan di bawah **Lisensi MIT**. Lihat file [LICENSE](LICENSE) untuk detail lebih lanjut.