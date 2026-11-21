'use strict';

const fs = require('node:fs');
const path = require('node:path');

const outputDirectory = process.env.MAKEFUN_OUTPUT_DIR || '/output';
fs.mkdirSync(outputDirectory, { recursive: true });
const destination = path.join(outputDirectory, 'entry.png');
fs.copyFileSync(path.join(__dirname, 'entry.png'), destination);
console.log(`Wrote ${destination}`);
