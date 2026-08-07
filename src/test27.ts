async function test() {
  const initRes = await fetch("https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/image-generation/generation", {
    method: "POST",
    headers: {
      "X-DashScope-Async": "enable",
      "Authorization": `Bearer ${process.env.QWEN_API_KEY}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: "wan2.7-image",
      input: { messages: [{ role: 'user', content: 'Un chat' }] },
      parameters: { size: "1024*1024", n: 1 }
    })
  });
  const data = await initRes.json();
  console.log(data);
  const taskId = data.output.task_id;

  for (let i = 0; i < 5; i++) {
    await new Promise(r => setTimeout(r, 2000));
    const pollRes = await fetch(`https://dashscope-intl.aliyuncs.com/api/v1/tasks/${taskId}`, {
      headers: { "Authorization": `Bearer ${process.env.QWEN_API_KEY}` }
    });
    console.log(await pollRes.json());
  }
}
test();
