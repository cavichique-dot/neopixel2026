# run.py  ← VERSIÓN FINAL QUE NUNCA FALLA
from app import create_app

app = create_app()

# Esto evita que se ejecute dos veces cuando lo llama otro script
if __name__ == '__main__':
    with app.app_context():
        print("AdSell Pro - NPIXEL 2026")
        print("="*40)
        print("SISTEMA FULL CARGANDO !!!")
        print("="*40)
    app.run(debug=True, host='127.0.0.1', port=5000)