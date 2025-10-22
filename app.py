from flask import Flask, render_template, request, redirect, url_for, flash
from db_config import get_connection

app = Flask(__name__)
app.secret_key = 'cambiame_por_una_clave_segura'

# ---------- RUTAS PRINCIPALES ----------
@app.route('/')
def index():
    return render_template('index.html')

# ----------------- PRODUCTOS -----------------
@app.route('/productos')
def productos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_producto, nombre, descripcion, stock_actual, stock_minimo, precio, id_proveedor FROM dbo.productos")
    productos = cursor.fetchall()
    conn.close()
    return render_template('productos.html', productos=productos)

@app.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    stock = request.form.get('stock') or 0
    stock_min = request.form.get('stock_minimo') or 0
    precio = request.form.get('precio') or 0
    proveedor = request.form.get('proveedor') or None

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO productos (nombre, descripcion, stock_actual, stock_minimo, precio, id_proveedor) VALUES (?, ?, ?, ?, ?, ?)",
        (nombre, descripcion, int(stock), int(stock_min), float(precio), int(proveedor) if proveedor else None)
    )
    conn.commit()
    conn.close()
    flash('Producto agregado correctamente.', 'success')
    return redirect(url_for('productos'))

@app.route('/eliminar_producto/<int:id>')
def eliminar_producto(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id_producto = ?", (id,))
    conn.commit()
    conn.close()
    flash('Producto eliminado.', 'info')
    return redirect(url_for('productos'))

# ----------------- PROVEEDORES -----------------
@app.route('/proveedores')
def proveedores():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_proveedor, nombre, telefono, correo, direccion FROM proveedores")
    proveedores = cursor.fetchall()
    conn.close()
    return render_template('proveedores.html', proveedores=proveedores)

@app.route('/agregar_proveedor', methods=['POST'])
def agregar_proveedor():
    nombre = request.form.get('nombre')
    telefono = request.form.get('telefono')
    correo = request.form.get('correo')
    direccion = request.form.get('direccion')

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO proveedores (nombre, telefono, correo, direccion) VALUES (?, ?, ?, ?)",
        (nombre, telefono, correo, direccion)
    )
    conn.commit()
    conn.close()
    flash('Proveedor agregado.', 'success')
    return redirect(url_for('proveedores'))

@app.route('/eliminar_proveedor/<int:id>')
def eliminar_proveedor(id):
    conn = get_connection()
    cursor = conn.cursor()
    # Antes de eliminar, verificar si tiene productos asociados
    cursor.execute("SELECT COUNT(*) FROM productos WHERE id_proveedor = ?", (id,))
    count = cursor.fetchone()[0]
    if count > 0:
        flash('No se puede eliminar el proveedor: tiene productos asociados.', 'danger')
    else:
        cursor.execute("DELETE FROM proveedores WHERE id_proveedor = ?", (id,))
        conn.commit()
        flash('Proveedor eliminado.', 'info')
    conn.close()
    return redirect(url_for('proveedores'))

# ----------------- ENTRADAS -----------------
@app.route('/entradas')
def entradas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id_entrada, e.id_producto, p.nombre, e.cantidad, e.fecha, e.id_proveedor
        FROM entradas e
        JOIN productos p ON e.id_producto = p.id_producto
        ORDER BY e.fecha DESC
    """)
    entradas = cursor.fetchall()
    # para el formulario de agregar entradas
    cursor.execute("SELECT id_producto, nombre FROM productos")
    productos = cursor.fetchall()
    cursor.execute("SELECT id_proveedor, nombre FROM proveedores")
    proveedores = cursor.fetchall()
    conn.close()
    return render_template('entradas.html', entradas=entradas, productos=productos, proveedores=proveedores)

@app.route('/agregar_entrada', methods=['POST'])
def agregar_entrada():
    id_producto = int(request.form.get('id_producto'))
    cantidad = int(request.form.get('cantidad'))
    fecha = request.form.get('fecha')
    id_proveedor = int(request.form.get('id_proveedor'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO entradas (id_producto, cantidad, fecha, id_proveedor) VALUES (?, ?, ?, ?)",
                   (id_producto, cantidad, fecha, id_proveedor))
    # actualizar stock_actual en productos
    cursor.execute("UPDATE productos SET stock_actual = stock_actual + ? WHERE id_producto = ?", (cantidad, id_producto))
    conn.commit()
    conn.close()
    flash('Entrada registrada y stock actualizado.', 'success')
    return redirect(url_for('entradas'))

# ----------------- SALIDAS -----------------
@app.route('/salidas')
def salidas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id_salida, s.id_producto, p.nombre, s.cantidad, s.fecha, s.destino
        FROM salidas s
        JOIN productos p ON s.id_producto = p.id_producto
        ORDER BY s.fecha DESC
    """)
    salidas = cursor.fetchall()
    cursor.execute("SELECT id_producto, nombre FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return render_template('salidas.html', salidas=salidas, productos=productos)

@app.route('/agregar_salida', methods=['POST'])
def agregar_salida():
    id_producto = int(request.form.get('id_producto'))
    cantidad = int(request.form.get('cantidad'))
    fecha = request.form.get('fecha')
    destino = request.form.get('destino')

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO salidas (id_producto, cantidad, fecha, destino) VALUES (?, ?, ?, ?)",
                   (id_producto, cantidad, fecha, destino))
    # actualizar stock_actual en productos (restar)
    cursor.execute("UPDATE productos SET stock_actual = stock_actual - ? WHERE id_producto = ?", (cantidad, id_producto))
    conn.commit()
    conn.close()
    flash('Salida registrada y stock actualizado.', 'success')
    return redirect(url_for('salidas'))
from flask import send_file
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

@app.route('/reporte_productos')
def reporte_productos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_producto, nombre, descripcion, stock_actual, stock_minimo, precio FROM productos")
    productos = cursor.fetchall()
    conn.close()

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 750, "REPORTE DE PRODUCTOS")

    c.setFont("Helvetica", 10)
    y = 700
    for p in productos:
        texto = f"ID: {p[0]} | {p[1]} | {p[2]} | Stock: {p[3]} | Precio: ${p[5]:,.2f}"
        c.drawString(40, y, texto)
        y -= 20
        if y < 50:
            c.showPage()
            y = 750

    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="reporte_productos.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
