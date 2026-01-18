# start.py  ← ESTE SÍ FUNCIONA SÍ O SÍ
from app import create_app

print("="*40)
print("   AdSell Pro - NPIXEL 2026")
print("="*40)
print("SISTEMA FULL CARGANDO !!!")
print("="*40)

app = create_app()

# Si por algún motivo create_app() devolvió None, te lo digo y paro todo
if app is None:
    print("ERROR FATAL: create_app() devolvió None")
    print("Revisa que al final de app/__init__.py tengas: return app")
    import sys
    sys.exit(1)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)