# api_client.py
import os
import httpx
from typing import Dict, Any, Optional

# Ambil URL dari environment variable, dengan fallback jika tidak ada
BASE_URL = os.getenv("FASTAPI_BACKEND_URL", "http://localhost:8000")
ASK_ENDPOINT = f"{BASE_URL}/ask"


async def get_rag_response(question: str) -> Dict[str, Any]:
    """
    Mengirim pertanyaan ke backend RAG FastAPI dan mengembalikan respons.

    Args:
        question: Pertanyaan dari pengguna.

    Returns:
        Sebuah dictionary berisi respons dari API atau pesan error.
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            payload = {"question": question}
            response = await client.post(ASK_ENDPOINT, json=payload)
            response.raise_for_status()  # Akan raise error untuk status 4xx/5xx
            return response.json()

        except httpx.HTTPStatusError as e:
            # Error dari server (misal: 500 Internal Server Error)
            return {
                "error": True,
                "message": f"Terjadi kesalahan pada server: {e.response.status_code}. Silakan coba lagi nanti.",
            }
        except httpx.RequestError as e:
            # Error koneksi (misal: backend tidak berjalan)
            return {
                "error": True,
                "message": f"Tidak dapat terhubung ke server. Pastikan backend berjalan di {BASE_URL}.",
            }
        except Exception as e:
            # Error tak terduga lainnya
            return {
                "error": True,
                "message": f"Terjadi kesalahan yang tidak terduga: {str(e)}",
            }
