import express from 'express';
const router = express.Router();

router.post('/:blockID/response'); 
//log response, send for similarity testing, log score in testBlock and Chat, conditionally create new TestBlock, return score, new prompt and new blockID

router.get('/fetch/:chatID')

export default router;