// python_backend/userDatabase/userDatabase.js

const sqlite3 = require('sqlite3').verbose();
const path   = require('path');
const { app } = require('electron');

// Decide where the .db lives:
// - in development it sits next to this JS file
// - once packaged, we copy only the .db into resources/python_backend/userDatabase/
const dbFile = app.isPackaged
  ? path.join(process.resourcesPath, 'python_backend', 'userDatabase', 'users.db')
  : path.join(__dirname, 'users.db');

const db = new sqlite3.Database(dbFile, err => {
  if (err) console.error('Could not connect to database', err);
});

function initializeDatabase() {
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL
    )
  `, err => {
    if (err) console.error('Error creating users table', err);
  });
}

function getUserByUsername(username, callback) {
  db.get(
    `SELECT * FROM users WHERE username = ?`,
    [username],
    (err, row) => callback(err, row)
  );
}

initializeDatabase();

module.exports = { getUserByUsername };