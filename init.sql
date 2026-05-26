CREATE TABLE IF NOT EXISTS reservas (
    id SERIAL PRIMARY KEY,
    sala VARCHAR(50) NOT NULL,
    data_reserva VARCHAR(10) NOT NULL,
    hora_reserva VARCHAR(5) NOT NULL,
    UNIQUE (sala, data_reserva, hora_reserva) -- Garante que o BD também não aceite duplicatas
);