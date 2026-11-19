// news-image-20261118 entry program (Node 22, standard library only).
//
// The entry image lives beside this file as entry.png. This program first
// verifies the image against the competition gate — PNG or JPEG magic bytes,
// at most 1 MiB, at most 1024x1024 pixels — and only then copies it to the
// output directory as entry.png. It runs offline and deterministically:
// the same input bytes always produce the same output bytes.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const MAX_BYTES = 1_048_576; // 1 MiB
const MAX_DIM = 1024;

const here = dirname(fileURLToPath(import.meta.url));
const sourcePath = join(here, 'entry.png');
const bytes = readFileSync(sourcePath);

function fail(message) {
  console.error(`entry check failed: ${message}`);
  process.exit(1);
}

if (bytes.length === 0) fail('entry.png is empty');
if (bytes.length > MAX_BYTES) {
  fail(`entry.png is ${bytes.length} bytes, over the ${MAX_BYTES}-byte limit`);
}

// Identify the format from magic bytes; the file name stays entry.png either way.
const isPng =
  bytes.length >= 8 &&
  bytes[0] === 0x89 && bytes[1] === 0x50 && bytes[2] === 0x4e && bytes[3] === 0x47 &&
  bytes[4] === 0x0d && bytes[5] === 0x0a && bytes[6] === 0x1a && bytes[7] === 0x0a;
const isJpeg = bytes.length >= 3 && bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff;

function pngDimensions(buf) {
  // IHDR is the first chunk: width and height are big-endian uint32 at 16 and 20.
  if (buf.length < 24 || buf.toString('ascii', 12, 16) !== 'IHDR') {
    fail('PNG is missing its IHDR chunk');
  }
  return [buf.readUInt32BE(16), buf.readUInt32BE(20)];
}

function jpegDimensions(buf) {
  // Walk the segments until a Start Of Frame marker (C0-CF except C4, C8, CC).
  let offset = 2;
  while (offset + 4 <= buf.length) {
    if (buf[offset] !== 0xff) fail('JPEG segment does not start with a marker');
    const marker = buf[offset + 1];
    if (marker === 0xd9) break;
    const length = buf.readUInt16BE(offset + 2);
    if (length < 2) fail('JPEG segment has an invalid length');
    const isSof =
      marker >= 0xc0 && marker <= 0xcf && marker !== 0xc4 && marker !== 0xc8 && marker !== 0xcc;
    if (isSof) {
      if (offset + 9 > buf.length) fail('JPEG SOF segment is truncated');
      return [buf.readUInt16BE(offset + 7), buf.readUInt16BE(offset + 5)]; // width, height
    }
    offset += 2 + length;
  }
  fail('no JPEG Start Of Frame segment found');
  return [0, 0];
}

let width, height;
if (isPng) {
  [width, height] = pngDimensions(bytes);
} else if (isJpeg) {
  [width, height] = jpegDimensions(bytes);
} else {
  fail('entry.png is neither a PNG nor a JPEG (bad magic bytes)');
}
if (width < 1 || height < 1) fail(`implausible dimensions ${width}x${height}`);
if (width > MAX_DIM || height > MAX_DIM) {
  fail(`image is ${width}x${height}, over the ${MAX_DIM}x${MAX_DIM} limit`);
}

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
const outPath = join(outDir, 'entry.png');
copyFileSync(sourcePath, outPath);
console.log(`wrote ${outPath}: ${isPng ? 'PNG' : 'JPEG'} ${width}x${height}, ${bytes.length} bytes`);
