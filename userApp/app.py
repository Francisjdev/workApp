
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, json
import mysql.connector
import smtplib
from datetime import datetime, timezone,timedelta
import re
import random
import string
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management


# MySQL connection
db = mysql.connector.connect(
      host="localhost",
    user="newuser",
    password="cnps10",
    database="spuntos",
    auth_plugin='mysql_native_password'
)
cursor = db.cursor()

# Email configuration
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_username = 'arojas.francisco@gmail.com'
smtp_password = 'ggvm azjj vycm bnyk'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username'].strip()  # Remove leading and trailing spaces
    password = request.form['password'].strip()  # Remove leading and trailing spaces

    # Query to check if username and password match in the user_login table
    query = "SELECT * FROM user_login WHERE username = %s AND clave = %s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    if user:
        # Set session data
        session['username'] = username
        session['rut'] = user[3]  # Assuming rut is in the second column of the user_login table
        return redirect(url_for('user_panel'))
    else:
        # Redirect back to login page with an error message
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    # Redirect to the login page or any other page you prefer
    return redirect(url_for('index'))
@app.route('/user_panel')
def user_panel():
    if 'username' in session:
        username = session['username']

        # Fetch user rut
        query_rut = "SELECT rut FROM user_login WHERE username = %s"
        cursor.execute(query_rut, (username,))
        rut = cursor.fetchone()[0]

        # Fetch user information
        query_info = "SELECT nombre, apellido, rut, email, puntos FROM clients WHERE rut = %s"
        cursor.execute(query_info, (rut,))
        user_info = cursor.fetchone()

        # Fetch user movements ordered by date
        query_movimientos = """
            SELECT m.tipo_mov, m.puntos, m.fecha_mov, m.id_mov, bh.nombre AS hora, tm.nombre AS mesa, s.nombre AS sucursal
            FROM movimientos m
            LEFT JOIN bloques_horas bh ON m.id_bloque_horario = bh.id
            LEFT JOIN tipos_mesa tm ON m.id_mesa = tm.id
            LEFT JOIN sucursales s ON m.id_sucursal = s.id
            WHERE m.rut = %s
            ORDER BY m.fecha_mov
        """
        cursor.execute(query_movimientos, (rut,))
        user_movimientos = cursor.fetchall()

        # Format user movements
        combined_data = []
        for movimiento in user_movimientos:
            combined_data.append({
                'tipo_mov': movimiento[0],
                'puntos': str(movimiento[1]),
                'fecha_mov': movimiento[2],
                'id_mov': movimiento[3],
                'hora': movimiento[4] if movimiento[4] else None,
                'mesa': movimiento[5] if movimiento[5] else None,
                'sucursal': movimiento[6] if movimiento[6] else None
            })

        # Fetch sum of points from movimientos table
        query_sum_movimientos = "SELECT SUM(puntos) FROM movimientos WHERE rut = %s"
        cursor.execute(query_sum_movimientos, (rut,))
        sum_movimientos = cursor.fetchone()[0] or 0

        # Calculate remaining points
        remaining_points = user_info[4] - sum_movimientos

        return render_template('user_panel.html', user_info=user_info, combined_data=combined_data, remaining_points=remaining_points)
    else:
        return redirect(url_for('index'))




@app.route('/arriendo')
def arriendo():
    # Here, you can add any necessary logic before rendering the template
    return render_template('arriendo.html')

@app.route('/home')
def home():
    # Here, you can add any necessary logic before rendering the template
     return redirect(url_for('user_panel'))


@app.route('/arrendar_mesa', methods=['POST'])
def arrendar_mesa():
    # Get data from the request
    rut = session.get('rut')
    if not rut:
        return jsonify({'error': 'Rut not found in session'}), 400

    fecha_arriendo = request.form['fecha_arriendo']
    bloque_horario = request.form['hora']
    sucursal = request.form['sucursal']
    mesa = request.form['mesas']
        # Remove time from fecha_arriendo
    fecha_arriendo = datetime.strptime(fecha_arriendo, '%Y-%m-%d').date()
    
    # Generate a random id_movimiento (arr + 3 random letters)
    id_movimiento = 'arr' + ''.join(random.choices(string.ascii_letters, k=3))
    
    try:
        # Insert data into the movimientos table
        insert_movimientos_query = "INSERT INTO movimientos (rut, tipo_mov, puntos, fecha_mov, id_mov) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_movimientos_query, (rut, 'arrendar', 100, fecha_arriendo, id_movimiento))
        
        # Insert data into the hist_arriendo table
        insert_hist_arriendo_query = "INSERT INTO hist_arriendo (rut, id_mov, fecha_arriendo,id_sucursal, id_mesa, id_bloque_horario) VALUES (%s, %s, %s,%s, %s, %s)"
        cursor.execute(insert_hist_arriendo_query, (rut, id_movimiento, fecha_arriendo,sucursal,mesa,bloque_horario))
        
        # Update stock_mesas table
        update_stock_query = "UPDATE stock_mesas SET stock_disponible = stock_disponible - 1 WHERE fecha = %s AND bloque_horario_id = %s AND sucursal_id = %s"
        cursor.execute(update_stock_query, (fecha_arriendo, bloque_horario, sucursal))
        db.commit()  # Commit the transaction
        
        # Redirect the user to the user_panel route
        return redirect(url_for('user_panel'))

    except mysql.connector.Error as err:
        # Handle MySQL errors
        return jsonify({'error': str(err)}), 500


