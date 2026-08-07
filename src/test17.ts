async function test() {
  const url = 'https://www.alibabacloud.com/help/en/model-studio/developer-reference/image-generation';
  let response = await fetch(url);
  if (!response.ok) {
     response = await fetch('https://www.alibabacloud.com/help/en/model-studio/developer-reference/wanx-image-generation');
  }
  const text = await response.text();
  console.log(text.match(/.{0,200}qwen-image.{0,200}/gi));
  console.log(text.match(/.{0,200}https:\/\/dashscope.{0,200}/gi));
}
test();
