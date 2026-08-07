import OpenAI from 'openai';

async function test() {
  const openai = new OpenAI({
    apiKey: process.env.QWEN_API_KEY,
    baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1",
  });
  
  try {
    const response = await openai.images.generate({
      model: "qwen-image-2.0",
      prompt: "Un chat",
      n: 1,
      size: "1024x1024"
    });
    console.log(response);
  } catch (e) {
    console.log(e.status, e.message);
  }
}
test();
