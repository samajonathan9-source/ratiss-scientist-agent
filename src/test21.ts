async function test() {
  const ep = 'https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/text-to-image/image-synthesis';
  const res = await fetch(ep, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.QWEN_API_KEY}`,
      'X-DashScope-Async': 'enable'
    },
    body: JSON.stringify({
      model: 'wan2.7-image',
      input: { prompt: 'Un chat' },
      parameters: { n: 1, size: '1024*1024' }
    })
  });
  console.log(await res.text());
}
test();
