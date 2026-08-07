async function test() {
  const response = await fetch('https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.QWEN_API_KEY}`,
      'X-DashScope-Async': 'enable'
    },
    body: JSON.stringify({
      model: 'wanx-v1',
      input: { prompt: 'Un chat' },
      parameters: { n: 1, size: '1024*1024' }
    })
  });
  console.log(response.status);
  console.log(await response.json());
}
test();
