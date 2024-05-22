
DROP DATABASE IF EXISTS spuntos;


-- Create the new database
CREATE DATABASE IF NOT EXISTS spuntos;

-- Use the new database
USE spuntos;

-- Create user_login table
CREATE TABLE IF NOT EXISTS user_login (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    clave VARCHAR(100) NOT NULL,
    rut VARCHAR(50) UNIQUE
);

-- Insert example data into user_login
INSERT INTO user_login (username, clave, rut)
VALUES ('francis', '006900', '15542970-4');

-- Create clients table
CREATE TABLE IF NOT EXISTS clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rut VARCHAR(20) UNIQUE,
    nombre VARCHAR(255),
    apellido VARCHAR(255),
    puntos INT,
    email VARCHAR(255),
    celular VARCHAR(20),
    comuna VARCHAR(255),
    ciudad VARCHAR(255),
    CONSTRAINT chk_rut_length CHECK (LENGTH(rut) >= 8),
    CONSTRAINT chk_celular_format CHECK (celular REGEXP '^9[0-9]{8}$')
);

-- Insert example data into clients
INSERT INTO clients (rut, nombre, apellido, puntos, email, celular, comuna, ciudad)
VALUES ('15542970-4', 'Francisco', 'Rojas', 10000, 'arojas.francisco@gmail.com', '992467200', 'Puente Alto', 'Santiago');

-- Create tipos_mesa table
CREATE TABLE IF NOT EXISTS tipos_mesa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255),
    tamano VARCHAR(50),
    cantidad INT
);

-- Insert example data into tipos_mesa
INSERT INTO tipos_mesa (nombre, tamano, cantidad)
VALUES ('Mesa grande', '120 * 180', 9),
       ('Mesa pequeña x 2', '120 * 180', 4),
       ('Mesa pequeña', '60 * 180', 4);

-- Create sucursales table
CREATE TABLE IF NOT EXISTS sucursales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255),
    direccion VARCHAR(255),
    comuna VARCHAR(100),
    ciudad VARCHAR(100),
    telefono VARCHAR(20),
    apertura VARCHAR(10),
    cierre VARCHAR(10)
);

-- Insert example data into sucursales
INSERT INTO sucursales (nombre, direccion, comuna, ciudad, telefono, apertura, cierre)
VALUES ('Manuel Montt', 'Dr Barros Borgono 160', 'Providencia', 'Santiago', '+56 (2) 2951 2373', '12:00', '21:00');

-- Create mesas_sucursal table
CREATE TABLE IF NOT EXISTS mesas_sucursal (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_sucursal INT,
    id_mesa INT,
    stock_mesas INT,
    FOREIGN KEY (id_sucursal) REFERENCES sucursales(id),
    FOREIGN KEY (id_mesa) REFERENCES tipos_mesa(id)
);

-- Create tipos_juego table
CREATE TABLE IF NOT EXISTS tipos_juego (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255)
);

-- Insert example data into tipos_juego
INSERT INTO tipos_juego (nombre) VALUES
('Warhammer 40k'),
('Age of Sigmar'),
('Bolt Action'),
('Horus Heresy'),
('Star Wars Legion'),
('Kill Team'),
('Warcry'),
('SW Shatterpoint');

-- Create bloques_horas table
CREATE TABLE IF NOT EXISTS bloques_horas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255),
    cant_horas INT,
    semana VARCHAR(255),
    fdsemana VARCHAR(255)
);

-- Insert example data into bloques_horas
INSERT INTO bloques_horas (nombre, cant_horas, semana, fdsemana) VALUES
('Bloque 1', 4, '12:00-16:00', '10:00-14:00'),
('Bloque 2', 4, '16:00-20:00', '15:00-19:00');

-- Create hist_descuentos table
CREATE TABLE IF NOT EXISTS hist_descuentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rut VARCHAR(20),
    id_mov VARCHAR(255),
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rut) REFERENCES clients(rut)
);

-- Create hist_arriendo table
CREATE TABLE IF NOT EXISTS hist_arriendo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rut VARCHAR(20),
    id_mov VARCHAR(255),
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_arriendo DATE NOT NULL,
    id_sucursal INT,
    id_mesa INT,
    id_bloque_horario INT,
    FOREIGN KEY (rut) REFERENCES clients(rut),
    FOREIGN KEY (id_sucursal) REFERENCES sucursales(id),
    FOREIGN KEY (id_mesa) REFERENCES tipos_mesa(id),
    FOREIGN KEY (id_bloque_horario) REFERENCES bloques_horas(id)
);

-- Create movimientos table
CREATE TABLE IF NOT EXISTS movimientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_mov VARCHAR(255),
    rut VARCHAR(20),
    puntos INT,
    tipo_mov VARCHAR(50),
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_mov DATE,
    id_sucursal INT,
    id_mesa INT,
    id_bloque_horario INT,
    FOREIGN KEY (rut) REFERENCES clients(rut),
    FOREIGN KEY (id_sucursal) REFERENCES sucursales(id),
    FOREIGN KEY (id_mesa) REFERENCES tipos_mesa(id),
    FOREIGN KEY (id_bloque_horario) REFERENCES bloques_horas(id)
);

-- Create stock_mesas table
CREATE TABLE IF NOT EXISTS stock_mesas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sucursal_id INT,
    mesa_id INT,
    bloque_horario_id INT,
    stock_disponible INT,
    stock_maximo INT,
    fecha DATE,
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id),
    FOREIGN KEY (mesa_id) REFERENCES tipos_mesa(id),
    FOREIGN KEY (bloque_horario_id) REFERENCES bloques_horas(id)
);

-- Create admins table
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(50) UNIQUE,
    clave VARCHAR(50),
    rut VARCHAR(20),
    CONSTRAINT email_format CHECK (email REGEXP '^[^@]+@[^@]+\.[^@]+$')
);

-- Insert example data into admins
INSERT INTO admins (email, clave, rut) VALUES
('francisco@wargaming.cl', 'admin', '155429704');

-- Sample insert into movimientos table
INSERT INTO movimientos (id_mov, rut, puntos, tipo_mov, fecha_mov, id_sucursal, id_mesa, id_bloque_horario) 
VALUES ('arrTRs', '15542970-4', 100, 'arriendo mesa', '2024-05-24', 1, 1, 1);
