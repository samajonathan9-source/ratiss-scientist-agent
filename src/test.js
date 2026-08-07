const fetch = require('node-fetch');

async function test() {
  const response = await fetch('http://localhost:3000/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages: [{ role: 'user', content: 'Générer une image de chat' }],
      mode: 'Standard (N1)'
    })
  });
  const data = await response.json();
  console.log(data);
}
test();
