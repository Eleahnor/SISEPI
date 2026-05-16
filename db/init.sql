CREATE TABLE IF NOT EXISTS casos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    edad INTEGER,
    sexo VARCHAR(10),
    municipio VARCHAR(50),
    enfermedad VARCHAR(50),
    tipo VARCHAR(20),
    estado VARCHAR(20),
    diag_date DATE DEFAULT CURRENT_DATE
);

INSERT INTO casos (nombre, edad, sexo, municipio, enfermedad, tipo, estado) VALUES
('Juan Pérez', 45, 'M', 'La Paz', 'Dengue', 'Confirmado', 'Activo'),
('María López', 32, 'F', 'Los Cabos', 'COVID-19', 'Sospechoso', 'Activo'),
('Carlos Ruiz', 58, 'M', 'Comondú', 'Zika', 'Confirmado', 'Recuperado'),
('Ana García', 27, 'F', 'La Paz', 'Dengue', 'Descartado', 'Recuperado'),
('Roberto Soto', 63, 'M', 'Mulegé', 'COVID-19', 'Confirmado', 'Fallecido'),
('Laura Méndez', 41, 'F', 'Loreto', 'Chikungunya', 'Confirmado', 'Activo')
ON CONFLICT DO NOTHING;