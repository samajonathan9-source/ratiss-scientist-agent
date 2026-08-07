import * as fs from 'fs';
import * as path from 'path';
import * as https from 'https';

const voicesDir = path.join(process.cwd(), 'bin', 'piper', 'voices');

const jsonFiles = [
  {
    fileName: "fr_FR-siwis-low.onnx.json",
    url: "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx.json"
  },
  {
    fileName: "fr_FR-siwis-medium.onnx.json",
    url: "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json"
  },
  {
    fileName: "fr_FR-gilles-low.onnx.json",
    url: "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/gilles/low/fr_FR-gilles-low.onnx.json"
  },
  {
    fileName: "fr_FR-upmc-medium.onnx.json",
    url: "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx.json"
  }
];

const downloadFile = (url: string, dest: string): Promise<void> => {
  return new Promise((resolve, reject) => {
    const request = https.get(url, (response) => {
      if ([301, 302, 307, 308].includes(response.statusCode || 0)) {
        const redirectUrl = response.headers.location;
        if (!redirectUrl) {
          reject(new Error(`Redirect response missing location header for: ${url}`));
          return;
        }
        downloadFile(redirectUrl, dest).then(resolve).catch(reject);
        return;
      }
      if (response.statusCode !== 200) {
        reject(new Error(`Failed to download ${url}: HTTP ${response.statusCode}`));
        return;
      }
      
      const file = fs.createWriteStream(dest);
      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve();
      });
    });
    request.on('error', (err) => {
      if (fs.existsSync(dest)) fs.unlinkSync(dest);
      reject(err);
    });
  });
};

async function main() {
  console.log("Downloading tiny JSON config files...");
  for (const item of jsonFiles) {
    const dest = path.join(voicesDir, item.fileName);
    console.log(`Downloading ${item.fileName} from ${item.url}...`);
    try {
      await downloadFile(item.url, dest);
      console.log(`Success: ${item.fileName} downloaded. Size: ${fs.statSync(dest).size} bytes.`);
    } catch (err: any) {
      console.error(`Error downloading ${item.fileName}:`, err.message || err);
    }
  }
  console.log("Done!");
}

main();
