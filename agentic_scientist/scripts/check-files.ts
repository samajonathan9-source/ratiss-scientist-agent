import * as fs from 'fs';
import * as path from 'path';

const voicesDir = path.join(process.cwd(), 'bin', 'piper', 'voices');
if (fs.existsSync(voicesDir)) {
  const files = fs.readdirSync(voicesDir);
  for (const f of files) {
    const p = path.join(voicesDir, f);
    const stat = fs.statSync(p);
    console.log(`${f}: ${stat.size} bytes (${(stat.size / 1024 / 1024).toFixed(2)} MB)`);
  }
} else {
  console.log("Voices directory does not exist!");
}
