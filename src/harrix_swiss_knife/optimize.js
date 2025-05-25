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

// Prepare folder paths based on current file location
const __filename = fileURLToPath(import.meta.url);
const __foldername = path.dirname(__filename);

// Parse CLI arguments into a dictionary
const args = process.argv.slice(2);
const dictionary = args.reduce((acc, item) => {
  const [key, value] = item.split("=");
  acc[key] = value === "true" ? true : value === "false" ? false : value;
  return acc;
}, {});

// Extract needed CLI params with defaults
const quality = "quality" in dictionary ? dictionary.quality : false;
const convertPngToAvif = "convertPngToAvif" in dictionary ? dictionary.convertPngToAvif : false;

// Prepare images folder; if not provided, use default
let imagesFolder = "imagesFolder" in dictionary ? dictionary.imagesFolder : "";
// Prepare output folder; if not provided, use default
let outputFolder = "outputFolder" in dictionary ? dictionary.outputFolder : "";

/**
 * Clear or create a folder
 * @param {string} folderPath - path to the folder to clear
 */
function clearFolder(folderPath) {
  if (fs.existsSync(folderPath)) {
    fs.readdirSync(folderPath).forEach((file) => {
      const filePath = path.join(folderPath, file);
      const stats = fs.lstatSync(filePath);
      if (stats.isDirectory()) {
        fs.rmSync(filePath, { recursive: true, force: true });
      } else {
        fs.unlinkSync(filePath);
      }
    });
  } else {
    fs.mkdirSync(folderPath, { recursive: true });
  }
}

/**
 * Convert JPG/JPEG/WEBP to AVIF
 * @param {string} filePath - source file path
 * @param {string} outputFilePath - destination file path
 * @param {string|boolean} quality - whether "quality" param is passed
 * @param {string} file - file name for logging
 */
function convertJpgWebpToAvif(filePath, outputFilePath, quality, file) {
  const qualityValue = quality ? 93 : 63;
  sharp(filePath)
    .avif({ quality: qualityValue })
    .toFile(outputFilePath)
    .then(() => {
      console.log(`✅ File ${file} successfully converted to AVIF.`);
    })
    .catch((err) => {
      console.error(`❌ Error while converting file ${file}:`, err);
    });
}

/**
 * Convert GIF/MP4 to AVIF using ffmpeg
 * @param {string} filePath - source file path
 * @param {string} outputFilePath - destination file path
 * @param {string} file - file name for logging
 */
function convertGifMp4ToAvif(filePath, outputFilePath, file) {
  const command = `ffmpeg -i "${filePath}" -c:a copy -c:v libaom-av1 -crf 30 -cpu-used 4 -pix_fmt yuv420p "${outputFilePath}"`;
  exec(command, (error) => {
    if (error) {
      console.error(`❌ Error while converting file ${file}:`, error);
      return;
    }
    console.log(`✅ File ${file} successfully converted to AVIF.`);
  });
}

/**
 * Optimize PNG or convert to AVIF, depending on flags
 * @param {string} filePath - source file path
 * @param {string} file - file name for logging
 * @param {boolean|string} quality - true/false from CLI
 * @param {boolean|string} convertPngToAvif - true/false from CLI
 * @param {string} outputFilePathAvif - destination path for AVIF
 * @param {string} outputFilePathPng - destination path for PNG
 */
async function processPng(
  filePath,
  file,
  quality,
  convertPngToAvif,
  outputFilePathAvif,
  outputFilePathPng
) {
  try {
    if (convertPngToAvif) {
      // Convert PNG to AVIF
      const qualityValue = quality ? 93 : 63;
      await sharp(filePath).avif({ quality: qualityValue }).toFile(outputFilePathAvif);
      console.log(`✅ File ${file} successfully converted from PNG to AVIF.`);
    } else {
      if (quality) {
        // If quality is true, copy the file without changes
        fs.copyFileSync(filePath, outputFilePathPng);
        console.log(`File ${file} copied without changes.`);
      } else {
        // Options for PNG
        const pngOptions = {
          compressionLevel: 9,
          adaptiveFiltering: true,
          colors: 256, // reduce colors to 256 for 8-bit PNG
        };

        // Step 1: Optimize with sharp
        const optimizedBuffer = await sharp(filePath).png(pngOptions).toBuffer();

        // Step 2: Further optimize with imagemin-pngquant
        const pngQuantBuffer = await imagemin.buffer(optimizedBuffer, {
          plugins: [
            imageminPngquant({
              quality: [0.6, 0.8],
              strip: true,
              speed: 1,
            }),
          ],
        });

        fs.writeFileSync(outputFilePathPng, pngQuantBuffer);
        console.log(`✅ File ${file} successfully optimized.`);
      }
    }
  } catch (error) {
    console.error(`❌ Error while processing file ${file}:`, error);
  }
}

