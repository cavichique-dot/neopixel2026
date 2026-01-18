# app/models.py ← VERSIÓN FINAL CON FECHA EN HORA LOCAL (VERACRUZ)
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  # ← IMPORTAMOS db DESDE __init__.py


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    fecha = db.Column(db.DateTime, default=datetime.now, nullable=False)


class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)


class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.now, nullable=False)
    total = db.Column(db.Float, nullable=False)
    abonado = db.Column(db.Float, default=0)
    estado = db.Column(db.String(20), default='pendiente')
    metodo_pago = db.Column(db.String(20), default='efectivo')
    entregado = db.Column(db.Boolean, default=False, nullable=False)
    estatus_pedido = db.Column(db.String(50), default='Pedido', nullable=False)

    items = db.relationship('ItemVenta', backref='venta', lazy=True, cascade="all, delete-orphan")
    cliente = db.relationship('Cliente', backref='ventas')
    abonos = db.relationship('Abono', backref='venta', lazy=True, cascade="all, delete-orphan")


class ItemVenta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    producto = db.relationship('Producto')


class Abono(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id'), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    metodo_pago = db.Column(db.String(20), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.now, nullable=False)