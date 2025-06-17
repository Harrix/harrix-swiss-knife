/**
 * Minimize images, including SVG, PNG, JPG, WEBP, AVIF via Node.js.
 *
 * This script provides comprehensive image optimization capabilities:
 * - Converts JPG/JPEG/WEBP to AVIF format
 * - Converts GIF/MP4 to AVIF using ffmpeg
 * - Optimizes PNG files or converts them to AVIF
 * - Optimizes SVG files using SVGO
 * - Resizes images to maximum dimensions before optimization
 * - Optimizes existing AVIF files
 *
 * Usage examples:
 * ```shell
 * npm run optimize
 * npm run optimize quality=true imagesFolder="/custom/images/path" outputFolder="/custom/output/path"
 * npm run optimize quality=true maxSize=1920
 * npm run optimize convertPngToAvif=true maxSize=800
 * ```
 *
 * CLI Arguments:
 * - quality: boolean - Use high quality settings. Defaults to `false`.
 * - convertPngToAvif: boolean - Convert PNG files to AVIF instead of optimizing. Defaults to `false`.
 * - imagesFolder: string - Source folder path. Defaults to "../../temp/images".
 * - outputFolder: string - Output folder path. Defaults to "../../temp/optimized_images".
 * - maxSize: number - Maximum width or height in pixels. Images larger than this will be resized. Optional.
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
const maxSize = "maxSize" in dictionary ? parseInt(dictionary.maxSize) : null;

// Prepare images folder; if not provided, use default
let imagesFolder = "imagesFolder" in dictionary ? dictionary.imagesFolder : "";
// Prepare output folder; if not provided, use default
let outputFolder = "outputFolder" in dictionary ? dictionary.outputFolder : "";

/**
 * Clear or create a folder at the specified path.
 *
 * Removes all contents from an existing folder or creates a new one if it doesn't exist.
 * Handles both files and nested directories recursively.
 *
 * Args:
 *
 * - `folderPath` (`string`): The path to the folder to clear or create.
 *
 * Returns:
 *
 * - `void`: This function doesn't return a value.
 *
 * Note:
 *
 * Uses synchronous file system operations. Will create parent directories if they don't exist.
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
 * Resize image if it exceeds maximum dimensions.
 *
 * Checks if image width or height exceeds the maxSize parameter and resizes
 * proportionally while maintaining aspect ratio if necessary.
 *
 * Args:
 *
 * - `sharpInstance` (`Sharp`): Sharp instance of the image to potentially resize.
 * - `maxSize` (`number|null`): Maximum width or height in pixels. If null, no resizing is applied.
 *
 * Returns:
 *
 * - `Promise<Sharp>`: Sharp instance, potentially resized.
 *
 * Note:
 *
 * Uses Sharp's resize method with { fit: 'inside' } to maintain aspect ratio.
 * Only resizes if image dimensions exceed maxSize parameter.
 */
async function resizeIfNeeded(sharpInstance, maxSize) {
  if (!maxSize) {
    return sharpInstance;
  }

  const metadata = await sharpInstance.metadata();
  const { width, height } = metadata;

  if (width > maxSize || height > maxSize) {
    return sharpInstance.resize(maxSize, maxSize, {
      fit: "inside",
      withoutEnlargement: true,
    });
  }

  return sharpInstance;
}

/**
 * Convert JPG/JPEG/WEBP images to AVIF format using Sharp.
 *
 * Converts supported image formats to AVIF with configurable quality settings.
 * Uses different quality values based on the quality parameter.
 * Applies resizing if maxSize is specified.
 *
 * Args:
 *
 * - `filePath` (`string`): The source file path to convert.
 * - `outputFilePath` (`string`): The destination file path for the AVIF output.
 * - `quality` (`string|boolean`): Quality setting - if truthy, uses high quality (93), otherwise standard quality (63).
 * - `file` (`string`): The original filename for logging purposes.
 * - `maxSize` (`number|null`): Maximum width or height in pixels for resizing.
 *
 * Returns:
 *
 * - `Promise<void>`: Resolves when conversion is complete.
 *
 * Note:
 *
 * This function is asynchronous and uses Sharp's promise-based API.
 * Quality values: high quality = 93, standard quality = 63.
 */
async function convertJpgWebpToAvif(filePath, outputFilePath, quality, file, maxSize) {
  try {
    const qualityValue = quality ? 93 : 63;
    let sharpInstance = sharp(filePath);

    // Resize if needed
    sharpInstance = await resizeIfNeeded(sharpInstance, maxSize);

    await sharpInstance.avif({ quality: qualityValue }).toFile(outputFilePath);

    console.log(`✅ File ${file} successfully converted to AVIF.`);
  } catch (err) {
    console.error(`❌ Error while converting file ${file}:`, err);
  }
}

