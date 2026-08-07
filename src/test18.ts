async function test() {
  try {
     const response = await fetch('https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.QWEN_API_KEY}`,
          'X-DashScope-Async': 'enable'
        },
        body: JSON.stringify({
          model: 'wan2.1-t2i-turbo',
          input: { prompt: 'Un chat' },
          parameters: { n: 1, size: '1024*1024' }
        })
     });
     console.log(await response.json());
  } catch(e) {}
}
test();
