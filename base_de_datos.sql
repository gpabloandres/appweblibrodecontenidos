-- Script para inicializar la base de datos SQLite

CREATE TABLE IF NOT EXISTS registro_clase (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dia TEXT NOT NULL,
    mes TEXT NOT NULL,
    clase_nro TEXT NOT NULL,
    unidad_nro TEXT,
    caracter_clase TEXT,
    contenidos TEXT NOT NULL,
    actividades TEXT,
    observaciones TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ejemplo de inserción de datos (opcional, para prueba)
INSERT INTO registro_clase (dia, mes, clase_nro, unidad_nro, caracter_clase, contenidos, actividades, observaciones)
VALUES ('05', '03', '01', '1', 'Introductoria', 'Introducción. Pautas y metodología de trabajo.', 'Presentación de herramientas.', '');
