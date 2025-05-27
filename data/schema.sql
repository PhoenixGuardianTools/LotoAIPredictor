-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    surnom TEXT,
    email TEXT UNIQUE NOT NULL,
    civilite TEXT,
    telephone TEXT,
    newsletter BOOLEAN DEFAULT 0,
    code_parrain TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    config_hash TEXT,
    is_active BOOLEAN DEFAULT 1
);

-- Table des adresses
CREATE TABLE IF NOT EXISTS addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    type_voie TEXT,
    numero TEXT,
    bis_ter TEXT,
    voie TEXT,
    complement TEXT,
    code_postal TEXT,
    ville TEXT,
    pays TEXT DEFAULT 'France',
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Table des configurations SMTP
CREATE TABLE IF NOT EXISTS smtp_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,
    server TEXT NOT NULL,
    port INTEGER NOT NULL,
    ssl BOOLEAN DEFAULT 1,
    tls BOOLEAN DEFAULT 1
);

-- Table des codes postaux et villes
CREATE TABLE IF NOT EXISTS postal_codes (
    code_postal TEXT PRIMARY KEY,
    ville TEXT NOT NULL,
    departement TEXT,
    region TEXT
);

-- Table des configurations utilisateur
CREATE TABLE IF NOT EXISTS user_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    config_type TEXT NOT NULL, -- 'admin' ou 'client'
    config_path TEXT NOT NULL,
    config_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Table des logs de synchronisation
CREATE TABLE IF NOT EXISTS sync_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    sync_type TEXT NOT NULL,
    status TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Insertion des configurations SMTP par défaut
INSERT INTO smtp_configs (provider, server, port, ssl, tls) VALUES
('Gmail', 'smtp.gmail.com', 465, 1, 1),
('Outlook', 'smtp-mail.outlook.com', 587, 0, 1),
('Yahoo', 'smtp.mail.yahoo.com', 587, 0, 1),
('Riseup', 'mail.riseup.net', 465, 1, 1),
('ProtonMail', 'smtp.protonmail.ch', 587, 0, 1);

-- Index pour les recherches
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_postal_codes_code ON postal_codes(code_postal);
CREATE INDEX IF NOT EXISTS idx_user_configs_hash ON user_configs(config_hash); 