# api/index.py - Punto de entrada OBLIGATORIO para Vercel

# Importamos la función que crea la app
from app import create_app

# Creamos la instancia de Flask (esto es lo que Vercel necesita)
app = create_app()

# Vercel usa 'application' como entrypoint WSGI
application = app