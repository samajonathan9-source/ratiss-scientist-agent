async function test() {
  const res = await fetch('https://dashscope.aliyuncs.com/compatible-mode/v1/images/generations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer fake_key` },
    body: JSON.stringify({
      model: "qwen-image-2.0",
      prompt: 'Un chat'
    })
  });
  console.log(res.status, await res.text());
}
test();
