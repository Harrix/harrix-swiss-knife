/*
Minimize images, including SVG, PNG, JPG, WEBP, AVIF via Node.js.

Example:

```shell
npm run optimize
npm run optimize -- --png8bit false --imagesDir "/custom/images/path" --outputDir "/custom/output/path"
npm run optimize -- --png8bit false
```
*/

import fs from "fs";
import path from "path";
import sharp from "sharp";
import imagemin from "imagemin";
import imageminPngquant from "imagemin-pngquant";
import { fileURLToPath } from "url";
import { exec } from "child_process";
import { optimize } from "svgo";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const args = process.argv.slice(2);
const getArgValue = (argName, defaultValue) => {
  const index = args.indexOf(argName);
  return index !== -1 && args[index + 1] ? args[index + 1] : defaultValue;
};

// Setting values with the possibility of redefinition via command line arguments
const png8bit = getArgValue("--png8bit", true) === "true";
const imagesDir = getArgValue("--imagesDir", path.join(__dirname, "../../data/images"));
const outputDir = getArgValue("--outputDir", path.join(__dirname, "../../data/optimized_images"));

const clearDirectory = (directoryPath) => {
  if (fs.existsSync(directoryPath)) {
    fs.readdirSync(directoryPath).forEach((file) => {
      const filePath = path.join(directoryPath, file);
      if (fs.lstatSync(filePath).isDirectory()) {
        fs.rmSync(filePath, { recursive: true, force: true });
      } else {
        fs.unlinkSync(filePath);
      }
    });
  } else {
    fs.mkdirSync(directoryPath, { recursive: true });
  }
};
clearDirectory(outputDir);

fs.readdir(imagesDir, async (err, files) => {
  if (err) {
    console.error("Error reading the image folder:", err);
    return;
  }

  for (const file of files) {
    const ext = path.extname(file).toLowerCase();
    const filePath = path.join(imagesDir, file);
    const outputFileName = path.parse(file).name;
    const outputFilePath = path.join(outputDir, `${outputFileName}.avif`);

    if (ext === ".jpg" || ext === ".jpeg" || ext === ".webp" || ext === ".avif") {
      sharp(filePath)
        .avif({ quality: 63 })
        .toFile(outputFilePath)
        .then(() => {
          console.log(`File ${file} successfully converted to AVIF.`);
        })
        .catch((err) => {
          console.error(`Error while converting file ${file}:`, err);
        });
    } else if (ext === ".gif" || ext === ".mp4") {
      // Converting GIF to animated AVIF
      const command = `ffmpeg -i "${filePath}" -c:a copy -c:v libaom-av1 -crf 30 -cpu-used 4 -pix_fmt yuv420p "${outputFilePath}"`;

      exec(command, (error, stdout, stderr) => {
        if (error) {
          console.error(`Error while converting file ${file}:`, error);
          return;
        }
        console.log(`File ${file} successfully converted to AVIF.`);
      });
    } else if (ext === ".png") {
      try {
        // Options for PNG
        let pngOptions = { compressionLevel: 9, adaptiveFiltering: true };
        if (png8bit) pngOptions.colors = 256; // Reduce colors to 256 for 8-bit PNG

        // Step 1: Optimize with sharp
        const optimizedBuffer = await sharp(filePath).png(pngOptions).toBuffer();

        // Step 2: Further optimize with imagemin-pngquant
        const pngQuantBuffer = await imagemin.buffer(optimizedBuffer, {
          plugins: [
            imageminPngquant({
              quality: [0.6, 0.8], // Adjust quality as needed
              strip: true, // Remove metadata
              speed: 1, // Slowest speed for best compression
            }),
          ],
        });

        // Write the optimized image to the output directory
        fs.writeFileSync(path.join(outputDir, `${outputFileName}.png`), pngQuantBuffer);

        console.log(`File ${file} successfully optimized.`);
      } catch (error) {
        console.error(`Error while optimizing file ${file}:`, error);
      }
    } else if (ext === ".svg") {
      // Optimize svg
      fs.readFile(filePath, "utf8", (err, data) => {
        if (err) {
          console.error(`File reading error ${file}:`, err);
          return;
        }

        const result = optimize(data, {
          path: filePath,
          multipass: true, // Optimization in multiple passes
          plugins: [
            // We use basic plugins or configure them as needed
            "preset-default",
          ],
        });

        const outputFilePath = path.join(outputDir, `${outputFileName}.svg`);

        fs.writeFile(outputFilePath, result.data, (err) => {
          if (err) {
            console.error(`Error writing the file ${file}:`, err);
          } else {
            console.log(`File ${file} successfully optimized.`);
          }
        });
      });
    } else {
      console.log(`File ${file} is skipped because its format is not supported.`);
    }
  }
});