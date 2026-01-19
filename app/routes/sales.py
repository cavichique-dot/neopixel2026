# app/routes/sales.py → VERSIÓN FINAL CON FIX PARA TICKET (datos siempre actualizados)
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import Cliente, Producto, Venta, ItemVenta, Abono, db
from sqlalchemy import func
from sqlalchemy.orm import joinedload
import qrcode
import base64
from io import BytesIO
from datetime import datetime

sales_bp = Blueprint('sales', __name__, url_prefix='')

# ======================= RUTAS BÁSICAS =======================
@sales_bp.route('/')
@login_required
def index():
    return redirect(url_for('sales.dashboard'))

@sales_bp.route('/dashboard')
@login_required
def dashboard():
    fecha_actual = datetime.now().strftime('%d de %B de %Y')
    return render_template('dashboard.html',
                           clientes=Cliente.query.count(),
                           ventas=Venta.query.count(),
                           ingresos=db.session.query(func.sum(Venta.abonado)).scalar() or 0,
                           pendientes=Venta.query.filter_by(estado='pendiente').count(),
                           fecha_actual=fecha_actual)

# ======================= CLIENTES =======================
@sales_bp.route('/clientes')
@login_required
def clientes():
    return render_template('clientes.html', clientes=Cliente.query.order_by(Cliente.fecha.desc()).all())

