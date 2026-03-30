document.addEventListener('DOMContentLoaded', async () => {
  // Load config and trigger login sound
  try {
    const config = await apiGet('/config')
    if (config.sounds_enabled) {
      playSound('login_music')
    }
    if (config.chat_font_size) {
      document.documentElement.style.setProperty('--chat-font-size', config.chat_font_size + 'px')
    }
    if (config.control_font_size) {
      document.documentElement.style.setProperty('--control-font-size', config.control_font_size + 'px')
    }
  } catch(e) {}

  initViewport()
  initMinimap()
  initChatbox()
  initPanel()
})
