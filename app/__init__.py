# app/__init__.py ← VERSIÓN FINAL PARA RENDER.COM (2026)
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Extensiones globales
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configuración (mejorada para producción)
    app.config['SECRET_KEY'] = 'neopixel2026_cambia_esto_por_una_mas_segura'  # ¡Cambia esto en producción!
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Configuración de Login Manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder.'
    login_manager.login_message_category = 'info'
    
    # User loader para Flask-Login
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Crear tablas + usuario admin (solo la primera vez)
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(email='admin@npixel.com').first()
        if not admin:
            admin = User(email='admin@npixel.com', name='Admin Neopixel')
            admin.set_password('admin123')  # ¡Cambia esta contraseña en producción!
            db.session.add(admin)
            db.session.commit()
            print("Usuario admin creado: admin@npixel.com / admin123")
    
    # Registrar Blueprints
    from .routes.auth import auth_bp
    from .routes.sales import sales_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(sales_bp)
    
    return app