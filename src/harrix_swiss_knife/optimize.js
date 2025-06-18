/**
 * Minimize images, including SVG, PNG, JPG, WEBP, AVIF via Node.js.
 *
 * This script provides comprehensive image optimization capabilities:
 *
 * - Converts JPG/JPEG/WEBP to AVIF format
 * - Converts GIF/MP4 to AVIF using ffmpeg
 * - Optimizes PNG files or converts them to AVIF
 * - Optimizes SVG files using SVGO
 * - Resizes images to maximum dimensions before optimization
 * - Optimizes existing AVIF files (both static and animated)
 *
 * Usage examples:
 *
 * ```shell
 * npm run optimize
 * npm run optimize quality=true imagesFolder="/custom/images/path" outputFolder="/custom/output/path"
 * npm run optimize quality=true maxSize=1920
 * npm run optimize convertPngToAvif=true maxSize=800
 * ```
 *
 * CLI Arguments:
 *
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
 * Uses Sharp's resize method with `{ fit: 'inside', withoutEnlargement: true }` to maintain aspect ratio.
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
 * - `quality` (`boolean`): Quality setting - if true, uses high quality (93), otherwise standard quality (63).
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
 * Includes optional resizing using ffmpeg's scale filter.
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
 * Resizing is done using ffmpeg's scale filter with aspect ratio preservation.
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
 *
 * 1. Convert to AVIF if convertPngToAvif is true
 * 2. Copy without changes (with optional resizing) if quality is true
 * 3. Optimize using Sharp and imagemin-pngquant for maximum compression
 *
 * Applies resizing if maxSize is specified.
 *
 * Args:
 *
 * - `filePath` (`string`): The source PNG file path.
 * - `file` (`string`): The original filename for logging purposes.
 * - `quality` (`boolean`): If true, copies file without optimization (but may resize). Defaults to `false`.
 * - `convertPngToAvif` (`boolean`): If true, converts PNG to AVIF instead of optimizing. Defaults to `false`.
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
 * PNG optimization: compressionLevel 9, adaptiveFiltering true, colors reduced to 256.
 * Pngquant settings: quality [0.6, 0.8], strip metadata, speed 1.
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
 * Check if AVIF file is animated using multiple detection methods.
 *
 * Uses a multi-tier approach for reliable animation detection:
 *
 * 1. First tries ffprobe to count packets
 * 2. Falls back to ffmpeg duration/fps analysis
 * 3. Finally uses avifdec frame extraction as last resort
 *
 * Considers a file animated if it has more than 1 frame or duration > 0.1 seconds.
 *
 * Args:
 *
 * - `filePath` (`string`): The source AVIF file path.
 *
 * Returns:
 *
 * - `Promise<boolean>`: Resolves to true if animated (more than 1 frame), false if static.
 *
 * Note:
 *
 * This function creates temporary directories for frame extraction testing.
 * Cleans up all temporary files after detection is complete.
 * Requires ffprobe, ffmpeg, and avifdec to be available in PATH or script directory.
 */
