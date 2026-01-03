// MySQL database creation example

// First, connect to your MySQL server using a tool like the MySQL command line or phpMyAdmin.
// Then, run the following SQL commands:

/*
Create a database called 'mydatabase':
*/
CREATE DATABASE mydatabase;

/*
Switch to the new database:
*/
USE mydatabase;

/*
Create a sample table called 'users':
*/
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

// Now you have a MySQL database with a 'users' table!
/*
You can insert a test user like this:
INSERT INTO users (username, email) VALUES ('johndoe', 'john@example.com');
*/
