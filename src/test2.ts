async function test() {
  const response = await fetch('https://dashscope-intl.aliyuncs.com/compatible-mode/v1/images/generations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${process.env.QWEN_API_KEY}` },
    body: JSON.stringify({
      model: "wanx-v1",
      prompt: 'Un chat'
    })
  });
  console.log(response.status);
  const text = await response.text();
  console.log(text);
}
test();
