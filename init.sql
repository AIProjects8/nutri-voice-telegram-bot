CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    telegram_id BIGINT CHECK (telegram_id >= 1000000000),
    name VARCHAR(255),
    date_of_birth DATE,
    weight INTEGER,
    sex VARCHAR(50)
); 