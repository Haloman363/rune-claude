# Exporting the 3D Lumbridge scene

`assets/scene/` is gitignored (27MB of Jagex-derived geometry). Regenerate it
with these steps. The renderer falls back to the 2D tile map without it.

## Requirements

- JDK 11+ (`sudo apt-get install openjdk-21-jdk`)

## 1. Build the exporter

```bash
git clone --depth 1 https://github.com/ConnorDY/OSRS-Environment-Exporter.git
cd OSRS-Environment-Exporter
./gradlew build -x test
```

Produces `build/libs/osrs-environment-exporter-fat-<version>.jar`.

## 2. Get an OSRS cache + XTEA keys

From the [OpenRS2 Archive](https://archive.openrs2.org/caches). Pick an
`oldschool` cache with high key coverage — this used **cache 2499, build 236**.

Note: the JSON reports `game: "oldschool"` but the download URLs use
`/caches/runescape/` — the `oldschool` path 404s.

```bash
curl -o disk.zip   https://archive.openrs2.org/caches/runescape/2499/disk.zip
curl -o keys.json  https://archive.openrs2.org/caches/runescape/2499/keys.json
unzip disk.zip -d osrsdir          # yields osrsdir/cache/
cp keys.json osrsdir/xteas.json    # already in the exporter's schema
printf 'param=25=236\n' > osrsdir/params.txt
```

`params.txt` holds the cache revision. Only param 25 is read, and it gates two
format branches (`readOverlayAsShort` >= 209, `shouldUseSingleFileTextures`
>= 234) — so it must match the cache's real build or parsing breaks.

## 3. Export region 12850 (Lumbridge)

```bash
java -jar build/libs/osrs-environment-exporter-fat-*.jar \
  --export --flat \
  --cache-dir /path/to/osrsdir \
  --export-dir /path/to/export-lumb \
  12850 1
```

`12850` = region (50, 50), covering game coords 3200–3263 — the same origin as
`assets/tiles/lumbridge.json`. `1` is the radius. An `ObjectLoader` warning
about an unrecognized opcode is expected and harmless.

## 4. Install into the project

```bash
mkdir -p assets/scene
cp export-lumb/scene.gltf export-lumb/data.bin assets/scene/
cp -r export-lumb/Textures assets/scene/
```

## Notes

- Output is glTF 2.0: 24 meshes, 208 textures, ~473k vertices.
- Geometry spans X 0..64, Z -64..0, Y = height — 1 unit per game tile.
- A **2009scape** (build 530) cache does *not* work: its config archives use a
  different encoding and `UnderlayLoader` fails. Use an OSRS cache.
