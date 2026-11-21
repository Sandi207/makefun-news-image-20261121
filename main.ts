const { mkdirSync: mk, copyFileSync: cp } = require('node:fs');
const { resolve } = require('node:path');

function put(at) {
  const pic = resolve(at, 'entry.png');
  mk(at, { recursive: true });
  cp(resolve(__dirname, 'entry.png'), pic);
  process.stdout.write('Wrote ' + pic + '\n');
}

put(resolve(process.env['MAKEFUN_OUTPUT_DIR'] || '/output'));
