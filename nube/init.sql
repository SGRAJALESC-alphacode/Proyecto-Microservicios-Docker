CREATE TABLE IF NOT EXISTS mediciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ciudad VARCHAR(50) NOT NULL,
    temperatura FLOAT NOT NULL,
    humedad INT NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO mediciones (ciudad, temperatura, humedad) VALUES ('Manizales', 18.5, 80);
INSERT INTO mediciones (ciudad, temperatura, humedad) VALUES ('Bogota', 14.2, 75);
INSERT INTO mediciones (ciudad, temperatura, humedad) VALUES ('Medellin', 22.0, 65);
