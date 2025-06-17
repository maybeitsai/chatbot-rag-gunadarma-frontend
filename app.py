# app.py
import chainlit as cl
from dotenv import load_dotenv
from api_client import get_rag_response
import random
from collections import defaultdict

# Muat environment variables dari file .env di awal
load_dotenv()

# --- KUMPULAN LENGKAP PERTANYAAN STARTER (FOKUS KAMPUS) ---
# Daftar ini telah direvisi untuk hanya berisi pertanyaan seputar Universitas Gunadarma.
ALL_STARTERS = [
    # Kategori: Pendaftaran & Admisi
    cl.Starter(
        label="Prosedur pendaftaran",
        message="Bagaimana prosedur pendaftaran mahasiswa baru di Universitas Gunadarma?",
        icon="/public/write.svg",
    ),
    cl.Starter(
        label="Biaya kuliah",
        message="Berapa rincian biaya kuliah untuk fakultas Teknik Industri?",
        icon="/public/write.svg",
    ),
    cl.Starter(
        label="Jalur masuk",
        message="Apa saja jalur masuk yang tersedia untuk calon mahasiswa baru?",
        icon="/public/write.svg",
    ),
    cl.Starter(
        label="Syarat pendaftaran",
        message="Dokumen apa saja yang diperlukan untuk pendaftaran?",
        icon="/public/write.svg",
    ),
    cl.Starter(
        label="Jadwal pendaftaran",
        message="Kapan jadwal pendaftaran mahasiswa baru dibuka dan ditutup?",
        icon="/public/write.svg",
    ),
    cl.Starter(
        label="Program beasiswa",
        message="Apakah ada program beasiswa yang tersedia dan bagaimana cara mendaftarnya?",
        icon="/public/write.svg",
    ),
    # Kategori: Informasi Akademik
    cl.Starter(
        label="Daftar fakultas",
        message="Sebutkan semua fakultas yang ada di Universitas Gunadarma.",
        icon="/public/learn.svg",
    ),
    cl.Starter(
        label="Program studi FIKTI",
        message="Apa saja program studi yang ada di Fakultas Ilmu Komputer & Teknologi Informasi?",
        icon="/public/learn.svg",
    ),
    cl.Starter(
        label="Kalender akademik",
        message="Di mana saya bisa melihat kalender akademik untuk tahun ini?",
        icon="/public/learn.svg",
    ),
    cl.Starter(
        label="Cara mengisi KRS",
        message="Bagaimana langkah-langkah untuk mengisi Kartu Rencana Studi (KRS)?",
        icon="/public/learn.svg",
    ),
    cl.Starter(
        label="Syarat mengambil skripsi",
        message="Apa saja syarat untuk bisa mengambil mata kuliah skripsi?",
        icon="/public/learn.svg",
    ),
    cl.Starter(
        label="Prosedur cuti akademik",
        message="Bagaimana prosedur untuk mengajukan cuti akademik?",
        icon="/public/learn.svg",
    ),
    cl.Starter(
        label="Akreditasi universitas",
        message="Apa status akreditasi Universitas Gunadarma saat ini?",
        icon="/public/learn.svg",
    ),
    cl.Starter(
        label="Program pascasarjana",
        message="Program pascasarjana apa saja yang tersedia?",
        icon="/public/learn.svg",
    ),
    cl.Starter(
        label="Cara melihat IPK",
        message="Bagaimana cara melihat Indeks Prestasi Kumulatif (IPK) di Studentsite?",
        icon="/public/learn.svg",
    ),
    # Kategori: BAAK & Administrasi
    cl.Starter(
        label="Kontak BAAK",
        message="Bagaimana cara menghubungi BAAK Universitas Gunadarma?",
        icon="/public/idea.svg",
    ),
    cl.Starter(
        label="Lokasi kantor BAAK",
        message="Di mana lokasi kantor BAAK di kampus D?",
        icon="/public/idea.svg",
    ),
    cl.Starter(
        label="Prosedur legalisir ijazah",
        message="Bagaimana prosedur untuk legalisir ijazah?",
        icon="/public/idea.svg",
    ),
    cl.Starter(
        label="Mengurus KTM yang hilang",
        message="Apa yang harus saya lakukan jika Kartu Tanda Mahasiswa (KTM) saya hilang?",
        icon="/public/idea.svg",
    ),
    cl.Starter(
        label="Jadwal pembayaran",
        message="Kapan batas akhir pembayaran Uang Kuliah untuk semester depan?",
        icon="/public/idea.svg",
    ),
    cl.Starter(
        label="Mendapatkan transkrip nilai",
        message="Bagaimana cara mendapatkan transkrip nilai resmi?",
        icon="/public/idea.svg",
    ),
    # Kategori: Fasilitas & Kehidupan Kampus
    cl.Starter(
        label="Lokasi perpustakaan",
        message="Di mana lokasi perpustakaan pusat Universitas Gunadarma?",
        icon="/public/question.svg",
    ),
    cl.Starter(
        label="Unit Kegiatan Mahasiswa (UKM)",
        message="Apa saja Unit Kegiatan Mahasiswa (UKM) yang populer?",
        icon="/public/question.svg",
    ),
    cl.Starter(
        label="Fasilitas olahraga",
        message="Fasilitas olahraga apa saja yang dimiliki Gunadarma?",
        icon="/public/question.svg",
    ),
    cl.Starter(
        label="Lokasi kampus J1",
        message="Di mana alamat lengkap kampus J1 Kalimalang?",
        icon="/public/question.svg",
    ),
    cl.Starter(
        label="Akses Wi-Fi kampus",
        message="Bagaimana cara mengakses jaringan Wi-Fi di area kampus?",
        icon="/public/question.svg",
    ),
    cl.Starter(
        label="Fasilitas poliklinik",
        message="Apakah ada fasilitas kesehatan atau poliklinik untuk mahasiswa?",
        icon="/public/question.svg",
    ),
    cl.Starter(
        label="Sejarah Gunadarma",
        message="Ceritakan secara singkat tentang sejarah berdirinya Universitas Gunadarma.",
        icon="/public/question.svg",
    ),
]

