-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255),
    verification_expires TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create email_verification_tokens table
CREATE TABLE IF NOT EXISTS email_verification_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create password_reset_tokens table
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_verification_tokens ON email_verification_tokens(token);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens ON password_reset_tokens(token);
CREATE INDEX IF NOT EXISTS idx_user_sessions ON user_sessions(session_token);

-- Insert admin user (password: admin123)
-- Hash generated with bcrypt for 'admin123'
INSERT INTO users (username, email, password_hash, is_verified, is_active) 
VALUES ('admin', 'admin@example.com', '$2b$12$MoFOR7EzFoBpBwrSjwjNaOF/U4pJqhhsKCFzIKaHJFWLiG5F8aEj6', TRUE, TRUE)
ON CONFLICT (username) DO NOTHING;

-- Insert a test user (password: test123)
-- Hash generated with bcrypt for 'test123'
INSERT INTO users (username, email, password_hash, is_verified, is_active) 
VALUES ('testuser', 'test@example.com', '$2b$12$qdy3UQcWFXSRlM7gYbnLaOw/q50Jl0lhj5Ymyhp1D74h7a24xQ/vu', TRUE, TRUE)
ON CONFLICT (username) DO NOTHING;
