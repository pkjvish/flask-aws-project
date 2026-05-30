-- init.sql: runs once after DB and user are created

CREATE TABLE IF NOT EXISTS tbl_user (
    user_id    INT AUTO_INCREMENT PRIMARY KEY,
    user_name  VARCHAR(100) NOT NULL,
    user_email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
