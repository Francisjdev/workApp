import mysql.connector
from datetime import datetime, timedelta

# Connect to your MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="newuser",
    password="cnps10",
    database="spuntos"
)
cursor = db.cursor()

# Define the data to insert
sucursal_id = 1
mesa_id = 2
stock_maximo = 4

# Insert data for bloque_horario_id 1
bloque_horario_id = 1
stock_disponible = 4  # Assuming initial stock is 8 for each day

# Generate dates for the month of May
start_date = datetime(2024, 5, 22)
end_date = datetime(2024, 7, 31)
delta = timedelta(days=1)
current_date = start_date

while current_date <= end_date:
    fecha = current_date.date()
    insert_query = """
    INSERT INTO stock_mesas (sucursal_id, mesa_id, bloque_horario_id, stock_disponible, stock_maximo, fecha)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (sucursal_id, mesa_id, bloque_horario_id, stock_disponible, stock_maximo, fecha))
    current_date += delta

# Insert data for bloque_horario_id 2
bloque_horario_id = 2

current_date = start_date
while current_date <= end_date:
    fecha = current_date.date()
    insert_query = """
    INSERT INTO stock_mesas (sucursal_id, mesa_id, bloque_horario_id, stock_disponible, stock_maximo, fecha)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (sucursal_id, mesa_id, bloque_horario_id, stock_disponible, stock_maximo, fecha))
    current_date += delta

# Commit changes and close connection
db.commit()
cursor.close()
db.close()