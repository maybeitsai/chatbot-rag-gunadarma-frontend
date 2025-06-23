"""Presentation configuration - UI configuration."""

import random
from collections import defaultdict
from typing import Dict, List, Optional, Any

from ..domain import StarterQuestion


class StarterQuestionsConfig:
    """Configuration for starter questions displayed in the chatbot interface."""
    
    REGISTRATION = "registration"
    ACADEMIC = "academic"
    ADMINISTRATION = "administration"
    FACILITIES = "facilities"
    
    @staticmethod
    def get_all_starter_questions() -> List[StarterQuestion]:
        """Get all starter questions."""
        questions = []
        
        registration_questions = [
            StarterQuestion("Prosedur pendaftaran mahasiswa baru", "/public/write.svg", "registration"),
            StarterQuestion("Rincian biaya kuliah", "/public/write.svg", "registration"),
            StarterQuestion("Jalur masuk yang tersedia", "/public/write.svg", "registration"),
            StarterQuestion("Dokumen persyaratan pendaftaran", "/public/write.svg", "registration"),
        ]
        
        # Academic questions
        academic_questions = [
            StarterQuestion("Sistem perkuliahan", "/public/learn.svg", "academic"),
            StarterQuestion("SKS minimal per semester", "/public/learn.svg", "academic"),
            StarterQuestion("Cara melihat jadwal kuliah", "/public/learn.svg", "academic"),
            StarterQuestion("Program studi tersedia", "/public/learn.svg", "academic"),
        ]
        
        # Administration questions
        admin_questions = [
            StarterQuestion("Mengurus surat keterangan kuliah", "/public/idea.svg", "administration"),
            StarterQuestion("Prosedur cuti akademik", "/public/idea.svg", "administration"),
            StarterQuestion("Mengurus transkrip nilai", "/public/idea.svg", "administration"),
            StarterQuestion("Lokasi bagian akademik", "/public/idea.svg", "administration"),
        ]
        
        # Facilities questions
        facility_questions = [
            StarterQuestion("Fasilitas kampus", "/public/question.svg", "facilities"),
            StarterQuestion("Layanan perpustakaan", "/public/question.svg", "facilities"),
            StarterQuestion("Laboratorium komputer", "/public/question.svg", "facilities"),
            StarterQuestion("Fasilitas olahraga", "/public/question.svg", "facilities"),
        ]
        
        questions.extend(registration_questions)
        questions.extend(academic_questions)
        questions.extend(admin_questions)
        questions.extend(facility_questions)        
        return questions
    
    @staticmethod
    def group_starters_by_icon(starters: List[StarterQuestion]) -> Dict[str, List[StarterQuestion]]:
        """Group starter questions by their icon."""
        grouped = defaultdict(list)
        for starter in starters:
            grouped[starter.icon].append(starter)
        return dict(grouped)
    
    @staticmethod
    def select_random_starters_per_category(
        grouped_starters: Dict[str, List[StarterQuestion]], 
        per_category: int = 1
    ) -> List[Dict[str, Any]]:
        """Select random starters from each category."""
        selected = []
        
        # Mapping dari label pendek ke pertanyaan lengkap
        full_questions = {
            "Prosedur pendaftaran mahasiswa baru": "Bagaimana prosedur pendaftaran mahasiswa baru di Universitas Gunadarma?",
            "Rincian biaya kuliah": "Berapa rincian biaya kuliah untuk fakultas Teknik Industri?",
            "Jalur masuk yang tersedia": "Apa saja jalur masuk yang tersedia untuk calon mahasiswa baru?",
            "Dokumen persyaratan pendaftaran": "Dokumen apa saja yang diperlukan untuk pendaftaran?",
            "Sistem perkuliahan": "Bagaimana sistem perkuliahan di Universitas Gunadarma?",
            "SKS minimal per semester": "Berapa SKS minimal yang harus diambil per semester?",
            "Cara melihat jadwal kuliah": "Bagaimana cara melihat jadwal kuliah dan nilai?",
            "Program studi tersedia": "Apa saja program studi yang tersedia di Universitas Gunadarma?",
            "Mengurus surat keterangan kuliah": "Bagaimana cara mengurus surat keterangan kuliah?",
            "Prosedur cuti akademik": "Prosedur apa saja untuk mengurus cuti akademik?",
            "Mengurus transkrip nilai": "Bagaimana cara mengurus transkrip nilai sementara?",
            "Lokasi bagian akademik": "Di mana lokasi bagian akademik dan administrasi?",
            "Fasilitas kampus": "Fasilitas apa saja yang tersedia di kampus Universitas Gunadarma?",
            "Layanan perpustakaan": "Bagaimana cara mengakses perpustakaan dan layanannya?",
            "Laboratorium komputer": "Di mana lokasi laboratorium komputer dan jam operasionalnya?",
            "Fasilitas olahraga": "Apakah ada fasilitas olahraga dan kesehatan di kampus?"
        }
        
        for icon, starters in grouped_starters.items():
            # Select random starters from this group
            sample_size = min(per_category, len(starters))
            sampled_starters = random.sample(starters, sample_size)
            
            # Convert to chainlit Starter format
            for starter in sampled_starters:
                full_question = full_questions.get(starter.content, starter.content)
                cl_starter = {
                    'label': starter.content,
                    'message': full_question,
                    'icon': starter.icon,
                }
                selected.append(cl_starter)
        
        return selected


class ChatProfileConfig:
    """Configuration for chat profiles."""
    
    @staticmethod
    def create_chat_profile(hybrid_available: bool = True) -> Dict[str, Any]:
        """Create chat profile with appropriate description."""
        all_starters = StarterQuestionsConfig.get_all_starter_questions()
        grouped_starters = StarterQuestionsConfig.group_starters_by_icon(all_starters)
        selected_starters = StarterQuestionsConfig.select_random_starters_per_category(grouped_starters)
        
        description = """
## **Chatbot Universitas Gunadarma**

Siap membantu pertanyaan seputar informasi dari Universitas Gunadarma
"""
        return {
            'name': "Chatbot UG",
            'description': description,
            'icon': "/public/favicon.png",
            'starters': selected_starters,
        }


def select_random_starters_per_category(
    grouped_starters: Dict[str, List[StarterQuestion]], 
    per_category: int = 1
) -> List[Dict[str, Any]]:
    """Select random starters per category."""
    return StarterQuestionsConfig.select_random_starters_per_category(grouped_starters, per_category)
