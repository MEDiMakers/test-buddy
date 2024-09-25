import express from 'express';
import dotenv from 'dotenv';
import pool from '../dbConnect.js';
import fetchUserId from '../fetchUserId.js';

const router = express.Router();
dotenv.config();

router.get('/:username/new', async (req, res) => {
    const { username } = req.params;
    try {

        const userId = await fetchUserId(username);

        //Create Chat and obtain Chat ID
        const createChatQuery = `
        INSERT INTO Chats (user_id)
        VALUES ($1)
        RETURNING id, user_id, scores, created_at;
    `;
        const chatResult = await pool.query(createChatQuery, [userId]);
        const chatId = chatResult.rows[0].id;

        //TO DO: Link to the Question Bank
        const prompt = 'This is a sample prompt! Is it working? :))';

        //Create TestBlock and obtain TestBlock ID
        const createTestBlockQuery = `
            INSERT INTO TestBlocks (chat_id, prompt)
            VALUES ($1, $2)
            RETURNING id, chat_id, prompt, response, score, created_at;
        `;
        const testBlockResult = await pool.query(createTestBlockQuery, [chatId, prompt]);

        // Send testBlockID and prompt as response
        res.status(201).json({
            success: true,
            prompt: prompt,
            testBlockID: testBlockResult.rows[0].id
        })
    } catch (error) {
        console.error('Error creating chat:', error.message);
        res.status(500).json({
            success: false,
            message: 'Server error'
        });
    }
});

router.get('/fetch/all/:username', async (req, res) => {
    const { username } = req.params;

    try {
        const userId = await fetchUserId(username);

        const fetchChatQuery = `
        SELECT * 
        FROM Chats 
        WHERE user_id = $1;`
        ;

        const chatResult = await pool.query(fetchChatQuery, [userId]);

        res.status(201).json({
            success: true,
            result: chatResult.rows
        })

    } catch (error) {
        console.error('Error fetching chats:', error.message);
        res.status(500).json({
            success: false,
            message: 'Server error'
        });
    }
});  

export default router;