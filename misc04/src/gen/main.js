const { createCanvas, loadImage, registerFont } = require("canvas");
const fs = require("fs");
const tqdm = require("tqdm");

require("dotenv").config();

const FLAG = process.env.FLAG;

const frames = 60;
const pixel_size = 5;
const scale_factor = 0.4;
const fontSize = 350;
const font = `${fontSize}px Helvetica`;
const chars = 8;
const width = frames * 30;
const height = frames * 30;

registerFont("./Helvetica-Bold.ttf", { family: "Helvetica" });

function getTextWidth() {
  let ctx = createCanvas(1, 1).getContext("2d");
  ctx.font = font;
  return Math.ceil(ctx.measureText(FLAG.substring(0, chars)).width);
}

function getTextPixels() {
  let canvas = createCanvas(width, height);
  let ctx = canvas.getContext("2d");
  let text_pixels = [];

  ctx.fillStyle = "white";
  ctx.textBaseline = "middle";
  ctx.font = font;
  const lines = FLAG.match(new RegExp(`.{1,${chars}}`, "g")) || [];
  lines.forEach((line, index) => {
    ctx.fillText(line, 0, fontSize + index * fontSize);
  });

  const imageData = ctx.getImageData(0, 0, width, height).data;

  for (let x = 0; x < width; x += pixel_size) {
    for (let y = 0; y < height; y += pixel_size) {
      let index = (y * width + x) * 4;
      let brightness = imageData[index] > 0 ? 255 : 0;
      if (brightness > 0) {
        text_pixels.push({ x, y, color: Math.random() > 0.5 ? 0 : 255 });
      }
    }
  }

  return text_pixels;
}

function drawBackground(ctx, grid, rows, cols, shiftAmount) {
  const first = grid.slice(0, shiftAmount);
  for (let x = 0; x < cols - shiftAmount; x++) {
    for (let y = 0; y < rows; y++) {
      grid[x][y] = grid[x + shiftAmount][y];
    }
  }
  for (let x = 0; x < shiftAmount; x++) {
    for (let y = 0; y < rows; y++) {
      grid[cols - shiftAmount + x][y] = first[x][y];
    }
  }

  for (let x = 0; x < cols; x++) {
    for (let y = 0; y < rows; y++) {
      ctx.fillStyle = `rgb(${grid[x][y]}, ${grid[x][y]}, ${grid[x][y]})`;
      ctx.fillRect(x * pixel_size, y * pixel_size, pixel_size, pixel_size);
    }
  }
}

function drawText(ctx, text_pixels, dx, dy) {
  for (let p of text_pixels) {
    ctx.fillStyle = `rgb(${p.color}, ${p.color}, ${p.color})`;
    ctx.fillRect(p.x + dx, p.y + dy, pixel_size, pixel_size);
  }
}

function getResizedCanvas(canvas) {
  let resizedCanvas = createCanvas(width * scale_factor, height * scale_factor);
  resizedCtx = resizedCanvas.getContext("2d");
  resizedCtx.drawImage(
    canvas,
    0,
    0,
    width * scale_factor,
    height * scale_factor,
  );
  return resizedCanvas;
}

function main() {
  const canvas = createCanvas(width, height);
  const ctx = canvas.getContext("2d");
  const cols = Math.floor(width / pixel_size);
  const rows = Math.floor(height / pixel_size);
  const text_pixels = getTextPixels(width, height);

  let grid = Array.from({ length: cols }, () =>
    Array.from({ length: rows }, () => (Math.random() > 0.5 ? 0 : 255)),
  );

  console.log("Generating assets...");
  for (let i of tqdm(Array.from({ length: frames }).keys(), {
    total: frames,
  })) {
    drawBackground(ctx, grid, rows, cols, width / pixel_size / frames);
    drawText(
      ctx,
      text_pixels,
      pixel_size * Math.ceil((width - getTextWidth()) / 2 / pixel_size),
      0,
    );
    fs.writeFileSync(
      `./assets/image${i}.png`,
      getResizedCanvas(canvas, width, height).toBuffer("image/png"),
    );
  }
}

if (require.main === module) {
  main();
}
