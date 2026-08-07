async function test() {
  const response = await fetch('https://www.alibabacloud.com/help/en/model-studio/error-code');
  const text = await response.text();
  console.log(text.substring(0, 1000));
}
test();
