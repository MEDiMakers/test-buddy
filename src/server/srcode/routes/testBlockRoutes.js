import express from 'express';
import pool from '../dbConnect.js';
import calculateSimilarityScore from '../calculateSimilarityScore.js';
const router = express.Router();

//Receives response from user, calculates score and conditionally produces new prompt
router.post('/:blockID/response', async (req, res) => {
    const { blockID } = req.params;
    const {prompt, answer} = req.body;

    console.log(blockID);

    if (!answer || answer == "") {
        res.status(400).json({
            success: false,
            message: "Response not specified"
        })
    }

    try {
        const similarityScore =  calculateSimilarityScore(prompt, answer);

        const updateTestBlockQuery = `
        UPDATE TestBlocks 
        SET response = $1 , score = $2
        WHERE id = $3
        RETURNING chat_id, prompt, response, score, created_at;
        `;

        const updateTestBlockResult = await pool.query(updateTestBlockQuery, [answer, similarityScore, blockID]);

        const updateChatQuery = `
        UPDATE Chats
        SET scores = array_append(scores, $1)
        WHERE id = $2
        RETURNING user_id, scores
        `;

        const updateChatResult = await pool.query(updateChatQuery, [similarityScore, updateTestBlockResult.rows[0].chat_id]);

        let goodAnswer = true;
        let newPrompt = null;
        let newBlockID = null;
        if (similarityScore < 5) {
            goodAnswer = false;

            //TO DO: Link to the LLM
            newPrompt = 'This is a sample follow-up! Is it working? :))';

            //Create TestBlock and obtain TestBlock ID
            const createTestBlockQuery = `
                INSERT INTO TestBlocks (chat_id, prompt)
                VALUES ($1, $2)
                RETURNING id, chat_id, prompt, response, score, created_at;
            `;
            const createTestBlockResult = await pool.query(createTestBlockQuery, [updateTestBlockResult.rows[0].chat_id, prompt]);
            newBlockID = createTestBlockResult.rows[0].id;
        }

        res.status(200).json({
            success: true,
            score: similarityScore,
            goodAnswer: goodAnswer,
            prompt: newPrompt,
            testBlockID: newBlockID
        })
    } catch (error) { //TODO: Make this robust
        console.log(error.message);
    }
}); 

router.get('/fetch/:chatID')

export default router;