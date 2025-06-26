"""Presentation configuration - UI configuration."""

import random
from typing import Dict, List, Any


class ChatProfileConfig:
    """Simplified configuration for chat profiles."""
    
    @staticmethod
    def get_all_questions() -> Dict[str, List[Dict[str, str]]]:
        """Get all categorized questions by icon."""
        return {
            "write.svg": [
                {
                    'label': "Cara mendaftar kuliah",
                    'message': "Bagaimana cara mendaftar kuliah di Universitas Gunadarma?",
                },
                {
                    'label': "Syarat pendaftaran",
                    'message': "Apa saja syarat pendaftaran mahasiswa baru di Universitas Gunadarma?",
                },
                {
                    'label': "Prosedur registrasi ulang",
                    'message': "Bagaimana prosedur registrasi ulang mahasiswa di Universitas Gunadarma?",
                },
                {
                    'label': "Cara mengurus KTM",
                    'message': "Bagaimana cara mengurus Kartu Tanda Mahasiswa (KTM) di Universitas Gunadarma?",
                },
                {
                    'label': "Prosedur mengambil cuti",
                    'message': "Bagaimana prosedur mengajukan cuti akademik di Universitas Gunadarma?",
                }
            ],
            "learn.svg": [
                {
                    'label': "Program studi yang tersedia",
                    'message': "Program studi apa saja yang tersedia di Universitas Gunadarma?",
                },
                {
                    'label': "Sistem pembelajaran",
                    'message': "Bagaimana sistem pembelajaran yang diterapkan di Universitas Gunadarma?",
                },
                {
                    'label': "Kurikulum dan mata kuliah",
                    'message': "Seperti apa kurikulum dan mata kuliah di program studi Universitas Gunadarma?",
                },
                {
                    'label': "Jadwal perkuliahan",
                    'message': "Bagaimana sistem penjadwalan perkuliahan di Universitas Gunadarma?",
                },
                {
                    'label': "Program magang/PKL",
                    'message': "Apakah ada program magang atau Praktek Kerja Lapangan (PKL) di Universitas Gunadarma?",
                }
            ],
            "question.svg": [
                {
                    'label': "Fasilitas kampus",
                    'message': "Fasilitas apa saja yang tersedia di kampus Universitas Gunadarma?",
                },
                {
                    'label': "Perpustakaan dan laboratorium",
                    'message': "Bagaimana fasilitas perpustakaan dan laboratorium di Universitas Gunadarma?",
                },
                {
                    'label': "Layanan mahasiswa",
                    'message': "Layanan apa saja yang tersedia untuk mendukung mahasiswa di Universitas Gunadarma?",
                },
                {
                    'label': "Fasilitas olahraga",
                    'message': "Fasilitas olahraga dan ekstrakurikuler apa saja yang tersedia di Universitas Gunadarma?",
                },
                {
                    'label': "Kantin dan parkir",
                    'message': "Bagaimana fasilitas kantin dan area parkir di Universitas Gunadarma?",
                }
            ],
            "idea.svg": [
                {
                    'label': "Kontak dan alamat",
                    'message': "Dimana alamat dan bagaimana cara menghubungi Universitas Gunadarma?",
                },
                {
                    'label': "Biaya kuliah",
                    'message': "Berapa biaya kuliah dan cara pembayaran di Universitas Gunadarma?",
                },
                {
                    'label': "Beasiswa tersedia",
                    'message': "Program beasiswa apa saja yang tersedia di Universitas Gunadarma?",
                },
                {
                    'label': "Prospek karir lulusan",
                    'message': "Bagaimana prospek karir dan peluang kerja lulusan Universitas Gunadarma?",
                },
                {
                    'label': "Akreditasi program studi",
                    'message': "Bagaimana status akreditasi program studi di Universitas Gunadarma?",
                }
            ]
        }
    
    @staticmethod
    def get_random_starters() -> List[Dict[str, str]]:
        """Get one random question from each icon category."""
        all_questions = ChatProfileConfig.get_all_questions()
        starters = []
        
        for icon, questions in all_questions.items():
            # Pick one random question from each category
            selected_question = random.choice(questions)
            starters.append({
                'label': selected_question['label'],
                'message': selected_question['message'],
                'icon': f"/public/{icon}"
            })
        
        # Shuffle the order of starters to randomize which icon appears first
        random.shuffle(starters)
        return starters
    
    @staticmethod
    def create_chat_profile(hybrid_available: bool = True) -> Dict[str, Any]:
        """Create chat profile with basic configuration."""
        # Get randomized starter questions
        starters = ChatProfileConfig.get_random_starters()
        
        description = """
## **Chatbot Universitas Gunadarma**

Siap membantu menjawab pertanyaan seputar informasi Universitas Gunadarma.
"""
        
        return {
            'name': "Chatbot UG",
            'description': description,
            'icon': "/public/favicon.png",
            'starters': starters,
        }
