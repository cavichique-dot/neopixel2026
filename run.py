# run.py  ← VERSIÓN QUE NUNCA FALLA
from app import create_app

app = create_app()

# Esto evita que cualquier otro script lo ejecute dos veces
if __name__ == '__main__':
    print("=========================================")
    print("   AdSell Pro - NPIXEL 2026")
    print("=========================================")
    print("SISTEMA FULL CARGANDO !!!")
    print("=========================================")
    print("Admin ya existe")
    app.run(debug=True, host='127.0.0.1', port=5000)