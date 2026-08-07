import * as fs from 'fs';
import * as path from 'path';
import * as https from 'https';
import { URL } from 'url';

const testUrl = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx.json";
const dest = path.join(process.cwd(), 'bin', 'piper', 'voices', 'fr_FR-siwis-low.onnx.json');

function downloadFile(urlStr: string, destPath: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(urlStr);
    const options: https.RequestOptions = {
      hostname: parsedUrl.hostname,
      path: parsedUrl.pathname + parsedUrl.search,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      }
    };

    const request = https.get(options, (response) => {
      console.log(`URL: ${urlStr} - Status: ${response.statusCode}`);
      
      if ([301, 302, 307, 308].includes(response.statusCode || 0)) {
        const redirectUrl = response.headers.location;
        if (!redirectUrl) {
          reject(new Error(`Redirect response missing location header for: ${urlStr}`));
          return;
        }
        console.log(`Redirecting to: ${redirectUrl}`);
        downloadFile(redirectUrl, destPath).then(resolve).catch(reject);
        return;
      }

      if (response.statusCode !== 200) {
        reject(new Error(`Failed to download: HTTP ${response.statusCode}`));
        return;
      }

      const file = fs.createWriteStream(destPath);
      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve();
      });
    });

    request.on('error', (err) => {
      reject(err);
    });
  });
}

async function run() {
  try {
    console.log("Starting test download...");
    await downloadFile(testUrl, dest);
    console.log("Test download succeeded! File size:", fs.statSync(dest).size);
  } catch (err) {
    console.error("Test download failed:", err);
  }
}

run();
