async function test() {
  const response = await fetch('http://localhost:3000/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages: [{ role: 'user', content: 'Générer une image de chat' }],
      mode: 'Standard (N1)'
    })
  });
  
  if (!response.ok) {
    const text = await response.text();
    console.error("HTTP Status:", response.status);
    console.error(text);
    return;
  }
  
  const data = await response.json();
  console.log(data);
}
test();
