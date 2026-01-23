# api/index.py
from app import app  # ← importa tu app Flask (ajusta la ruta si tu estructura es diferente)

# Esto es lo que Vercel necesita para detectar tu app Flask
app = app  # Vercel lo usa como punto de entrada WSGI