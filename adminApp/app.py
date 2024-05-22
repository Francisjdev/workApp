from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import mysql.connector
import smtplib
from datetime import datetime, timezone, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="newuser",
    password="cnps10",
    database="spuntos"
)
cursor = db.cursor()

# Email configuration
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_username = 'arojas.francisco@gmail.com'
smtp_password = 'ggvm azjj vycm bnyk'


@app.route('/')
def index():
    return render_template('login.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']
        query = "SELECT * FROM admins WHERE email=%s AND clave=%s"
        values = (usuario, clave)
        cursor.execute(query, values)
        user = cursor.fetchone()
        if user:
            session['logged_in'] = True
            return redirect(url_for('admin_home'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')


# Logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/admin_home')
def admin_home():
    if 'logged_in' in session:
        query = "SELECT rut, nombre, email, puntos FROM clients ORDER BY puntos DESC LIMIT 10"
        cursor.execute(query)
        clientes = cursor.fetchall()
        return render_template('admin_home.html', clientes=clientes)
    else:
        return redirect(url_for('login'))


@app.route('/client_panel', methods=['GET', 'POST'])
def client_panel():
    if 'logged_in' in session:
        if request.method == 'POST':
            rut = request.form['rut'].strip()
            query = "SELECT rut, nombre, email, puntos FROM clients WHERE rut=%s"
            values = (rut,)
            cursor.execute(query, values)
            cliente = cursor.fetchone()
            print("Query result:")
            print(cliente)
            if cliente:
                
                query = "SELECT rut, tipo_mov, puntos, fecha_mov FROM movimientos WHERE rut=%s ORDER BY fecha_mov"
                values = (rut,)
                cursor.execute(query, values)
                movimientos = cursor.fetchall()
                disable_actions = cliente[3] < 20
                disable_solicitar_descuento = cliente[3] < 50
                return render_template('client_panel.html', cliente=cliente, movimientos=movimientos, disable_actions=disable_actions, disable_solicitar_descuento=disable_solicitar_descuento)
            else:
                return 'Cliente no encontrado'
        return render_template('client_search.html')
    else:
        return redirect(url_for('login'))


@app.route('/mantenedor')
def mantenedor():
    # Add any logic or data retrieval needed for mantenedor.html
    return render_template('mantenedor.html')


# Helper function to send email
def send_email(recipient, subject, body):
    try:
        message = f"Subject: {subject}\n\n{body}"
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, recipient, message)
    except Exception as e:
        print(f"Error sending email: {e}")


@app.route('/cliente', methods=['GET', 'POST'])
def cliente():
    if request.method == 'POST':
        username = request.form['username']
        clave = request.form['clave']
        try:
            # Check if the client's credentials match with the user_login table
            query = "SELECT rut FROM user_login WHERE username=%s AND clave=%s"
            values = (username, clave)
            cursor.execute(query, values)
            client_data = cursor.fetchone()
            if client_data:
                # Client authenticated, get client information from the clients table
                query_client = "SELECT rut, nombre, email, puntos FROM clients WHERE rut=%s"
                values_client = (client_data[0],)  # Use the retrieved RUT from user_login
                cursor.execute(query_client, values_client)
                cliente = cursor.fetchone()
                if cliente:
                    # Get client movimientos
                    movimientos = get_movimientos(cliente[0])
                    # Render cliente.html template with client information and movimientos
                    return render_template('cliente.html', cliente=cliente, movimientos=movimientos)
                else:
                    return 'Cliente no encontrado'
            else:
                # Authentication failed, display an error message or redirect to login page
                return 'Nombre de usuario y/o clave incorrectos'
        except Exception as e:
            print(f"Error during login: {e}")
            return 'Error during login, please try again'
    # Render the cliente_login.html template for GET requests (displaying the login form)
    return render_template('cliente_login.html')


def get_movimientos(rut):
    query = "SELECT rut, tipo_movimiento, puntos, fecha_movimiento FROM movimientos WHERE rut=%s ORDER BY fecha_movimiento"
    values = (rut,)
    cursor.execute(query, values)
    movimientos = cursor.fetchall()
    return movimientos


@app.route('/historial_movimientos/<rut>')
def historial_movimientos(rut):
    query = "SELECT rut, tipo_movimiento, puntos, fecha_movimiento FROM movimientos WHERE rut=%s ORDER BY fecha_movimiento"
    values = (rut,)
    cursor.execute(query, values)
    movimientos = cursor.fetchall()
    return render_template('historial_movimientos.html', movimientos=movimientos)


@app.route('/fetch_table_data', methods=['POST'])
def fetch_table_data():
    selected_table = request.json['selected_table']
    # Perform query based on the selected_table
    if selected_table == 'tipos_mesa':
        query = "SELECT * FROM tipos_mesa"
    elif selected_table == 'sucursales':
        query = "SELECT * FROM sucursales"
    elif selected_table == 'mesas_sucursal':
        query = """
            SELECT ms.id, s.nombre AS sucursal_nombre, tm.nombre AS mesa_nombre, ms.stock_mesas
            FROM mesas_sucursal ms
            INNER JOIN sucursales s ON ms.id_sucursal = s.id
            INNER JOIN tipos_mesa tm ON ms.id_mesa = tm.id
        """
    else:
        return jsonify({'table_html': 'Invalid table selected'})

    cursor.execute(query)
    table_data = cursor.fetchall()

    table_html = '<table><thead><tr>'
    if selected_table == 'tipos_mesa':
        table_html += '<th>ID</th><th>Nombre</th><th>Tamaño</th><th>Cantidad</th></tr></thead><tbody>'
        for row in table_data:
            table_html += f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>'
    elif selected_table == 'sucursales':
        table_html += '<th>ID</th><th>Nombre</th><th>Dirección</th><th>Comuna</th><th>Ciudad</th><th>Teléfono</th><th>Apertura</th><th>Cierre</th></tr></thead><tbody>'
        for row in table_data:
            table_html += f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td>{row[7]}</td></tr>'
    elif selected_table == 'mesas_sucursal':
        table_html += '<th>ID</th><th>Nombre Sucursal</th><th>ID Mesa</th><th>Stock Mesa</th></tr></thead><tbody>'
        for row in table_data:
            table_html += f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>'
    table_html += '</tbody></table>'

    return jsonify({'table_html': table_html})


@app.route('/agregar_entry', methods=['POST'])
def agregar_entry():
    # Get the selected table from the request
    selected_table = request.form['selected_table']

    # Check which table was selected and insert data accordingly
    if selected_table == 'tipos_mesa':
        nombre = request.form['nombre']
        tamano = request.form['tamano']
        cantidad = request.form['cantidad']

        query = "INSERT INTO tipos_mesa (nombre, tamano, cantidad) VALUES (%s, %s, %s)"
        values = (nombre, tamano, cantidad)
        cursor.execute(query, values)
        db.commit()

        return jsonify({'message': 'Data added to tipos_mesa successfully'})
    elif selected_table == 'sucursales':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        comuna = request.form['comuna']
        ciudad = request.form['ciudad']
        telefono = request.form['telefono']
        apertura = request.form['apertura']
        cierre = request.form['cierre']

        query = "INSERT INTO sucursales (nombre, direccion, comuna, ciudad, telefono, apertura, cierre) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (nombre, direccion, comuna, ciudad, telefono, apertura, cierre)
        cursor.execute(query, values)
        db.commit()

        return jsonify({'message': 'Data added to sucursales successfully'})
    elif selected_table == 'mesas_sucursal':
        id_sucursal = request.form['id_sucursal']
        id_mesa = request.form['id_mesa']
        stock_mesas = request.form['stock_mesas']

        query = "INSERT INTO mesas_sucursal (id_sucursal, id_mesa, stock_mesas) VALUES (%s, %s, %s)"
        values = (id_sucursal, id_mesa, stock_mesas)
        cursor.execute(query, values)
        db.commit()

        return jsonify({'message': 'Data added to mesas_sucursal successfully'})
    else:
        return jsonify({'error': 'Invalid table selected'})


@app.route('/actualizar_entry', methods=['POST'])
def actualizar_entry():
    print("Received POST request to /actualizar_entry")
    print("Form Data:", request.form)

    selected_table = request.form.get('selected_table')
    entry_id = request.form.get('id')

    if selected_table is None or entry_id is None:
        return jsonify({'error': 'Missing data in the request'})

    print("Selected Table:", selected_table)
    print("Entry ID:", entry_id)
    

    if selected_table == 'tipos_mesa':
        nombre = request.form['nombre']
        tamano = request.form['tamano']
        cantidad = request.form['cantidad']

        query = "UPDATE tipos_mesa SET nombre=%s, tamano=%s, cantidad=%s WHERE id=%s"
        values = (nombre, tamano, cantidad, entry_id)
        cursor.execute(query, values)
        db.commit()

        return jsonify({'message': 'Data updated in tipos_mesa successfully'})
    elif selected_table == 'sucursales':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        comuna = request.form['comuna']
        ciudad = request.form['ciudad']
        telefono = request.form['telefono']
        apertura = request.form['apertura']
        cierre = request.form['cierre']

        query = "UPDATE sucursales SET nombre=%s, direccion=%s, comuna=%s, ciudad=%s, telefono=%s, apertura=%s, cierre=%s WHERE id=%s"
        values = (nombre, direccion, comuna, ciudad, telefono, apertura, cierre, entry_id)
        cursor.execute(query, values)
        db.commit()

        return jsonify({'message': 'Data updated in sucursales successfully'})
    elif selected_table == 'mesas_sucursal':
        id_sucursal = request.form['id_sucursal']
        id_mesa = request.form['id_mesa']
        stock_mesas = request.form['stock_mesas']

        query = "UPDATE mesas_sucursal SET id_sucursal=%s, id_mesa=%s, stock_mesas=%s WHERE id=%s"
        values = (id_sucursal, id_mesa, stock_mesas, entry_id)
        cursor.execute(query, values)
        db.commit()

        return jsonify({'message': 'Data updated in mesas_sucursal successfully'})
    else:
        return jsonify({'error': 'Invalid table selected'})


@app.route('/borrar_entry', methods=['POST'])
def borrar_entry():
    data = request.get_json()
    print('Data Received:', data)  # Add this print statement to check the received data
    entry_id = data['id']
    selected_table = data['selected_table']
    print('Selected Table:', selected_table)
    print('ID to Delete:', entry_id)  # Add this print statement

    if selected_table == 'tipos_mesa':
        query = "DELETE FROM tipos_mesa WHERE id=%s"
    elif selected_table == 'sucursales':
        query = "DELETE FROM sucursales WHERE id=%s"
    elif selected_table == 'mesas_sucursal':
        query = "DELETE FROM mesas_sucursal WHERE id=%s"
    else:
        return jsonify({'error': 'Invalid table selected'})

    values = (entry_id,)
    cursor.execute(query, values)
    db.commit()

    return jsonify({'message': 'Entry deleted successfully'})

###########################################################
@app.route('/arriendo_diario')
def arriendo_diario():
    return render_template('movimientos_por_fecha.html')


###########################################################
@app.route('/movimientos_por_fecha', methods=['GET', 'POST'])
def movimientos_por_fecha():
    if request.method == 'POST':
        fecha = request.form['fecha']
        try:
            query = """
                SELECT 
                    m.id, m.id_mov, m.rut, m.puntos, m.tipo_mov, m.fecha_creacion, m.fecha_mov,
                    s.nombre AS sucursal, tm.nombre AS mesa, bh.nombre AS bloque_horario
                FROM 
                    movimientos m
                LEFT JOIN 
                    sucursales s ON m.id_sucursal = s.id
                LEFT JOIN 
                    tipos_mesa tm ON m.id_mesa = tm.id
                LEFT JOIN 
                    bloques_horas bh ON m.id_bloque_horario = bh.id
                WHERE 
                    DATE(m.fecha_mov) = %s
                ORDER BY 
                    m.fecha_mov
            """
            values = (fecha,)
            cursor.execute(query, values)
            movimientos = cursor.fetchall()
            return render_template('movimientos_por_fecha.html', movimientos=movimientos)
        except Exception as e:
            print(f"Error fetching movimientos: {e}")
            return 'Error fetching movimientos, please try again'
    return render_template('movimientos_por_fecha.html')

if __name__ == '__main__':
    app.run(debug=True)
