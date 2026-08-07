import express from 'express';
import cors from 'cors';
import { OpenAI } from 'openai';
import { config } from './config.js';
import { prepareMessages, verifyResponse } from './ratiss_mini_core.js';

const app = express();
app.use(cors());
app.use(express.json());

const openai = new OpenAI({
    baseURL: 'https://openrouter.ai/api/v1',
    apiKey: config.openRouterKey || 'dummy',
});

app.post('/api/chat', async (req, res) => {
    try {
        const { message } = req.body;
        if (!message) return res.status(400).json({ error: 'Message requis' });
        
        console.log(`[RATISS] Requête entrante : ${message.substring(0, 50)}...`);

        const messages = prepareMessages(message);

        const completion = await openai.chat.completions.create({
            model: config.defaultModel,
            messages: messages,
            max_tokens: 1000
        });

        let rawResponse = completion.choices[0]?.message?.content || "";
        
        // Post-verification (TopoZK simulé)
        const verifiedResponse = verifyResponse(message, rawResponse);
        const isProven = verifiedResponse === rawResponse;

        res.json({ 
            response: verifiedResponse,
            proof: isProven ? "ZK-CPU-PASSED" : "ZK-CPU-REJECTED"
        });

    } catch (error) {
        console.error('[RATISS ERROR]', error);
        res.status(500).json({ error: 'Erreur interne du moteur RATISS' });
    }
});

app.listen(config.port, () => {
    console.log(`[RATISS MINI CORE] Serveur démarré sur le port ${config.port}`);
});
