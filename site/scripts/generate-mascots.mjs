import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createAvatar } from "@dicebear/core";
import { bottts } from "@dicebear/collection";
import { toPng } from "@dicebear/converter";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const outputDir = path.resolve(__dirname, "../public/assets/generated");

const mascots = [
  {
    fileStem: "superior-mascot-core",
    seed: "Superior Core",
    title: "Core mascot",
    options: {
      baseColor: ["19dcff"],
      face: ["square03"],
      top: ["radar"],
      sides: ["square"],
      texture: ["circuits"],
      eyes: ["sensor"],
      mouth: ["diagram"],
    },
  },
  {
    fileStem: "superior-mascot-scout",
    seed: "Superior Scout",
    title: "Scout mascot",
    options: {
      baseColor: ["ffd84a"],
      face: ["square02"],
      top: ["lights"],
      sides: ["antenna02"],
      texture: ["dots"],
      eyes: ["robocop"],
      mouth: ["grill01"],
    },
  },
  {
    fileStem: "superior-mascot-pilot",
    seed: "Superior Pilot",
    title: "Pilot mascot",
    options: {
      baseColor: ["ff33cc"],
      face: ["round02"],
      top: ["bulb01"],
      sides: ["round"],
      texture: ["circuits"],
      eyes: ["glow"],
      mouth: ["square02"],
    },
  },
];

function createBotMascot(seed, options) {
  return createAvatar(bottts, {
    seed,
    size: 512,
    radius: 0,
    backgroundColor: ["0a1230"],
    topProbability: 100,
    sidesProbability: 100,
    textureProbability: 100,
    mouthProbability: 100,
    ...options,
  });
}

async function writeMascotFiles({ fileStem, seed, options }) {
  const avatar = createBotMascot(seed, options);
  const svgOutput = avatar.toString();
  const pngOutput = await toPng(avatar);
  const pngBuffer = Buffer.from(await pngOutput.toArrayBuffer());

  await writeFile(path.join(outputDir, `${fileStem}.svg`), svgOutput, "utf8");
  await writeFile(path.join(outputDir, `${fileStem}.png`), pngBuffer);
}

async function main() {
  await mkdir(outputDir, { recursive: true });

  for (const mascot of mascots) {
    await writeMascotFiles(mascot);
  }

  const manifest = {
    generator: "DiceBear bottts",
    createdAt: new Date().toISOString(),
    mascots: mascots.map(({ fileStem, seed, title }) => ({
      title,
      seed,
      svg: `/assets/generated/${fileStem}.svg`,
      png: `/assets/generated/${fileStem}.png`,
    })),
  };

  await writeFile(
    path.join(outputDir, "superior-mascot-manifest.json"),
    `${JSON.stringify(manifest, null, 2)}\n`,
    "utf8"
  );

  console.log(`Generated ${mascots.length} mascot variants in ${outputDir}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