@app.route('/cancelar', methods=['POST'])
def cancelar():
    try:
        # Get the data sent in the POST request
        data = request.get_json()

        # Extract the id_movimiento and rut from the JSON data
        id_movimiento = data.get('id')
        rut = data.get('rut')

        logging.info(f"Received cancelar request: id_movimiento={id_movimiento}, rut={rut}")

        # Query to fetch the necessary data from the movimientos table
        select_query = """
            SELECT fecha_mov, id_bloque_horario, id_sucursal, id_mesa
            FROM movimientos
            WHERE id_mov = %s AND rut = %s
        """
        cursor.execute(select_query, (id_movimiento, rut))
        movimiento_data = cursor.fetchone()

        if movimiento_data:
            # Extract data from the fetched row
            fecha_mov, bloque_horario, sucursal, mesa = movimiento_data
            logging.info(f"Fetched movimiento data: fecha_mov={fecha_mov}, bloque_horario={bloque_horario}, sucursal={sucursal}, mesa={mesa}")

            # Query to delete the entry from the movimientos table based on id_movimiento and rut
            delete_query = "DELETE FROM movimientos WHERE id_mov = %s AND rut = %s"
            cursor.execute(delete_query, (id_movimiento, rut))
            logging.info(f"Deleted from movimientos: id_movimiento={id_movimiento}, rut={rut}")

            # Update the stock_mesas table
            update_stock_query = """
                UPDATE stock_mesas
                SET stock_disponible = stock_disponible + 1
                WHERE fecha = %s AND bloque_horario_id = %s AND sucursal_id = %s AND mesa_id = %s
            """
            cursor.execute(update_stock_query, (fecha_mov, bloque_horario, sucursal, mesa))
            logging.info(f"Updated stock_mesas: fecha_mov={fecha_mov}, bloque_horario={bloque_horario}, sucursal={sucursal}, mesa={mesa}")

            db.commit()  # Commit the transaction

            return jsonify({'message': 'Entry deleted successfully'}), 200
        else:
            logging.error("Data not found in movimientos")
            return jsonify({'error': 'Data not found in movimientos'}), 404

    except Exception as e:
        # Log the error
        logging.exception("Error in cancelar route: %s", e)
        return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/get_juegos', methods=['GET'])
def get_juegos():
    # Query to fetch data from the tipos_juego table
    query_juegos = "SELECT id, nombre FROM tipos_juego"
    cursor.execute(query_juegos)
    juegos_data = cursor.fetchall()

    # Convert the data to a list of dictionaries for JSON serialization
    juegos_list = [{'id': juego[0], 'nombre': juego[1]} for juego in juegos_data]

    return jsonify({'juegos': juegos_list})

   # CHEQUEA DISPONIBILIDAD DE MESAS SEGUN FECHA
@app.route('/verificar_disponibilidad', methods=['POST'])
def verificar_disponibilidad():
    # Obtén los datos enviados desde el cliente
    data = request.json
    fecha = data.get('fecha')
    bloque_horario = data.get('bloqueHorario')  # Asegúrate de que coincida con el nombre en tu JavaScript

    # Realiza la consulta a la base de datos para verificar la disponibilidad de stock
    cursor = db.cursor()
    consulta = "SELECT stock_disponible FROM stock_mesas WHERE fecha = %s AND bloque_horario_id = %s"
    cursor.execute(consulta, (fecha, bloque_horario))
    resultado = cursor.fetchone()
    # Devuelve la respuesta al cliente
    if resultado:
        print(resultado[0])
        stock_disponible = resultado[0]
        return jsonify({'disponible': stock_disponible > 0})
    else:
        return jsonify({'disponible': False})





if __name__ == '__main__':
    app.run(debug=True)