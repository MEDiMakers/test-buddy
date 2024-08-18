import pool from "../dbConnect.js";
/**
 * Drops all tables in the current database.
 */
async function dropAllTables() {
  try {
    const client = await pool.connect();
    
    // Get a list of all tables in the current database
    const result = await client.query(`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = 'public';`); // Change 'public' if your tables are in a different schema

    // Drop each table
    for (const row of result.rows) {
      const tableName = row.table_name;
      await client.query(`DROP TABLE IF EXISTS ${tableName} CASCADE`);
      console.log(`Table ${tableName} dropped successfully.`);
    }

    client.release();
  } catch (error) {
    console.error('Error dropping tables:', error);
    throw new Error('Error dropping tables.');
  }
}

export default dropAllTables;