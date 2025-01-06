/*
Minimize images, including SVG, PNG, JPG, WEBP, AVIF via Node.js.

Example:

```shell
npm run optimize
npm run optimize quality=true imagesFolder="/custom/images/path" outputFolder="/custom/output/path"
npm run optimize quality=true
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
const __foldername = path.dirname(__filename);

const args = process.argv.slice(2);
const dictionary = args.reduce((acc, item) => {
  const [key, value] = item.split("=");
  acc[key] = value === "true" ? true : value === "false" ? false : value;
  return acc;
}, {});

const quality = "quality" in dictionary ? dictionary.quality : false;
let imagesFolder = "imagesFolder" in dictionary ? dictionary.imagesFolder : "";
let outputFolder = "outputFolder" in dictionary ? dictionary.outputFolder : "";

const clearFolder = (folderPath) => {
  if (fs.existsSync(folderPath)) {
    fs.readdirSync(folderPath).forEach((file) => {
      const filePath = path.join(folderPath, file);
      if (fs.lstatSync(filePath).isDirectory()) {
        fs.rmSync(filePath, { recursive: true, force: true });
      } else {
        fs.unlinkSync(filePath);
      }
    });
  } else {
    fs.mkdirSync(folderPath, { recursive: true });
  }
};

const processImage = async (file) => {
  const ext = path.extname(file).toLowerCase();
  const filePath = path.join(imagesFolder, file);
  const outputFileName = path.parse(file).name;
  const outputFilePath = path.join(outputFolder, `${outputFileName}.avif`);

  if (ext === ".jpg" || ext === ".jpeg" || ext === ".webp") {
    let qualityValue = quality ? 93 : 63;
    sharp(filePath)
      .avif({ quality: qualityValue })
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
      if (quality) {
        // If quality is true, copy the file without changes
        fs.copyFileSync(filePath, path.join(outputFolder, `${outputFileName}.png`));
        console.log(`File ${file} copied without changes.`);
      } else {
        // Options for PNG
        let pngOptions = { compressionLevel: 9, adaptiveFiltering: true };
        pngOptions.colors = 256; // Reduce colors to 256 for 8-bit PNG

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

        // Write the optimized image to the output folder
        fs.writeFileSync(path.join(outputFolder, `${outputFileName}.png`), pngQuantBuffer);

        console.log(`File ${file} successfully optimized.`);
      }
    } catch (error) {
      console.error(`Error while processing file ${file}:`, error);
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

      const outputFilePath = path.join(outputFolder, `${outputFileName}.svg`);

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
};

if (!imagesFolder) {
  imagesFolder = path.join(__foldername, "../../temp/images");
  outputFolder = path.join(__foldername, "../../temp/optimized_images");
  clearFolder(outputFolder);
} else {
  if (outputFolder == "optimized_images") {
    outputFolder = path.join(__foldername, "../../temp/optimized_images");
  } else if (!outputFolder) {
    const tempFolderPath = path.join(dictionary.imagesFolder, "temp");
    fs.mkdir(tempFolderPath, { recursive: true }, (err) => {
      if (err) return console.error(`Error creating the folder: ${err.message}`);
    });
    outputFolder = path.join(imagesFolder, `temp`);
  }
}

console.log(`imagesFolder: ${imagesFolder}`);
console.log(`outputFolder: ${outputFolder}`);

fs.readdir(imagesFolder, async (err, files) => {
  if (err) {
    console.error("Error reading the image folder:", err);
    return;
  }

  for (const file of files) {
    processImage(file);
  }
});