/**
 * Optimize SVG
 * @param {string} filePath - source file path
 * @param {string} outputFilePath - destination file path
 * @param {string} file - file name for logging
 */
function optimizeSvg(filePath, outputFilePath, file) {
  fs.readFile(filePath, "utf8", (err, data) => {
    if (err) {
      console.error(`❌ File reading error ${file}:`, err);
      return;
    }
    const result = optimize(data, {
      path: filePath,
      multipass: true,
      plugins: [
        // "preset-default" includes a set of default plugins
        "preset-default",
      ],
    });

    fs.writeFile(outputFilePath, result.data, (writeErr) => {
      if (writeErr) {
        console.error(`❌ Error writing the file ${file}:`, writeErr);
        return;
      }
      console.log(`✅ File ${file} successfully optimized.`);
    });
  });
}

/**
 * Decide how to process each image based on extension
 * @param {string} file - name of the file to process
 * @param {object} options - includes imagesFolder, outputFolder, quality, convertPngToAvif
 */
async function processImage(file, { imagesFolder, outputFolder, quality, convertPngToAvif }) {
  const filePath = path.join(imagesFolder, file);

  // Skip directories
  if (fs.lstatSync(filePath).isDirectory()) {
    return;
  }

  const ext = path.extname(file).toLowerCase();
  const outputFileName = path.parse(file).name;
  const outputFilePathAvif = path.join(outputFolder, `${outputFileName}.avif`);
  const outputFilePathPng = path.join(outputFolder, `${outputFileName}.png`);
  const outputFilePathSvg = path.join(outputFolder, `${outputFileName}.svg`);

  switch (ext) {
    case ".jpg":
    case ".jpeg":
    case ".webp":
      convertJpgWebpToAvif(filePath, outputFilePathAvif, quality, file);
      break;

    case ".gif":
    case ".mp4":
      convertGifMp4ToAvif(filePath, outputFilePathAvif, file);
      break;

    case ".png":
      await processPng(filePath, file, quality, convertPngToAvif, outputFilePathAvif, outputFilePathPng);
      break;

    case ".svg":
      optimizeSvg(filePath, outputFilePathSvg, file);
      break;

    default:
      console.log(`🔵 File ${file} is skipped because its format is not supported.`);
      break;
  }
}


async function main() {
  // If no imagesFolder is provided, set default
  if (!imagesFolder) {
    // default paths if none provided
    imagesFolder = path.join(__foldername, "../../temp/images");
    outputFolder = path.join(__foldername, "../../temp/optimized_images");
    clearFolder(outputFolder);
  } else {
    if (outputFolder === "optimized_images") {
      // use a folder inside temp
      outputFolder = path.join(__foldername, "../../temp/optimized_images");
      clearFolder(outputFolder);
    } else if (!outputFolder) {
      // if outputFolder isn't provided but imagesFolder is, create "temp" subfolder
      const tempFolderPath = path.join(imagesFolder, "temp");
      fs.mkdirSync(tempFolderPath, { recursive: true });
      outputFolder = tempFolderPath;
    }
  }

  console.log(`imagesFolder: ${imagesFolder}`);
  console.log(`outputFolder: ${outputFolder}`);

  fs.readdir(imagesFolder, async (err, files) => {
    if (err) {
      console.error("❌ Error reading the image folder:", err);
      return;
    }

    for (const file of files) {
      await processImage(file, { imagesFolder, outputFolder, quality, convertPngToAvif });
    }
  });
}

// Execute main
main();
