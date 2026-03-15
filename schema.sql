-- Create database
CREATE DATABASE IF NOT EXISTS p2p_notes;
USE p2p_notes;

-- Drop tables if they exist to apply new schema
DROP TABLE IF EXISTS downloads;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS notes;
DROP TABLE IF EXISTS users;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    branch VARCHAR(50),
    year INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notes table
CREATE TABLE IF NOT EXISTS notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    description TEXT,
    branch VARCHAR(50),
    semester VARCHAR(10),
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    download_count INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Downloads table (Optional: tracking who downloaded what)
CREATE TABLE IF NOT EXISTS downloads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    note_id INT NOT NULL,
    user_id INT NOT NULL,
    download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    note_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Sample Data
-- Passwords should be hashed using werkzeug.security.generate_password_hash. 
-- For demo purposes, the plaintext is given in comments.
-- Password 'password123' hashed (example only, actual hashes will vary)
INSERT INTO users (name, email, password_hash, branch, year) VALUES 
('Alice Smith', 'alice@college.edu', 'scrypt:32768:8:1$Cq7a8q9C$889e4c194689b093375815616dc31d77a28e83be602b9370007817e089d81d520379def286f9ee19f4a62e3d30b9101b05807afb248a3ed444d320475af317ca', 'Computer Science', 3),
('Bob Jones', 'bob@college.edu', 'scrypt:32768:8:1$Cq7a8q9C$889e4c194689b093375815616dc31d77a28e83be602b9370007817e089d81d520379def286f9ee19f4a62e3d30b9101b05807afb248a3ed444d320475af317ca', 'Information Technology', 2);

-- Assuming file is stored somewhere like 'static/uploads/sample.pdf'
INSERT INTO notes (user_id, title, subject, description, branch, semester, file_name, file_path, file_hash) VALUES 
(1, 'OS Chapter 1-3 Notes', 'Operating Systems', 'Detailed notes on processes and threads', 'Computer Science', '3-1', 'OS_Notes_Ch1_3.pdf', 'static/uploads/OS_Notes_Ch1_3.pdf', 'dummy_hash_1'),
(2, 'DBMS ER Diagrams', 'Database Management', 'Examples of ER diagrams with solutions', 'Information Technology', '2-2', 'DBMS_ER.pdf', 'static/uploads/DBMS_ER.pdf', 'dummy_hash_2');
