async function test() {
  const eps = [
    'https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/text2image/generation',
    'https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/image-synthesis/generation',
    'https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/image-generation/generation',
    'https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/wanx/image-synthesis',
    'https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/images/generations',
    'https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis'
  ];

  for (const ep of eps) {
    console.log(ep);
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
}
test();