async function isAvifAnimated(filePath) {
  return new Promise((resolve) => {
    // First, try using ffprobe for more reliable detection
    const ffprobeCommand = `ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -of csv=p=0 "${filePath}"`;

    exec(ffprobeCommand, (error, stdout, stderr) => {
      if (!error && stdout.trim()) {
        const packetCount = parseInt(stdout.trim());
        // If we can get packet count, use it
        if (!isNaN(packetCount)) {
          const isAnimated = packetCount > 1;
          console.log(`📊 FFprobe detected ${packetCount} packet(s) in ${path.basename(filePath)}`);
          console.log(isAnimated ? `🎬 AVIF is animated` : `🖼️ AVIF is static`);
          resolve(isAnimated);
          return;
        }
      }

      // If ffprobe fails, try alternative ffmpeg detection
      const ffmpegCommand = `ffmpeg -i "${filePath}" -f null - 2>&1`;

      exec(ffmpegCommand, (ffError, ffStdout, ffStderr) => {
        const ffOutput = ffStdout + ffStderr;

        // Look for specific indicators of animation
        // Check for duration > 0 and fps > 0
        const durationMatch = ffOutput.match(/Duration: (\d{2}):(\d{2}):(\d{2}\.\d+)/);
        const fpsMatch = ffOutput.match(/(\d+(?:\.\d+)?)\s*fps/);

        let isAnimated = false;

        if (durationMatch) {
          const hours = parseInt(durationMatch[1]);
          const minutes = parseInt(durationMatch[2]);
          const seconds = parseFloat(durationMatch[3]);
          const totalSeconds = hours * 3600 + minutes * 60 + seconds;

          // If duration is more than 0.1 seconds, likely animated
          if (totalSeconds > 0.1) {
            isAnimated = true;
          }
        }

        // Also check fps - static images usually report 25 fps but with single frame
        if (fpsMatch) {
          const fps = parseFloat(fpsMatch[1]);
          // Look for frame count in the output
          const frameMatch = ffOutput.match(/(\d+)\s+frames?/i);
          if (frameMatch) {
            const frameCount = parseInt(frameMatch[1]);
            if (frameCount > 1) {
              isAnimated = true;
            } else if (frameCount === 1) {
              isAnimated = false;
            }
          }
        }

        // As a last resort, try avifdec with a more careful approach
        if (!durationMatch && !frameMatch) {
          const avifdecPath = path.join(__foldername, "../../avifdec.exe");
          const tempDir = path.join(path.dirname(filePath), `temp_check_${Date.now()}`);

          // Create temp directory
          fs.mkdirSync(tempDir, { recursive: true });

          const frameBasePath = path.join(tempDir, "check_frame.png");
          const avifdecCommand = `"${avifdecPath}" "${filePath}" "${frameBasePath}" --index 0`;

          exec(avifdecCommand, (avifdecError) => {
            let frameCount = 0;

            try {
              // First check if even a single frame was extracted
              if (!avifdecError && fs.existsSync(tempDir)) {
                const extractedFiles = fs.readdirSync(tempDir).filter((f) => f.endsWith(".png"));

                if (extractedFiles.length > 0) {
                  // Now try to extract second frame
                  const secondFrameCommand = `"${avifdecPath}" "${filePath}" "${path.join(
                    tempDir,
                    "check_frame2.png"
                  )}" --index 1`;

                  exec(secondFrameCommand, (secondFrameError) => {
                    // If second frame extraction succeeds, it's animated
                    if (!secondFrameError) {
                      const secondFrameFiles = fs
                        .readdirSync(tempDir)
                        .filter((f) => f.includes("check_frame2") && f.endsWith(".png"));

                      isAnimated = secondFrameFiles.length > 0;
                    }

                    // Clean up temp directory
                    if (fs.existsSync(tempDir)) {
                      fs.rmSync(tempDir, { recursive: true, force: true });
                    }

                    console.log(`📊 avifdec detection for ${path.basename(filePath)}`);
                    console.log(isAnimated ? `🎬 AVIF is animated` : `🖼️ AVIF is static`);
                    resolve(isAnimated);
                  });
                } else {
                  // No frames extracted at all
                  if (fs.existsSync(tempDir)) {
                    fs.rmSync(tempDir, { recursive: true, force: true });
                  }
                  console.log(`🖼️ AVIF appears to be static (no frames extracted)`);
                  resolve(false);
                }
              } else {
                // avifdec failed
                if (fs.existsSync(tempDir)) {
                  fs.rmSync(tempDir, { recursive: true, force: true });
                }
                console.log(`⚠️ Could not determine animation status, assuming static`);
                resolve(false);
              }
            } catch (err) {
              // Clean up on error
              if (fs.existsSync(tempDir)) {
                fs.rmSync(tempDir, { recursive: true, force: true });
              }
              console.error(`❌ Error checking AVIF animation status:`, err);
              resolve(false);
            }
          });
        } else {
          console.log(`📊 FFmpeg detection for ${path.basename(filePath)}`);
          console.log(isAnimated ? `🎬 AVIF is animated` : `🖼️ AVIF is static`);
          resolve(isAnimated);
        }
      });
    });
  });
}

