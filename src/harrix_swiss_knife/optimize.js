import fs from 'fs';
import path from 'path';
import sharp from 'sharp';
import { fileURLToPath } from 'url';
import { exec } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const imagesDir = path.join(__dirname, '../../data/images');
const outputDir = path.join(__dirname, '../../data/optimized_images');

if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir);
}

fs.readdir(imagesDir, (err, files) => {
  if (err) {
      console.error('Error reading the image folder:', err);
      return;
  }

  files.forEach(file => {
      const ext = path.extname(file).toLowerCase();
      const filePath = path.join(imagesDir, file);
      const outputFileName = path.parse(file).name;
      const outputFilePath = path.join(outputDir, `${outputFileName}.avif`);

      if (ext === '.jpg' || ext === '.jpeg' || ext === '.webp'){
          sharp(filePath)
              .avif({ quality: 63 })
              .toFile(outputFilePath)
              .then(() => {
                  console.log(`File ${file} successfully converted to AVIF.`);
              })
              .catch(err => {
                  console.error(`Error while converting file ${file}:`, err);
              });
      } else if (ext === '.gif' || ext === '.mp4') {
          // Converting GIF to animated AVIF
          const command = `ffmpeg -i "${filePath}" -c:a copy -c:v libaom-av1 -crf 30 -cpu-used 4 -pix_fmt yuv420p "${outputFilePath}"`;

          exec(command, (error, stdout, stderr) => {
              if (error) {
                  console.error(`Error while converting file ${file}:`, error);
                  return;
              }
              console.log(`File ${file} successfully converted to AVIF.`);
          });
      } else {
          console.log(`File ${file} is skipped because its format is not supported.`);
      }
  });});