// ─── 3D Lumbridge viewport ───────────────────────────────────────────────────
// Static camera over real OSRS geometry exported from the game cache
// (assets/scene/scene.gltf). Agents are billboard sprites placed on the terrain.
//
// The glTF is one 64x64 OSRS region: X runs 0..64, Z runs -64..0, Y is height.
// That's 1 unit per game tile, so tile coords map straight onto world coords.
import * as THREE from '/vendor/three.module.min.js'
import { GLTFLoader } from '/vendor/GLTFLoader.js'

const REGION = 64          // tiles per region axis
const POLL_MS = 500

// Canvas size, kept in sync with COLS*TILE x ROWS*TILE in viewport.js.
const VIEW_W = 768
const VIEW_H = 496

// Agent positions are viewport-local tile coords (0..47 x 0..30), the same grid
// the 2D renderer uses — not absolute game coords. Spread them over the region.
const AGENT_COLS = 48
const AGENT_ROWS = 31


let scene, camera, renderer, raf
let terrain = null
let worldState = { agents: {}, tick: -1 }
const agentSprites = {}   // id -> THREE.Sprite
let heightSampler = null

// ─── Tile -> world ────────────────────────────────────────────────────────────
// Map the 48x31 agent grid onto the 64x64 region. X grows east (+X), rows grow
// south (-Z in the exporter's frame).
function tileToWorld(col, row) {
  return {
    x: (col / AGENT_COLS) * REGION,
    z: -(row / AGENT_ROWS) * REGION,
  }
}

// ─── Terrain height lookup ────────────────────────────────────────────────────
// Raycast straight down to sit sprites on the ground instead of floating.
function makeHeightSampler(root) {
  const ray = new THREE.Raycaster()
  const down = new THREE.Vector3(0, -1, 0)
  const from = new THREE.Vector3()
  return (x, z) => {
    from.set(x, 100, z)
    ray.set(from, down)
    const hits = ray.intersectObject(root, true)
    return hits.length ? hits[0].point.y : 0
  }
}

// ─── Agent sprite ─────────────────────────────────────────────────────────────
// Canvas-drawn billboard: colored body + initials, matching the 2D renderer's
// look until real character sprites land.
function makeAgentTexture(color, initials) {
  const c = document.createElement('canvas')
  c.width = c.height = 64
  const ctx = c.getContext('2d')
  ctx.fillStyle = color
  ctx.fillRect(16, 8, 32, 48)
  ctx.strokeStyle = '#18140c'
  ctx.lineWidth = 3
  ctx.strokeRect(16, 8, 32, 48)
  ctx.fillStyle = '#18140c'
  ctx.font = 'bold 22px monospace'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(initials, 32, 32)
  const tex = new THREE.CanvasTexture(c)
  tex.magFilter = THREE.NearestFilter
  tex.minFilter = THREE.NearestFilter
  return tex
}

function ensureSprite(id, agent) {
  if (agentSprites[id]) return agentSprites[id]
  const initials = (agent.name || '?').slice(0, 2).toUpperCase()
  const mat = new THREE.SpriteMaterial({
    map: makeAgentTexture(agent.color || '#ffcc00', initials),
    depthTest: true,
  })
  const s = new THREE.Sprite(mat)
  s.scale.set(1.6, 1.6, 1.6)
  scene.add(s)
  agentSprites[id] = s
  return s
}

// ─── Poll ─────────────────────────────────────────────────────────────────────
async function pollState() {
  try {
    const r = await fetch('/api/viewport/state')
    if (!r.ok) return
    worldState = await r.json()
  } catch (_) { /* server down — keep last state */ }
}

// ─── Frame ────────────────────────────────────────────────────────────────────
function updateAgents() {
  const agents = worldState.agents || {}
  for (const [id, agent] of Object.entries(agents)) {
    const s = ensureSprite(id, agent)
    const { x, z } = tileToWorld(agent.position[0], agent.position[1])
    const groundY = heightSampler ? heightSampler(x, z) : 0
    const bob = agent.status === 'working' ? Math.sin(Date.now() / 200) * 0.08 : 0
    s.position.set(x, groundY + 0.9 + bob, z)
  }
  for (const id of Object.keys(agentSprites)) {
    if (!agents[id]) {
      scene.remove(agentSprites[id])
      agentSprites[id].material.map?.dispose()
      agentSprites[id].material.dispose()
      delete agentSprites[id]
    }
  }
}

function animate() {
  raf = requestAnimationFrame(animate)
  updateAgents()
  renderer.render(scene, camera)
}

// ─── Init ─────────────────────────────────────────────────────────────────────
export async function initViewport3D(canvas) {
  // The canvas may still report the 300x150 default at module-eval time (CSS
  // layout not resolved, viewport.js not run yet), so pin the known viewport
  // size rather than measuring. Matches COLS*TILE x ROWS*TILE in viewport.js.
  const w = VIEW_W
  const h = VIEW_H
  canvas.width = w
  canvas.height = h

  renderer = new THREE.WebGLRenderer({ canvas, antialias: false })
  renderer.setPixelRatio(1)
  renderer.setSize(w, h, false)
  renderer.setViewport(0, 0, w, h)

  scene = new THREE.Scene()
  scene.background = new THREE.Color('#18140c')

  // Static three-quarter view, roughly the OSRS angle. Position is set once the
  // scene loads and its real bounds are known.
  camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 500)
  camera.aspect = w / h
  camera.updateProjectionMatrix()

  scene.add(new THREE.AmbientLight(0xffffff, 1.6))
  const sun = new THREE.DirectionalLight(0xffffff, 1.2)
  sun.position.set(1, 2, 1)
  scene.add(sun)

  const gltf = await new GLTFLoader().loadAsync('/assets/scene/scene.gltf')
  terrain = gltf.scene
  // Exporter emits unlit vertex-colored meshes; keep textures crisp.
  terrain.traverse((o) => {
    if (o.isMesh && o.material.map) {
      o.material.map.magFilter = THREE.NearestFilter
      o.material.map.minFilter = THREE.NearestFilter
    }
  })
  scene.add(terrain)
  heightSampler = makeHeightSampler(terrain)

  // Frame the camera from the real geometry bounds rather than assuming where
  // the exporter put the region — it varies with the chosen radius.
  const box = new THREE.Box3().setFromObject(terrain)
  const centre = box.getCenter(new THREE.Vector3())
  const size = box.getSize(new THREE.Vector3())
  const span = Math.max(size.x, size.z)
  // Pull back far enough that the whole region fits the vertical FOV.
  // Fit the horizontal extent too — the viewport is wider than it is tall.
  const vFov = camera.fov * Math.PI / 180
  const hFov = 2 * Math.atan(Math.tan(vFov / 2) * camera.aspect)
  const dist = Math.max(
    (size.z / 2) / Math.tan(vFov / 2),
    (size.x / 2) / Math.tan(hFov / 2),
  ) * 1.05
  camera.position.set(centre.x, centre.y + dist * 0.72, centre.z + dist * 0.72)
  camera.lookAt(centre)
  camera.updateProjectionMatrix()
  console.log('bounds', size.toArray(), 'centre', centre.toArray(),
    'aspect', camera.aspect, 'dist', dist)

  await pollState()
  setInterval(pollState, POLL_MS)
  animate()

  return { scene, camera, renderer }
}

export function disposeViewport3D() {
  if (raf) cancelAnimationFrame(raf)
  renderer?.dispose()
}
