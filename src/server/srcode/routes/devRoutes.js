import express from 'express';
const router = express.Router();
import createDataBase from '../db/createDb.js';
import dropAllTables from '../db/deleteDb.js';

const resetMiddleware = (req, res, next) => {
    const { password } = req.headers;
    const correctPassword = process.env.DB_PASSWORD;
    console.log(password);
    if (password === correctPassword) {
        next();
    } else {
        res.status(403).json({ message: 'Forbidden: Invalid password' });
    }
};

router.get('/resetdb', resetMiddleware, async (req, res) => {
    try {
        await dropAllTables();
        await createDataBase();
        res.status(200).json({ message: 'Database successfully reset' });
    } catch (error) {
        console.error('Error resetting database:', error);
        res.status(500).json({ message: 'Could not reset database', error: error.message });
    }
});

export default router;