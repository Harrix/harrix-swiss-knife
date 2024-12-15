import imagemin from "imagemin";
import imageminMozjpeg from "imagemin-mozjpeg";
import imageminPngquant from "imagemin-pngquant";
import imageminGifsicle from "imagemin-gifsicle";
import imageminWebp from "imagemin-webp";
import imageminSvgo from "imagemin-svgo";

function optimizeFiles(extension, imageminPlugin) {
  let path = process.argv.slice(2)[0];
  path = !!path ? path : "images/";
  if (path.slice(-1) != "/") path += "/";
  let destinationPath = path + "/optimized/";

  (async () => {
    let files = await imagemin([path + extension], {
      destination: destinationPath,
      plugins: [imageminPlugin],
    });

    console.log(extension + ":");
    console.log(files);
  })();
}

//optimizeFiles("*.{jpg,jpeg}", imageminMozjpeg({ quality: 90, progressive: true }));
optimizeFiles("*.{jpg,jpeg}", imageminWebp({ quality: 80, method: 6 }));
optimizeFiles("*.png", imageminPngquant());
optimizeFiles("*.gif", imageminGifsicle());
optimizeFiles("*.webp", imageminWebp({ quality: 80, method: 6 }));
optimizeFiles(
  "*.svg",
  imageminSvgo({
    plugins: [
      {
        name: "preset-default",
        params: {
          overrides: {
            cleanupIDs: {
              force: true,
            },
          },
        },
      },
    ],
  })
);
