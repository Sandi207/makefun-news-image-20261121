// Place the bundled entry image in the chosen output directory.
const fileSystem = require("node:fs");
const paths = require("node:path");

const deliveryFolder = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const bundledImage = paths.join(__dirname, "entry.png");
const writtenImage = paths.join(deliveryFolder, "entry.png");

fileSystem.mkdirSync(deliveryFolder, { recursive: true });
fileSystem.copyFileSync(bundledImage, writtenImage);

console.log("Wrote image to " + writtenImage);
