-- Database Schema for Mini Freelance Application
-- This is a reference file. The actual database is managed by SQLAlchemy in Python.

-- Users Table
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128),
    bio TEXT,
    location VARCHAR(100),
    skills VARCHAR(200),
    profile_pic VARCHAR(100) DEFAULT 'default.jpg',
    is_admin BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Jobs Table
CREATE TABLE job (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    budget FLOAT NOT NULL,
    status VARCHAR(20) DEFAULT 'open',
    poster_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (poster_id) REFERENCES user (id)
);

-- Applications Table
CREATE TABLE application (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    applicant_id INTEGER NOT NULL,
    cover_letter TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES job (id),
    FOREIGN KEY (applicant_id) REFERENCES user (id)
);

-- Messages Table
CREATE TABLE message (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    body TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT 0,
    FOREIGN KEY (sender_id) REFERENCES user (id),
    FOREIGN KEY (receiver_id) REFERENCES user (id)
);

-- Reviews Table
CREATE TABLE review (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reviewer_id INTEGER NOT NULL,
    reviewee_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    rating INTEGER NOT NULL,
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reviewer_id) REFERENCES user (id),
    FOREIGN KEY (reviewee_id) REFERENCES user (id),
    FOREIGN KEY (job_id) REFERENCES job (id)
);