/**
 * Get frame rate from video file using ffmpeg.
 *
 * Extracts the frame rate (fps) from video files by parsing ffmpeg output.
 * Looks for fps values in ffmpeg streams, prioritizing Stream #0:1 when available.
 * Filters out unrealistic values (< 1 or > 120 fps).
 *
 * Args:
 *
 * - `filePath` (`string`): The source video file path.
 *
 * Returns:
 *
 * - `Promise<number>`: Frame rate in fps, defaults to 25 if unable to detect.
 *
 * Note:
 *
 * Uses platform-specific commands (findstr on Windows, grep on Unix-like systems).
 * Prioritizes Stream #0:1 over other streams for more accurate fps detection.
 */
async function getFrameRate(filePath) {
  return new Promise((resolve) => {
    const command =
      process.platform === "win32"
        ? `ffmpeg -i "${filePath}" -f null - 2>&1 | findstr "fps"`
        : `ffmpeg -i "${filePath}" -f null - 2>&1 | grep "fps"`;

    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.log(`⚠️ Could not determine frame rate, using default 25 fps`);
        resolve(25);
        return;
      }

      // Parse all lines containing fps
      const lines = stdout.split("\n").filter((line) => line.includes("fps"));

      // Try to find the fps value from the second stream (usually the correct one)
      let fps = 25; // default fallback

      for (const line of lines) {
        // Match patterns like "14.42 fps" or "25 fps"
        const fpsMatch = line.match(/(\d+(?:\.\d+)?)\s*fps/);
        if (fpsMatch) {
          const detectedFps = parseFloat(fpsMatch[1]);
          // Skip obviously wrong values like 0 or 1
          if (detectedFps > 1 && detectedFps < 120) {
            fps = detectedFps;
            // If this is from Stream #0:1, it's likely the correct one
            if (line.includes("Stream #0:1")) {
              break;
            }
          }
        }
      }

      console.log(`📊 Detected frame rate: ${fps} fps`);
      resolve(fps);
    });
  });
}

/**
 * Process animated AVIF files using avifdec and ffmpeg tools.
 *
 * Extracts all frames from animated AVIF, resizes them if needed, reduces frame rate to max 10 fps for optimization,
 * and reassembles into optimized animated AVIF using ffmpeg or avifenc.
 * Uses avifdec to extract frames and either ffmpeg or avifenc to create the final animated AVIF.
 * Preserves original playback speed while reducing frame count for optimization.
 *
 * Args:
 *
 * - `filePath` (`string`): The source animated AVIF file path.
 * - `outputFilePath` (`string`): The destination path for optimized AVIF.
 * - `file` (`string`): The original filename for logging purposes.
 * - `quality` (`boolean`): Quality setting flag - affects CRF/quality values.
 * - `maxSize` (`number|null`): Maximum width or height in pixels for resizing.
 *
 * Returns:
 *
 * - `Promise<void>`: Resolves when optimization is complete.
 *
 * Note:
 *
 * Creates temporary directories for frame extraction and processing.
 * Uses different assembly methods based on frame count (ffmpeg for >50 frames, avifenc for ≤50).
 * Reduces frame rate from original to maximum 10 fps for file size optimization.
 * Quality settings: high quality uses min=15/max=20, standard uses min=25/max=30.
 */
