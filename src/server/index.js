import express from 'express';
import userRoutes from './routes/userRoutes.js';
import chatRoutes from './routes/chatRoutes.js';
import testBlockRoutes from './routes/testBlockRoutes.js';
import devRoutes from './routes/devRoutes.js';

const app = express();
const port = 3000;

// Use express.json() middleware
app.use(express.json());

app.use('/user', userRoutes);
app.use('/chat', chatRoutes);
app.use('/testBlock', testBlockRoutes);
app.use('/dev', devRoutes);



app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});