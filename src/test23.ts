async function test() {
  const res = await fetch('https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/image-generation/generation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.QWEN_API_KEY}`,
        'X-DashScope-Async': 'enable'
      },
      body: JSON.stringify({
        model: 'qwen-image-2.0',
        input: { prompt: 'Un chat' },
        parameters: { n: 1, size: '1024*1024' }
      })
  });
  console.log(await res.text());
}
test();
