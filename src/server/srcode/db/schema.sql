-- schema.sql

-- Create Users Table
CREATE TABLE IF NOT EXISTS Users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    -- email VARCHAR(255) UNIQUE NOT NULL,
    -- password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Chats Table
CREATE TABLE IF NOT EXISTS Chats (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES Users(id) ON DELETE CASCADE,
    scores FLOAT[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chats_user_id ON Chats(user_id);

-- Create TestBlocks Table
CREATE TABLE IF NOT EXISTS TestBlocks (
    id SERIAL PRIMARY KEY,
    chat_id INT REFERENCES Chats(id) ON DELETE CASCADE,
    prompt TEXT NOT NULL,
    response TEXT DEFAULT NULL,
    score FLOAT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_testblocks_chat_id ON TestBlocks(chat_id);