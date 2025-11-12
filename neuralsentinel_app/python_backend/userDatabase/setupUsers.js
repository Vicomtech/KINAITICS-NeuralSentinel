const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcryptjs');
const path = require('path');

const dbFile = path.join(__dirname, 'users.db');
const db = new sqlite3.Database(dbFile, (err) => {
  if (err) console.error('Error opening database:', err);
});

db.run(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
  )
`, (err) => {
  if (err) console.error('Error creating table:', err);
});

const users = [
  { username: 'user1', password: 'user1' },
  { username: 'user2', password: 'user2' },
  { username: 'user3', password: 'user3' }
];

// Insert default users with hashed passwords
function seedUsers() {
  users.forEach(user => {
    const hash = bcrypt.hashSync(user.password, 10);
    db.run(
      `INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)`,
      [user.username, hash],
      (err) => {
        if (err) console.error(`Error inserting ${user.username}:`, err);
      }
    );
  });
}

seedUsers();
db.close();