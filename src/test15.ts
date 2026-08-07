async function test() {
  const response = await fetch('https://www.alibabacloud.com/help/en/model-studio/error-code');
  const text = await response.text();
  const match = text.match(/.{0,200}url error.{0,200}/gi);
  console.log(match);
}
test();