/**
 * Convert GIF/MP4 files to AVIF format using ffmpeg.
 *
 * Uses ffmpeg command line tool to convert animated GIF or MP4 video files to AVIF format.
 * Applies specific encoding settings optimized for quality and file size.
 *
 * Args:
 *
 * - `filePath` (`string`): The source file path to convert.
 * - `outputFilePath` (`string`): The destination file path for the AVIF output.
 * - `file` (`string`): The original filename for logging purposes.
 * - `maxSize` (`number|null`): Maximum width or height in pixels for resizing.
 *
 * Returns:
 *
 * - `void`: This function doesn't return a value, but logs success/error messages.
 *
 * Note:
 *
 * Requires ffmpeg to be installed and available in PATH.
 * Uses libaom-av1 codec with CRF 30 and cpu-used 4 for balanced quality/speed.
 */
function convertGifMp4ToAvif(filePath, outputFilePath, file, maxSize) {
  let scaleFilter = "";
  if (maxSize) {
    scaleFilter = `-vf "scale='if(gt(iw,ih),min(${maxSize},iw),-1)':'if(gt(iw,ih),-1,min(${maxSize},ih))'"`;
  }

  const command = `ffmpeg -i "${filePath}" ${scaleFilter} -c:a copy -c:v libaom-av1 -crf 30 -cpu-used 4 -pix_fmt yuv420p "${outputFilePath}"`;

  exec(command, (error) => {
    if (error) {
      console.error(`❌ Error while converting file ${file}:`, error);
      return;
    }
    console.log(`✅ File ${file} successfully converted to AVIF.`);
  });
}

/**
 * Process PNG files - either optimize or convert to AVIF based on parameters.
 *
 * Handles PNG files in three different ways based on the provided flags:
 * 1. Convert to AVIF if convertPngToAvif is true
 * 2. Copy without changes if quality is true
 * 3. Optimize using Sharp and pngquant for maximum compression
 * Applies resizing if maxSize is specified.
 *
 * Args:
 *
 * - `filePath` (`string`): The source PNG file path.
 * - `file` (`string`): The original filename for logging purposes.
 * - `quality` (`boolean|string`): If truthy, copies file without optimization. Defaults to `false`.
 * - `convertPngToAvif` (`boolean|string`): If truthy, converts PNG to AVIF instead of optimizing. Defaults to `false`.
 * - `outputFilePathAvif` (`string`): The destination path for AVIF conversion.
 * - `outputFilePathPng` (`string`): The destination path for PNG optimization.
 * - `maxSize` (`number|null`): Maximum width or height in pixels for resizing.
 *
 * Returns:
 *
 * - `Promise<void>`: Resolves when processing is complete.
 *
 * Note:
 *
 * Uses Sharp for initial PNG optimization and imagemin-pngquant for further compression.
 * AVIF quality: high quality = 93, standard quality = 63.
 * PNG optimization reduces colors to 256 and applies maximum compression.
 */
