create database if not exists spuntos2;
use spuntos2;
CREATE TABLE if not exists user_login (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL unique,
    clave VARCHAR(100) NOT NULL,
    rut varchar(50) unique
);

INSERT INTO user_login (username, clave, rut)
VALUES ('francis', '006900', '15542970-4');



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
INSERT INTO clients (rut, nombre, apellido, puntos, email, celular, comuna, ciudad)
VALUES ('15542970-4', 'Francisco', 'Rojas', 10000, 'arojas.francisco@gmail.com', '992467200', 'Puente Alto', 'Santiago');


CREATE TABLE  if not exists tipos_mesa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255),
    tamano VARCHAR(50),
    cantidad INT
);

INSERT INTO tipos_mesa (nombre, tamano, cantidad)
VALUES ('Mesa grande', '120 * 180', 9),
       ('Mesa pequeña x 2', '120 * 180', 4),
       ('Mesa pequeña', '60 * 180', 8);

CREATE TABLE if not exists sucursales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255),
    direccion VARCHAR(255),
    comuna VARCHAR(100),
    ciudad VARCHAR(100),
    telefono VARCHAR(20),
    apertura VARCHAR(10),
    cierre VARCHAR(10)
);

INSERT INTO sucursales (nombre, direccion, comuna, ciudad, telefono, apertura, cierre)
VALUES ('Manuel Montt', 'Dr Barros Borgono 160', 'Providencia', 'Santiago', '+56 (2) 2951 2373', '12:00', '21:00');

CREATE TABLE if not exists Mesas_Sucursal (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_sucursal INT,
    id_mesa INT,
    stock_mesas INT,
    FOREIGN KEY (id_sucursal) REFERENCES sucursales(id),
    FOREIGN KEY (id_mesa) REFERENCES tipos_mesa(id)
);


CREATE TABLE if not exists  tipos_juego (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255)
);

INSERT INTO tipos_juego (nombre) VALUES
('Warhammer 40k'),
('Age of Sigmar'),
('Bolt Action'),
('Horus Heresy'),
('Star Wars Legion'),
('Kill Team'),
('Warcry'),
('SW Shatterpoint');

CREATE TABLE if not exists  bloques_horas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255),
    cant_horas int,
    semana VARCHAR(255),
    fdsemana VARCHAR(255)
);
INSERT INTO bloques_horas (nombre,cant_horas,semana,fdsemana) VALUES
("Bloque 1",4, "12:00-16:00","10:00-14:00"),
("Bloque 2",4, "16:00-20:00","15:00-19:00");

CREATE TABLE if not exists hist_descuentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rut VARCHAR(20),
    id_movimiento INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rut) REFERENCES clients(rut)
);

CREATE TABLE if not exists hist_arriendo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rut VARCHAR(20),
    id_mov varchar(255),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	fecha_arriendo datetime not null,
    FOREIGN KEY (rut) REFERENCES clients(rut)
); 



CREATE TABLE IF NOT EXISTS movimientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_mov VARCHAR(255),
    rut VARCHAR(20),
    puntos int,
    tipo_mov VARCHAR(50),
    fecha_mov TIMESTAMP,
    CONSTRAINT fk_client FOREIGN KEY (rut) REFERENCES clients(rut)
);

CREATE TABLE stock_mesas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sucursal_id INT,
    mesa_id INT,
    bloque_horario_id INT,
    stock_disponible INT,
    stock_maximo INT,
    fecha Date,
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id),
    FOREIGN KEY (mesa_id) REFERENCES tipos_mesa(id),
    FOREIGN KEY (bloque_horario_id) REFERENCES bloques_horas(id)
);

ALTER TABLE hist_arriendo
ADD COLUMN id_sucursal INT,
ADD COLUMN id_mesa INT,
ADD COLUMN id_bloque_horario INT;

select * from bloques_horas;  
 select * from stock_mesas;  