async function processAnimatedAvif(filePath, outputFilePath, file, quality, maxSize) {
  return new Promise(async (resolve, reject) => {
    try {
      const avifdecPath = path.join(__foldername, "../../avifdec.exe");
      const avifencPath = path.join(__foldername, "../../avifenc.exe");

      // Get original frame rate
      const originalFrameRate = await getFrameRate(filePath);

      // Calculate target frame rate (max 10 fps)
      const targetFrameRate = Math.min(originalFrameRate, 10);
      const frameRateReduction = originalFrameRate > 10;

      // Calculate which frames to keep
      const framesToKeepRatio = targetFrameRate / originalFrameRate;

      console.log(`📊 Original frame rate: ${originalFrameRate} fps`);
      if (frameRateReduction) {
        console.log(`🎯 Target frame rate: ${targetFrameRate} fps (reducing from ${originalFrameRate} fps)`);
        console.log(`📉 Keeping approximately ${Math.round(framesToKeepRatio * 100)}% of frames`);
      }

      // Create temporary directory for frames
      const tempDir = path.join(path.dirname(filePath), `temp_frames_${Date.now()}`);
      fs.mkdirSync(tempDir, { recursive: true });

      console.log(`🔄 Processing animated AVIF: ${file}...`);
      console.log(`📁 Created temp directory: ${tempDir}`);

      // Step 1: Extract all frames using avifdec
      const frameBasePath = path.join(tempDir, "frame.png");
      const extractCommand = `"${avifdecPath}" "${filePath}" "${frameBasePath}" --index all`;

      console.log(`🎬 Extracting frames from ${file}...`);

      exec(extractCommand, async (extractError, stdout, stderr) => {
        if (extractError) {
          console.error(`❌ Error extracting frames from ${file}:`, extractError);
          // Clean up temp directory
          fs.rmSync(tempDir, { recursive: true, force: true });
          reject(extractError);
          return;
        }

        try {
          // Step 2: Get list of extracted frame files
          let frameFiles = fs
            .readdirSync(tempDir)
            .filter((f) => f.startsWith("frame-") && f.endsWith(".png"))
            .sort(); // Ensure proper order

          if (frameFiles.length === 0) {
            throw new Error("No frames were extracted");
          }

          console.log(`📸 Extracted ${frameFiles.length} frames`);

          // Step 3: Remove excess frames if frame rate is too high
          if (frameRateReduction) {
            console.log(`🗑️ Reducing frame count for optimal file size...`);

            const originalFrameCount = frameFiles.length;
            const targetFrameCount = Math.max(1, Math.round(originalFrameCount * framesToKeepRatio));

            // Calculate which frames to keep using uniform distribution
            const framesToKeep = new Set();
            for (let i = 0; i < targetFrameCount; i++) {
              const frameIndex = Math.round((i * (originalFrameCount - 1)) / (targetFrameCount - 1));
              framesToKeep.add(frameIndex);
            }

            // Delete frames we don't need and rename remaining frames
            const keptFrames = [];
            frameFiles.forEach((frameFile, index) => {
              const framePath = path.join(tempDir, frameFile);
              if (framesToKeep.has(index)) {
                // Rename to maintain sequence
                const newFrameName = `kept-frame-${String(keptFrames.length).padStart(6, "0")}.png`;
                const newFramePath = path.join(tempDir, newFrameName);
                fs.renameSync(framePath, newFramePath);
                keptFrames.push(newFrameName);
              } else {
                // Delete unneeded frame
                fs.unlinkSync(framePath);
              }
            });

            frameFiles = keptFrames;
            console.log(`✅ Reduced from ${originalFrameCount} to ${frameFiles.length} frames`);
          }

          // Step 4: Resize frames if needed
          if (maxSize) {
            console.log(`🔧 Resizing frames to max ${maxSize}px...`);

            for (const frameFile of frameFiles) {
              const framePath = path.join(tempDir, frameFile);
              const tempFramePath = path.join(tempDir, `temp_${frameFile}`);

              let sharpInstance = sharp(framePath);

              // Resize frame and save to temporary file
              sharpInstance = await resizeIfNeeded(sharpInstance, maxSize);
              await sharpInstance.png().toFile(tempFramePath);

              // Replace original with resized version
              fs.unlinkSync(framePath);
              fs.renameSync(tempFramePath, framePath);
            }

            console.log(`✅ Resized ${frameFiles.length} frames`);
          }

          // Step 5: Reassemble frames into animated AVIF using avifenc with correct frame rate
          console.log(`🔧 Reassembling frames into animated AVIF with ${targetFrameRate} fps...`);

          // Convert quality values:
          // For avifenc: 0 = best quality, 63 = worst quality
          const minQuality = quality ? 15 : 25; // min quality (best case)
          const maxQuality = quality ? 20 : 30; // max quality (worst case)

          console.log(`🎨 Using quality settings: min=${minQuality}, max=${maxQuality}`);

          // Check if we have frames to process
          if (frameFiles.length === 0) {
            throw new Error("No frames available for reassembly");
          }

          // Use different approaches based on frame count
          let assembleCommand;

          if (frameFiles.length > 50) {
            // For many frames, use a file list approach
            const fileListPath = path.join(tempDir, "frames.txt");
            const fileListContent = frameFiles.map((f) => path.join(tempDir, f)).join("\n");
            fs.writeFileSync(fileListPath, fileListContent);

            // Use ffmpeg to create the animated AVIF when there are too many frames
            assembleCommand = `ffmpeg -r ${targetFrameRate} -f image2 -i "${path.join(
              tempDir,
              frameFiles[0].replace(/\d+/, "%06d")
            )}" -c:v libaom-av1 -crf ${minQuality + 10} -cpu-used 4 -pix_fmt yuv420p "${outputFilePath}"`;
          } else {
            // For fewer frames, use the original approach
            const frameList = frameFiles.map((f) => `"${path.join(tempDir, f)}"`).join(" ");
            assembleCommand = `"${avifencPath}" ${frameList} --fps ${targetFrameRate} --min ${minQuality} --max ${maxQuality} "${outputFilePath}"`;
          }

          exec(assembleCommand, (assembleError, stdout, stderr) => {
            // Clean up temp directory
            fs.rmSync(tempDir, { recursive: true, force: true });

            if (assembleError) {
              console.error(`❌ Error reassembling frames for ${file}:`, assembleError);
              console.error(`stderr: ${stderr}`);
              reject(assembleError);
              return;
            }

            console.log(`✅ Animated AVIF ${file} successfully processed with ${targetFrameRate} fps`);
            if (frameRateReduction) {
              console.log(`💾 Frame rate reduced from ${originalFrameRate} to ${targetFrameRate} fps`);
            }
            resolve();
          });
        } catch (processingError) {
          // Clean up temp directory
          if (fs.existsSync(tempDir)) {
            fs.rmSync(tempDir, { recursive: true, force: true });
          }
          console.error(`❌ Error processing frames for ${file}:`, processingError);
          reject(processingError);
        }
      });
    } catch (error) {
      console.error(`❌ Error in processAnimatedAvif for ${file}:`, error);
      reject(error);
    }
  });
}

