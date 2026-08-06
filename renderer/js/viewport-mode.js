// Claims the game canvas for the WebGL renderer before viewport.js starts its
// 2D loop. Separate file (not inline) because index.html enforces a strict CSP.
// viewport3d-boot.js flips this back to false if WebGL init fails.
window.RUNE_VIEWPORT_3D = true
