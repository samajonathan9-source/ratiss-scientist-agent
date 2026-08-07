import dotenv from 'dotenv';
dotenv.config();

export const config = {
    port: process.env.PORT || 3001,
    openRouterKey: process.env.OPENROUTER_API_KEY,
    defaultModel: 'google/gemma-4-26b-a4b-it:free'
};