/**
 * Process AVIF files - determine if animated or static and route accordingly.
 *
 * Uses multiple detection methods to determine if AVIF files contain multiple frames (animated) or single frame (static).
 * Routes to appropriate processing function based on animation detection results.
 *
 * Args:
 *
 * - `filePath` (`string`): The source AVIF file path.
 * - `outputFilePath` (`string`): The destination path for optimized AVIF.
 * - `file` (`string`): The original filename for logging purposes.
 * - `quality` (`boolean`): Quality setting flag.
 * - `maxSize` (`number|null`): Maximum width or height in pixels for resizing.
 *
 * Returns:
 *
 * - `Promise<void>`: Resolves when optimization is complete.
 *
 * Note:
 *
 * Uses isAvifAnimated() function for detection, which employs multiple fallback methods.
 * Animated AVIF files are processed with frame rate optimization and reassembly.
 * Static AVIF files are processed with ffmpeg for quality optimization.
 */
async function processAvif(filePath, outputFilePath, file, quality, maxSize) {
  const isAnimated = await isAvifAnimated(filePath);

  if (isAnimated) {
    console.log(`🎬 Detected animated AVIF: ${file}`);
    try {
      await processAnimatedAvif(filePath, outputFilePath, file, quality, maxSize);
    } catch (error) {
      console.error(`❌ Error processing animated AVIF ${file}:`, error);
    }
  } else {
    console.log(`🖼️ Detected static AVIF: ${file}.`);
    try {
      await processStaticAvif(filePath, outputFilePath, file, quality, maxSize);
    } catch (error) {
      console.error(`❌ Error processing static AVIF ${file}:`, error);
    }
  }
}