@sales_bp.route('/cliente/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_cliente():
    if request.method == 'POST':
        c = Cliente(nombre=request.form['nombre'], telefono=request.form.get('telefono', ''))
        db.session.add(c)
        db.session.commit()
        flash('Cliente agregado', 'success')
        return redirect(url_for('sales.clientes'))
    return render_template('nuevo_cliente.html')

@sales_bp.route('/cliente/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_cliente(id):
    c = Cliente.query.get_or_404(id)
    if request.method == 'POST':
        c.nombre = request.form['nombre']
        c.telefono = request.form.get('telefono', '')
        db.session.commit()
        flash('Cliente actualizado', 'success')
        return redirect(url_for('sales.clientes'))
    return render_template('editar_cliente.html', cliente=c)

@sales_bp.route('/cliente/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_cliente(id):
    c = Cliente.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    flash('Cliente eliminado', 'success')
    return redirect(url_for('sales.clientes'))

# ======================= PRODUCTOS =======================
@sales_bp.route('/productos')
@login_required
def productos():
    return render_template('productos.html', productos=Producto.query.all())

@sales_bp.route('/producto/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_producto():
    if request.method == 'POST':
        p = Producto(nombre=request.form['nombre'], precio=float(request.form['precio']), stock=int(request.form.get('stock', 0)))
        db.session.add(p)
        db.session.commit()
        flash('Producto agregado', 'success')
        return redirect(url_for('sales.productos'))
    return render_template('nuevo_producto.html')

@sales_bp.route('/producto/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    p = Producto.query.get_or_404(id)
    if request.method == 'POST':
        p.nombre = request.form['nombre']
        p.precio = float(request.form['precio'])
        p.stock = int(request.form.get('stock', 0))
        db.session.commit()
        flash('Producto actualizado', 'success')
        return redirect(url_for('sales.productos'))
    return render_template('editar_producto.html', producto=p)

@sales_bp.route('/producto/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_producto(id):
    p = Producto.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    flash('Producto eliminado', 'success')
    return redirect(url_for('sales.productos'))

# ======================= VENTAS =======================
@sales_bp.route('/ventas')
@login_required
def ventas():
    return render_template('ventas.html', ventas=Venta.query.order_by(Venta.fecha.desc()).all())

@sales_bp.route('/venta/nueva', methods=['GET', 'POST'])
@login_required
def nueva_venta():
    if request.method == 'POST':
        cliente_id = request.form['cliente']
        metodo_general = request.form.get('metodo_pago', 'efectivo')
        abono_inicial = float(request.form.get('abono_inicial', 0))
        metodo_abono_inicial = request.form.get('metodo_abono_inicial', metodo_general)
        items = request.form.getlist('items[]')
        cantidades = request.form.getlist('cantidades[]')
        precios = request.form.getlist('precios[]')
        total = sum(float(cantidades[i]) * float(precios[i]) for i in range(len(items)))
        venta = Venta(
            cliente_id=cliente_id,
            total=total,
            abonado=abono_inicial if abono_inicial > 0 else 0,
            metodo_pago=metodo_general,
            entregado=False,
            estatus_pedido='Pedido'
        )
        db.session.add(venta)
        db.session.flush()
        if abono_inicial > 0:
            abono = Abono(
                venta_id=venta.id,
                monto=abono_inicial,
                metodo_pago=metodo_abono_inicial
            )
            db.session.add(abono)
        for i in range(len(items)):
            db.session.add(ItemVenta(
                venta_id=venta.id,
                producto_id=items[i],
                cantidad=int(cantidades[i]),
                precio=float(precios[i])
            ))
        db.session.commit()
        flash(f'VENTA #{venta.id} CREADA', 'success')
        return redirect(url_for('sales.ventas'))
    return render_template('nueva_venta.html', clientes=Cliente.query.all(), productos=Producto.query.all())

@sales_bp.route('/ticket/<int:id>')
@login_required
def ticket(id):
    # FIX: carga datos frescos y evita caché
    venta = Venta.query.options(joinedload(Venta.abonos)).get_or_404(id)
    db.session.refresh(venta)  # Fuerza recargar desde DB los cambios más recientes
    
    items = ItemVenta.query.filter_by(venta_id=id).all()
    estatus_actual = getattr(venta, 'estatus_pedido', 'Pedido') or 'Pedido'
    texto_qr = f"Estatus del pedido:\n{estatus_actual}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=15,
        border=8,
    )
    qr.add_data(texto_qr)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1e40af", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return render_template(
        'ticket.html',
        venta=venta,
        items=items,
        qr=qr_base64
    )

@sales_bp.route('/venta/<int:id>/estatus/<estatus>', methods=['POST'])
@login_required
def actualizar_estatus(id, estatus):
    venta = Venta.query.get_or_404(id)
    pasos_validos = ['Pedido', 'Revisión de Diseño', 'Diseño Autorizado', 'Producción', 'Listo para Entrega', 'Entregado']
    if estatus in pasos_validos:
        venta.estatus_pedido = estatus
        if estatus == 'Entregado':
            venta.entregado = True
        db.session.commit()
        flash(f'Estatus actualizado a: {estatus}', 'success')
    else:
        flash('Estatus inválido', 'error')
    return redirect(url_for('sales.ventas'))

@sales_bp.route('/venta/<int:id>/abonar', methods=['GET', 'POST'])
@login_required
def abonar_venta(id):
    venta = Venta.query.get_or_404(id)
    if request.method == 'POST':
        abono_monto = float(request.form['abono'])
        abono_metodo = request.form.get('metodo_abono', 'efectivo')
        nuevo_abono = Abono(
            venta_id=venta.id,
            monto=abono_monto,
            metodo_pago=abono_metodo
        )
        db.session.add(nuevo_abono)
        venta.abonado += abono_monto
        venta.estado = 'pagado' if venta.abonado >= venta.total else 'pendiente'
        db.session.commit()
        flash(f'Abono de ${abono_monto:,.0f} ({abono_metodo.capitalize()}) registrado', 'success')
        return redirect(url_for('sales.ventas'))
    return render_template('abonar_venta.html', venta=venta)

@sales_bp.route('/venta/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_venta(id):
    venta = Venta.query.get_or_404(id)
    items = ItemVenta.query.filter_by(venta_id=id).all()
    if request.method == 'POST':
        venta.cliente_id = request.form['cliente']
        venta.metodo_pago = request.form.get('metodo_pago', 'efectivo')
        ItemVenta.query.filter_by(venta_id=id).delete()
        items_ids = request.form.getlist('items[]')
        cantidades = request.form.getlist('cantidades[]')
        precios = request.form.getlist('precios[]')
        total = 0
        for i in range(len(items_ids)):
            cant = int(cantidades[i])
            precio = float(precios[i])
            total += cant * precio
            db.session.add(ItemVenta(venta_id=venta.id, producto_id=items_ids[i], cantidad=cant, precio=precio))
        venta.total = total
        venta.abonado = float(request.form.get('abonado', 0))
        venta.estado = 'pagado' if venta.abonado >= venta.total else 'pendiente'
        db.session.commit()
        flash(f'VENTA #{venta.id} ACTUALIZADA', 'success')
        return redirect(url_for('sales.ventas'))
    return render_template('editar_venta.html', venta=venta, items=items, clientes=Cliente.query.all(), productos=Producto.query.all())

@sales_bp.route('/venta/<int:id>/cancelar', methods=['GET', 'POST'])
@login_required
def cancelar_venta(id):
    venta = Venta.query.get_or_404(id)
    if request.method == 'POST':
        ItemVenta.query.filter_by(venta_id=id).delete()
        Abono.query.filter_by(venta_id=id).delete()
        db.session.delete(venta)
        db.session.commit()
        flash(f'VENTA #{id} CANCELADA correctamente', 'warning')
        return redirect(url_for('sales.ventas'))
    return render_template('confirmar_cancelar.html', venta=venta)

@sales_bp.route('/venta/<int:id>/entregar', methods=['POST'])
@login_required
def marcar_entregado(id):
    venta = Venta.query.get_or_404(id)
    venta.entregado = True
    venta.estatus_pedido = 'Entregado'
    db.session.commit()
    flash(f'Venta #{id} marcada como ENTREGADA', 'success')
    return redirect(url_for('sales.ventas'))