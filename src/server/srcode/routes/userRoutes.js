import express from 'express';
import pool from '../dbConnect.js';
const router = express.Router();


//Creates new user
router.get('/create/:username', async (req, res) => {
    const { username } = req.params;

    try {
        // Insert a new user into the Users table
        const newUserQuery = `
            INSERT INTO Users (username)
            VALUES ($1)
            RETURNING id, username, created_at;
        `;
        const result = await pool.query(newUserQuery, [username]);

        // Send the newly created user data as a response
        res.status(201).json({
            success: true,
            user: result.rows[0]
        });
    } catch (error) {
        // Handle errors, such as if the username is not unique
        console.error('Error creating user:', error.message);
        if (error.code === '23505') { // Unique violation error code
            res.status(409).json({ success: false, message: 'Username already exists' });
        } else {
            res.status(500).json({ success: false, message: 'Server error' });
        }
    }
});

//Fetches user id for the given username
router.get('/fetchID/:username', async (req, res) => {
    const { username } = req.params;

    try {
        const fetchIdQuery = `
            SELECT id FROM Users WHERE username = $1;
        `;
        const result = await pool.query(fetchIdQuery, [username]);

        if (result.rows.length === 0) {
            return res.status(404).json({
                success: false,
                message: 'User not found'
            });
        }

        res.status(200).json({
            success: true,
            userId: result.rows[0].id
        });
    } catch (error) {
        console.error('Error fetching user ID:', error.message);
        res.status(500).json({
            success: false,
            message: error.message
        });
    }
});


export default router;