"""
Configuration for starter questions displayed in the chatbot interface.

This module contains predefined questions categorized by topics related to
Gunadarma University to help users start conversations with the chatbot.
"""

import random
from collections import defaultdict
from typing import Dict, List

import chainlit as cl


class StarterQuestionCategories:
    """Categories for organizing starter questions."""

    REGISTRATION = "registration"
    ACADEMIC = "academic"
    ADMINISTRATION = "administration"
    FACILITIES = "facilities"


def create_registration_questions() -> List[cl.Starter]:
    """Create starter questions related to registration and admission."""
    return [
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
    ]


def create_academic_questions() -> List[cl.Starter]:
    """Create starter questions related to academic information."""
    return [
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
    ]


def create_administration_questions() -> List[cl.Starter]:
    """Create starter questions related to BAAK and administration."""
    return [
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
    ]


def create_facilities_questions() -> List[cl.Starter]:
    """Create starter questions related to facilities and campus life."""
    return [
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


def get_all_starter_questions() -> List[cl.Starter]:
    """Get all starter questions from all categories."""
    all_questions = []
    all_questions.extend(create_registration_questions())
    all_questions.extend(create_academic_questions())
    all_questions.extend(create_administration_questions())
    all_questions.extend(create_facilities_questions())
    return all_questions


def group_starters_by_icon(starters: List[cl.Starter]) -> Dict[str, List[cl.Starter]]:
    """Group starter questions by their icon for balanced selection."""
    grouped_starters = defaultdict(list)
    for starter in starters:
        grouped_starters[starter.icon].append(starter)
    return dict(grouped_starters)


def select_random_starters_per_category(
    grouped_starters: Dict[str, List[cl.Starter]], shuffle_order: bool = True
) -> List[cl.Starter]:
    """
    Select one random starter from each icon group for display.

    Args:
        grouped_starters: Dictionary of starters grouped by icon
        shuffle_order: Whether to shuffle the final order of starters

    Returns:
        List of selected starters
    """
    selected_starters = []
    for icon_group in grouped_starters.values():
        if icon_group:
            selected_starters.append(random.choice(icon_group))

    if shuffle_order:
        random.shuffle(selected_starters)

    return selected_starters
