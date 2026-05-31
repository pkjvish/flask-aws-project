-- init.sql: runs once after DB and user are created

CREATE TABLE IF NOT EXISTS tbl_user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(45) NOT NULL,
    user_email VARCHAR(45) NOT NULL UNIQUE
);

-- Insert sample data using the correct column names
INSERT INTO tbl_user (user_name, user_email) VALUES 
('Pankaj Kumar', 'pankaj@example.com'),
('Jane Doe', 'jane@example.com')
ON DUPLICATE KEY UPDATE user_name=VALUES(user_name);