async function processPng(filePath, file, quality, convertPngToAvif, outputFilePathAvif, outputFilePathPng, maxSize) {
  try {
    if (convertPngToAvif) {
      // Convert PNG to AVIF
      const qualityValue = quality ? 93 : 63;
      let sharpInstance = sharp(filePath);

      // Resize if needed
      sharpInstance = await resizeIfNeeded(sharpInstance, maxSize);

      await sharpInstance.avif({ quality: qualityValue }).toFile(outputFilePathAvif);
      console.log(`✅ File ${file} successfully converted from PNG to AVIF.`);
    } else {
      if (quality) {
        // If quality is true, copy the file without changes (but still resize if needed)
        if (maxSize) {
          let sharpInstance = sharp(filePath);
          sharpInstance = await resizeIfNeeded(sharpInstance, maxSize);
          await sharpInstance.png().toFile(outputFilePathPng);
          console.log(`✅ File ${file} resized and copied.`);
        } else {
          fs.copyFileSync(filePath, outputFilePathPng);
          console.log(`File ${file} copied without changes.`);
        }
      } else {
        // Options for PNG optimization
        const pngOptions = {
          compressionLevel: 9,
          adaptiveFiltering: true,
          colors: 256, // reduce colors to 256 for 8-bit PNG
        };

        // Step 1: Optimize with Sharp (and resize if needed)
        let sharpInstance = sharp(filePath);
        sharpInstance = await resizeIfNeeded(sharpInstance, maxSize);
        const optimizedBuffer = await sharpInstance.png(pngOptions).toBuffer();

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
 * Process static AVIF files - optimize existing static AVIF images using Sharp.
 *
 * Optimizes static AVIF images using Sharp with quality settings and optional resizing.
 * This function handles only single-frame AVIF images.
 *
 * Args:
 *
 * - `filePath` (`string`): The source AVIF file path.
 * - `outputFilePath` (`string`): The destination path for optimized AVIF.
 * - `file` (`string`): The original filename for logging purposes.
 * - `quality` (`boolean|string`): Quality setting flag.
 * - `maxSize` (`number|null`): Maximum width or height in pixels for resizing.
 *
 * Returns:
 *
 * - `Promise<void>`: Resolves when optimization is complete.
 *
 * Note:
 *
 * Sharp quality: 93 (high), 63 (standard).
 */
async function processStaticAvif(filePath, outputFilePath, file, quality, maxSize) {
  const qualityValue = quality ? 93 : 63;
  let sharpInstance = sharp(filePath);

  sharpInstance = await resizeIfNeeded(sharpInstance, maxSize);
  await sharpInstance.avif({ quality: qualityValue }).toFile(outputFilePath);

  console.log(`✅ File ${file} successfully optimized with sharp.`);
}

/**
 * Process animated AVIF files using ffmpeg.
 *
 * Optimizes animated AVIF images using ffmpeg to preserve animation frames.
 * Uses libaom-av1 codec with configurable quality settings.
 *
 * Args:
 *
 * - `filePath` (`string`): The source animated AVIF file path.
 * - `outputFilePath` (`string`): The destination path for optimized AVIF.
 * - `file` (`string`): The original filename for logging purposes.
 * - `quality` (`boolean|string`): Quality setting flag.
 * - `maxSize` (`number|null`): Maximum width or height in pixels for resizing.
 *
 * Returns:
 *
 * - `Promise<void>`: Resolves when optimization is complete.
 *
 * Note:
 *
 * ffmpeg quality: CRF 20 (high), 30 (standard). Lower CRF values mean better quality.
 * Requires ffmpeg to be installed and available in PATH.
 */
async function processAnimatedAvif(filePath, outputFilePath, file, quality, maxSize) {
  let scaleFilter = "";
  if (maxSize) {
    scaleFilter = `-vf "scale='if(gt(iw,ih),min(${maxSize},iw),-1)':'if(gt(iw,ih),-1,min(${maxSize},ih))':force_original_aspect_ratio=decrease"`;
  }

  const crf = quality ? 20 : 30;
  const command = `ffmpeg -i "${filePath}" ${scaleFilter} -c:a copy -c:v libaom-av1 -crf ${crf} -cpu-used 4 -pix_fmt yuv420p "${outputFilePath}"`;

  return new Promise((resolve, reject) => {
    exec(command, (execError) => {
      if (execError) {
        console.error(`❌ Error while processing animated AVIF file ${file} with ffmpeg:`, execError);
        reject(execError);
        return;
      }
      console.log(`✅ File ${file} successfully optimized with ffmpeg.`);
      resolve();
    });
  });
}

/**
 * Process AVIF files - determine if animated or static and route accordingly.
 *
 * Analyzes AVIF files to determine if they contain multiple frames (animated) or single frame (static).
 * Routes to appropriate processing function based on animation detection.
 * Falls back to ffmpeg if Sharp fails at any stage.
 *
 * Args:
 *
 * - `filePath` (`string`): The source AVIF file path.
 * - `outputFilePath` (`string`): The destination path for optimized AVIF.
 * - `file` (`string`): The original filename for logging purposes.
 * - `quality` (`boolean|string`): Quality setting flag.
 * - `maxSize` (`number|null`): Maximum width or height in pixels for resizing.
 *
 * Returns:
 *
 * - `Promise<void>`: Resolves when optimization is complete.
 *
 * Note:
 *
 * Uses Sharp to read metadata and detect animation. Falls back to ffmpeg if Sharp fails.
 * Animated AVIFs are detected by checking if metadata.pages > 1.
 */
async function processAvif(filePath, outputFilePath, file, quality, maxSize) {
  try {
    // Try to read metadata with Sharp to determine if animated
    const metadata = await sharp(filePath).metadata();

    // Check if the AVIF is animated (multiple frames/pages)
    if (metadata.pages && metadata.pages > 1) {
      console.log(`🔄 ${file} is animated. Processing with ffmpeg...`);
      await processAnimatedAvif(filePath, outputFilePath, file, quality, maxSize);
    } else {
      console.log(`🔄 ${file} is static. Processing with Sharp...`);
      try {
        await processStaticAvif(filePath, outputFilePath, file, quality, maxSize);
      } catch (sharpError) {
        console.log(`⚠️ Sharp failed to process static AVIF ${file}. Falling back to ffmpeg. (Error: ${sharpError.message})`);
        await processAnimatedAvif(filePath, outputFilePath, file, quality, maxSize);
      }
    }
  } catch (metadataError) {
    // If Sharp fails to read metadata, assume it's animated and use ffmpeg
    console.log(`⚠️ Sharp failed to read metadata for ${file}. Falling back to ffmpeg. (Error: ${metadataError.message})`);
    await processAnimatedAvif(filePath, outputFilePath, file, quality, maxSize);
  }
}

/**
 * Optimize SVG files using SVGO library.
 *
 * Reads SVG files and applies SVGO optimization with default preset plugins.
 * Uses multipass optimization for better results.
 *
 * Args:
 *
 * - `filePath` (`string`): The source SVG file path.
 * - `outputFilePath` (`string`): The destination path for optimized SVG.
 * - `file` (`string`): The original filename for logging purposes.
 *
 * Returns:
 *
 * - `void`: This function doesn't return a value, but logs success/error messages.
 *
 * Note:
 *
 * Uses SVGO's "preset-default" plugin set with multipass enabled.
 * All file operations are asynchronous using Node.js fs callbacks.
 * SVG files are not resized as they are vector-based and scalable by nature.
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
 * Process a single image file based on its extension and configuration.
 *
 * Routes image processing based on file extension:
 * - JPG/JPEG/WEBP → AVIF conversion
 * - GIF/MP4 → AVIF conversion via ffmpeg
 * - PNG → Optimization or AVIF conversion
 * - AVIF → Optimization
 * - SVG → Optimization
 * - Other formats → Skip with message
 *
 * Args:
 *
 * - `file` (`string`): The filename to process.
 * - `options` (`object`): Configuration object containing:
 *   - `imagesFolder` (`string`): Source folder path
 *   - `outputFolder` (`string`): Destination folder path
 *   - `quality` (`boolean|string`): Quality setting flag. Defaults to `false`.
 *   - `convertPngToAvif` (`boolean|string`): PNG to AVIF conversion flag. Defaults to `false`.
 *   - `maxSize` (`number|null`): Maximum width or height in pixels for resizing.
 *
 * Returns:
 *
 * - `Promise<void>`: Resolves when processing is complete or skipped.
 *
 * Note:
 *
 * Skips directories automatically. File extension detection is case-insensitive.
 * Output filenames preserve the original name but change the extension based on processing type.
 */
async function processImage(file, { imagesFolder, outputFolder, quality, convertPngToAvif, maxSize }) {
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
      await convertJpgWebpToAvif(filePath, outputFilePathAvif, quality, file, maxSize);
      break;

    case ".gif":
    case ".mp4":
      convertGifMp4ToAvif(filePath, outputFilePathAvif, file, maxSize);
      break;

    case ".png":
      await processPng(filePath, file, quality, convertPngToAvif, outputFilePathAvif, outputFilePathPng, maxSize);
      break;

    case ".avif":
      await processAvif(filePath, outputFilePathAvif, file, quality, maxSize);
      break;

    case ".svg":
      optimizeSvg(filePath, outputFilePathSvg, file);
      break;

    default:
      console.log(`🔵 File ${file} is skipped because its format is not supported.`);
      break;
  }
}

/**
 * Main function that orchestrates the image optimization process.
 *
 * Sets up folder paths, handles CLI argument parsing, and processes all images in the source folder.
 * Manages default folder creation and cleanup based on provided arguments.
 *
 * Returns:
 *
 * - `Promise<void>`: Resolves when all images have been processed.
 *
 * Note:
 *
 * Default paths:
 * - imagesFolder: "../../temp/images" (relative to script location)
 * - outputFolder: "../../temp/optimized_images" (relative to script location)
 *
 * If custom imagesFolder is provided but no outputFolder, creates a "temp" subfolder in imagesFolder.
 * Clears output folder before processing to ensure clean results.
 */
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
  if (maxSize) {
    console.log(`maxSize: ${maxSize}px`);
  }

  fs.readdir(imagesFolder, async (err, files) => {
    if (err) {
      console.error("❌ Error reading the image folder:", err);
      return;
    }

    for (const file of files) {
      await processImage(file, { imagesFolder, outputFolder, quality, convertPngToAvif, maxSize });
    }
  });
}

// Execute main function
main();
