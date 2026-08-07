async function test() {
  const url = 'https://www.alibabacloud.com/help/en/model-studio/developer-reference/use-qwen-by-calling-api';
  const response = await fetch(url);
  const text = await response.text();
  const match = text.match(/.{0,200}qwen-image.{0,200}/gi);
  console.log(match);
}
test();