# --- LOGIKA UNTUK MENGELOMPOKKAN STARTER ---
STARTERS_BY_ICON = defaultdict(list)
for starter in ALL_STARTERS:
    STARTERS_BY_ICON[starter.icon].append(starter)


@cl.set_chat_profiles
async def chat_profile():
    """
    Menggunakan ChatProfile untuk menampilkan pesan selamat datang, avatar,
    dan starters secara bersamaan di layar awal.
    """

    # Memilih satu starter acak dari setiap grup
    final_starters = []
    for icon_group in STARTERS_BY_ICON.values():
        if icon_group:
            final_starters.append(random.choice(icon_group))

    # Mengacak urutan tampilan starter agar tidak monoton
    random.shuffle(final_starters)

    return [
        cl.ChatProfile(
            name="Chatbot UG",
            markdown_description="""
## &emsp; **Chatbot Universitas Gunadarma** &emsp;

&emsp; Siap membantu seputar info akademik Universitas Gunadarma. &emsp;
""",
            icon="/public/favicon.png",
            starters=final_starters,
        )
    ]


@cl.on_message
async def main(message: cl.Message):
    """
    Fungsi ini dipanggil setiap kali pengguna mengirim pesan.
    """
    final_answer = ""

    async with cl.Step(name="Context", type="run") as step:
        step.input = message.content

        response = await get_rag_response(message.content)

        if response.get("error"):
            final_answer = response["message"]
            step.is_error = True
            step.output = final_answer
        else:
            answer = response.get(
                "answer",
                "Maaf, saya tidak dapat menemukan jawaban untuk pertanyaan Anda.",
            )
            source_urls = response.get("source_urls", [])

            final_answer = answer

            if source_urls:
                unique_urls = sorted(list(set(source_urls)))
                sources_markdown = "\n\n**Sumber:**\n"
                for url in unique_urls:
                    sources_markdown += f"- <{url}>\n"
                final_answer += sources_markdown

            step.output = "Jawaban berhasil ditemukan."

    await cl.Message(content=final_answer, author="Assistant").send()
