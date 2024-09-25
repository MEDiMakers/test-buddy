import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import mysql from 'mysql2/promise';

const app = express();
const port = 3000;

app.use(cors({ origin: 'http://localhost:5173' }));

// Create a MySQL connection pool
const pool = mysql.createPool({
  host: process.env.DB_URL,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_DATABASE,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

// testing db connection
const testConnection = async () => {
  try {
    const connection = await pool.getConnection();
    console.log('Database connection successful');
    connection.release();
  } catch (error) {
    console.error('Database connection failed:', error);
  }
};

// create the table if it doesnt exist and populate it with sample data
const initializeDatabase = async () => {
  try {
    const connection = await pool.getConnection();

    // create the table if it doesnt exist
    const createTableQuery = `
      CREATE TABLE IF NOT EXISTS sample_texts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        text VARCHAR(255) NOT NULL
      );
    `;
    await connection.query(createTableQuery);
    console.log('Table "sample_texts" is ready.');

    // check if table empty
    const [rows] = await connection.query('SELECT COUNT(*) AS count FROM sample_texts');
    if (rows[0].count === 0) {
      // if empty populate with sample data (always does this for now)
      const insertSampleData = `
        INSERT INTO sample_texts (text)
        VALUES ('Hello, world!'),
               ('Sample text 1'),
               ('Sample text 2'),
               ('This is a test text'),
               ('Random text for testing');
      `;
      await connection.query(insertSampleData);
      console.log('Inserted sample texts into "sample_texts" table.');
    }

    connection.release();
  } catch (error) {
    console.error('Database initialization failed:', error);
  }
};

//test first to see if my shit crashes
testConnection();
initializeDatabase();

app.get('/', (req, res) => {
  res.send('Welcome to the backend!');
});

app.get('/api/get-text', async (req, res) => {
  try {
    const [rows] = await pool.query('SELECT text FROM sample_texts ORDER BY RAND() LIMIT 1');
    if (rows.length > 0) {
      res.json({ text: rows[0].text });
    } else {
      res.json({ text: 'No text available' });
    }
  } catch (error) {
    console.error('Database query error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.listen(port, () => {
  console.log(`Backend is running at http://localhost:${port}`);
});
