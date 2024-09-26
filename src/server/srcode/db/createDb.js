import path from 'path';
import fs from 'fs/promises';
import pool from '../dbConnect.js';

// Helper function to get the directory name of the current module
const getDirname = (url) => path.dirname(new URL(url).pathname);

const createDataBase = async () => {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    // Read SQL file
    const sqlPath = path.join(getDirname(import.meta.url), 'schema.sql');
    console.log('Reading schema from:', sqlPath);

    const sql = await fs.readFile(sqlPath, 'utf8');
    console.log('Executing SQL script:', sql);

    // Execute SQL script
    await client.query(sql);

    await client.query('COMMIT');
    console.log('Schema setup complete!');
  } catch (err) {
    await client.query('ROLLBACK');
    console.error('Error executing SQL script:', err);
  } finally {
    client.release();
  }
};

export default createDataBase;