/**
 * Process static AVIF files - optimize existing static AVIF images using ffmpeg.
 *
 * Optimizes static AVIF images using ffmpeg with quality settings and optional resizing.
 * This function handles only single-frame AVIF images and ensures output contains exactly one frame.
 *
 * Args:
 *
 * - `filePath` (`string`): The source AVIF file path.
 * - `outputFilePath` (`string`): The destination path for optimized AVIF.
 * - `file` (`string`): The original filename for logging purposes.
 * - `quality` (`boolean`): Quality setting flag - if true uses CRF 18, otherwise CRF 28.
 * - `maxSize` (`number|null`): Maximum width or height in pixels for resizing.
 *
 * Returns:
 *
 * - `Promise<void>`: Resolves when optimization is complete.
 *
 * Note:
 *
 * Uses ffmpeg with libaom-av1 codec for re-encoding.
 * Quality settings: high quality CRF=18, standard quality CRF=28.
 * Includes scale filter for resizing while maintaining aspect ratio.
 * Forces single frame output with `-frames:v 1` parameter.
 */
async function processStaticAvif(filePath, outputFilePath, file, quality, maxSize) {
  return new Promise((resolve, reject) => {
    console.log(`🎯 Processing static AVIF with ffmpeg: ${file}...`);

    const crf = quality ? 18 : 28;

    // Build ffmpeg command for static image (single frame)
    let command = `ffmpeg -i "${filePath}" -c:v libaom-av1 -crf ${crf} -cpu-used 4 -pix_fmt yuv420p`;

    // Add scale filter if maxSize was specified
    if (maxSize) {
      command += ` -vf "scale='if(gt(iw,ih),min(${maxSize},iw),-1)':'if(gt(iw,ih),-1,min(${maxSize},ih))'"`;
    }

    // Important: ensure only one frame is output for static images
    command += ` -frames:v 1`;

    command += ` -y "${outputFilePath}"`;

    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error(`❌ Error processing static AVIF ${file}:`, error);
        console.error(`stderr: ${stderr}`);
        reject(error);
        return;
      }

      console.log(`✅ Static AVIF ${file} successfully processed with ffmpeg`);
      resolve();
    });
  });
}

/**
 * Optimize SVG files using SVGO library.
 *
 * Reads SVG files and applies SVGO optimization with default preset plugins.
 * Uses multipass optimization for better compression results.
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
 * Uses SVGO's "preset-default" plugin set with multipass enabled for thorough optimization.
 * All file operations are asynchronous using Node.js fs callbacks.
 * SVG files are not resized as they are vector-based and scalable by nature.
 * Preserves SVG structure while removing unnecessary elements and attributes.
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
 *
 * - JPG/JPEG/WEBP → AVIF conversion using Sharp
 * - GIF/MP4 → AVIF conversion via ffmpeg
 * - PNG → Optimization with Sharp/pngquant or AVIF conversion
 * - AVIF → Animation detection and appropriate optimization
 * - SVG → Optimization using SVGO
 * - Other formats → Skip with informational message
 *
 * Args:
 *
 * - `file` (`string`): The filename to process.
 * - `options` (`object`): Configuration object containing:
 *   - `imagesFolder` (`string`): Source folder path
 *   - `outputFolder` (`string`): Destination folder path
 *   - `quality` (`boolean`): Quality setting flag. Defaults to `false`.
 *   - `convertPngToAvif` (`boolean`): PNG to AVIF conversion flag. Defaults to `false`.
 *   - `maxSize` (`number|null`): Maximum width or height in pixels for resizing.
 *
 * Returns:
 *
 * - `Promise<void>`: Resolves when processing is complete or skipped.
 *
 * Note:
 *
 * Automatically skips directories. File extension detection is case-insensitive.
 * Output filenames preserve the original name but change the extension based on processing type.
 * All processing functions handle resizing internally if maxSize is specified.
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
 * Sets up folder paths based on CLI arguments or defaults, handles folder creation and cleanup,
 * and processes all images in the source folder sequentially.
 * Manages both default and custom folder configurations.
 *
 * Returns:
 *
 * - `Promise<void>`: Resolves when all images have been processed.
 *
 * Note:
 *
 * Default paths (relative to script location):
 *
 * - imagesFolder: "../../temp/images"
 * - outputFolder: "../../temp/optimized_images"
 *
 * Folder logic:
 *
 * - If no imagesFolder provided: uses defaults and clears output folder
 * - If imagesFolder provided but no outputFolder: creates "temp" subfolder in imagesFolder
 * - If both provided: uses custom paths without clearing
 *
 * Processes images sequentially to avoid overwhelming system resources.
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
