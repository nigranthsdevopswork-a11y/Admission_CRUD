-- Initialize admission_db
CREATE DATABASE IF NOT EXISTS admission_db;
USE admission_db;

-- Grant privileges
GRANT ALL PRIVILEGES ON admission_db.* TO 'root'@'%' IDENTIFIED BY 'redhat';
FLUSH PRIVILEGES;
