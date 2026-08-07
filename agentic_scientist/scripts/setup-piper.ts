import * as fs from 'fs';
import * as path from 'path';
import * as https from 'https';
import { execSync } from 'child_process';

const binDir = path.join(process.cwd(), 'bin');
const piperBin = path.join(binDir, 'piper', 'piper');
const voicesDir = path.join(binDir, 'piper', 'voices');

const AVAILABLE_VOICES = [
  {
    id: "fr_FR-siwis-low",
    onnxUrl: "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx",
    jsonUrl: "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx.json",
    fileName: "fr_FR-siwis-low.onnx"
  },
  {
    id: "fr_FR-siwis-medium",
    onnxUrl: "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx",
    jsonUrl: "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json",
    fileName: "fr_FR-siwis-medium.onnx"
  },
  {
    id: "fr_FR-gilles-low",
    onnxUrl: "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/gilles/low/fr_FR-gilles-low.onnx",
    jsonUrl: "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/gilles/low/fr_FR-gilles-low.onnx.json",
    fileName: "fr_FR-gilles-low.onnx"
  },
  {
    id: "fr_FR-upmc-medium",
    onnxUrl: "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx",
    jsonUrl: "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx.json",
    fileName: "fr_FR-upmc-medium.onnx"
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
  console.log("=== STARTING DIRECT PIPER SETUP ===");
  
  if (!fs.existsSync(binDir)) {
    fs.mkdirSync(binDir, { recursive: true });
  }
  
  // 1. Download Piper engine
  if (!fs.existsSync(piperBin)) {
    console.log("Piper binary not found. Downloading Piper Linux Engine...");
    const tarPath = path.join(binDir, 'piper.tar.gz');
    const piperTarUrl = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz";
    
    try {
      await downloadFile(piperTarUrl, tarPath);
      console.log("Piper Tarball downloaded. Extracting to /bin...");
      execSync(`tar -xzf "${tarPath}" -C "${binDir}"`);
      if (fs.existsSync(tarPath)) fs.unlinkSync(tarPath);
      if (fs.existsSync(piperBin)) {
        fs.chmodSync(piperBin, '755');
        console.log("Piper binary extracted and chmod +x successful!");
      } else {
        throw new Error("Piper binary was not found after extraction!");
      }
    } catch (err) {
      console.error("Failed to setup Piper binary:", err);
      process.exit(1);
    }
  } else {
    console.log("Piper binary is already installed.");
  }
  
  // 2. Download voices
  if (!fs.existsSync(voicesDir)) {
    fs.mkdirSync(voicesDir, { recursive: true });
  }
  
  for (const voice of AVAILABLE_VOICES) {
    const onnxPath = path.join(voicesDir, voice.fileName);
    const jsonPath = path.join(voicesDir, `${voice.fileName}.json`);
    
    console.log(`\n--- Voice: ${voice.id} ---`);
    
    // Check .onnx file
    if (fs.existsSync(onnxPath)) {
      const stats = fs.statSync(onnxPath);
      if (stats.size > 1000000) {
        console.log(`ONNX file exists and is valid (${(stats.size / 1024 / 1024).toFixed(2)} MB). Skipping download.`);
      } else {
        console.log(`ONNX file exists but is too small (${stats.size} bytes). Re-downloading...`);
        try {
          await downloadFile(voice.onnxUrl, onnxPath);
          console.log(`ONNX file downloaded successfully!`);
        } catch (err) {
          console.error(`Failed to download ONNX for ${voice.id}:`, err);
        }
      }
    } else {
      console.log(`ONNX file not found. Downloading...`);
      try {
        await downloadFile(voice.onnxUrl, onnxPath);
        console.log(`ONNX file downloaded successfully!`);
      } catch (err) {
        console.error(`Failed to download ONNX for ${voice.id}:`, err);
      }
    }
    
    // Check config .json file
    if (fs.existsSync(jsonPath)) {
      const stats = fs.statSync(jsonPath);
      if (stats.size > 100) {
        console.log(`JSON config exists and is valid. Skipping download.`);
      } else {
        console.log(`JSON config is too small. Re-downloading...`);
        try {
          await downloadFile(voice.jsonUrl, jsonPath);
          console.log(`JSON config downloaded successfully!`);
        } catch (err) {
          console.error(`Failed to download JSON config for ${voice.id}:`, err);
        }
      }
    } else {
      console.log(`JSON config not found. Downloading...`);
      try {
        await downloadFile(voice.jsonUrl, jsonPath);
        console.log(`JSON config downloaded successfully!`);
      } catch (err) {
        console.error(`Failed to download JSON config for ${voice.id}:`, err);
      }
    }
  }
  
  console.log("\n=== PIPER SETUP COMPLETED SUCCESSFULLY ===");
}

main().catch(err => {
  console.error("FATAL: Setup failed", err);
  process.exit(1);
});
