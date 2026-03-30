let musicState = { playing: false, current_track: null, current_index: 0 }
let trackList = []
let musicPollInterval = null

function renderMusicPanel(container) {
  // Stop any previous poll
  if (musicPollInterval) { clearInterval(musicPollInterval); musicPollInterval = null }

  const panel = document.createElement('div')
  panel.id = 'music-panel'

  // Source row
  const sourceRow = document.createElement('div')
  sourceRow.id = 'music-source-row'
  const btnOsrs = document.createElement('button')
  btnOsrs.className = 'src-btn'
  btnOsrs.id = 'src-osrs'
  btnOsrs.textContent = 'OSRS Tracks'
  const btnCustom = document.createElement('button')
  btnCustom.className = 'src-btn'
  btnCustom.id = 'src-custom'
  btnCustom.textContent = 'Custom Folder'
  sourceRow.appendChild(btnOsrs)
  sourceRow.appendChild(btnCustom)
  panel.appendChild(sourceRow)

  // Now playing
  const nowPlaying = document.createElement('div')
  nowPlaying.id = 'music-now-playing'
  nowPlaying.textContent = 'Now Playing: \u2014'
  panel.appendChild(nowPlaying)

  // Controls
  const controls = document.createElement('div')
  controls.id = 'music-controls'
  ;[
    ['music-prev', '\u25C4\u25C4'],
    ['music-play', '\u25BA'],
    ['music-next', '\u25BA\u25BA'],
    ['music-stop', '\u25A0'],
  ].forEach(([id, label]) => {
    const btn = document.createElement('button')
    btn.className = 'ctrl-btn'
    btn.id = id
    btn.textContent = label
    controls.appendChild(btn)
  })
  const volLabel = document.createElement('span')
  volLabel.id = 'music-vol-label'
  volLabel.textContent = 'Vol: 80%'
  controls.appendChild(volLabel)
  panel.appendChild(controls)

  // Track list
  const trackListEl = document.createElement('div')
  trackListEl.id = 'music-track-list'
  panel.appendChild(trackListEl)

  // Custom dir row
  const dirRow = document.createElement('div')
  dirRow.id = 'custom-dir-row'
  const dirLabel = document.createElement('label')
  dirLabel.textContent = 'Folder:'
  const dirInput = document.createElement('input')
  dirInput.id = 'custom-dir-input'
  dirInput.type = 'text'
  dirInput.placeholder = 'path/to/music'
  dirInput.spellcheck = false
  dirRow.appendChild(dirLabel)
  dirRow.appendChild(dirInput)
  panel.appendChild(dirRow)

  container.appendChild(panel)

  // Load config to set initial state
  apiGet('/config').then(cfg => {
    const src = cfg.music_source || 'osrs'
    if (src === 'osrs') btnOsrs.classList.add('active')
    else btnCustom.classList.add('active')
    const vol = cfg.music_volume || 80
    volLabel.textContent = 'Vol: ' + vol + '%'
    dirInput.value = cfg.custom_music_dir || ''
  }).catch(() => {})

  // Wire buttons
  btnOsrs.onclick = () => setMusicSource('osrs', '')
  btnCustom.onclick = () => setMusicSource('custom', dirInput.value)

  document.getElementById('music-prev').onclick = () =>
    apiPost('/music/play', { action: 'prev' }).then(refreshMusicStatus).catch(() => {})
  document.getElementById('music-next').onclick = () =>
    apiPost('/music/play', { action: 'next' }).then(refreshMusicStatus).catch(() => {})
  document.getElementById('music-stop').onclick = () =>
    apiPost('/music/play', { action: 'stop' }).then(refreshMusicStatus).catch(() => {})
  document.getElementById('music-play').onclick = () => {
    if (musicState.playing) {
      apiPost('/music/play', { action: 'stop' }).then(refreshMusicStatus).catch(() => {})
    } else if (trackList.length > 0) {
      apiPost('/music/play', { index: musicState.current_index }).then(refreshMusicStatus).catch(() => {})
    }
  }

  dirInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      setMusicSource('custom', dirInput.value.trim())
    }
  })

  refreshMusicStatus()
  loadMusicTracks()
  musicPollInterval = setInterval(refreshMusicStatus, 2000)
}

function setMusicSource(src, dir) {
  const body = { source: src }
  if (dir) body.dir = dir
  apiPost('/music/source', body).then(() => {
    document.querySelectorAll('.src-btn').forEach(b => b.classList.remove('active'))
    const activeBtn = document.getElementById('src-' + src)
    if (activeBtn) activeBtn.classList.add('active')
    loadMusicTracks()
  }).catch(() => {})
}

async function refreshMusicStatus() {
  try {
    musicState = await apiGet('/music/status')
    const np = document.getElementById('music-now-playing')
    if (np) np.textContent = 'Now Playing: ' + (musicState.current_track || '\u2014')
    const playBtn = document.getElementById('music-play')
    if (playBtn) playBtn.textContent = musicState.playing ? '\u2759\u2759' : '\u25BA'
    updateMusicTrackHighlight()
  } catch(e) {}
}

async function loadMusicTracks() {
  try {
    trackList = await apiGet('/music/tracks')
    renderMusicTrackList()
  } catch(e) {}
}

function renderMusicTrackList() {
  const container = document.getElementById('music-track-list')
  if (!container) return
  container.textContent = ''
  trackList.forEach((track, i) => {
    const item = document.createElement('div')
    item.className = 'track-item' + (track.name === musicState.current_track ? ' playing' : '')
    item.dataset.index = i

    const cachedMark = document.createElement('span')
    cachedMark.className = 'track-cached'
    cachedMark.textContent = track.is_cached ? '\u2713' : ' '

    const nameSpan = document.createElement('span')
    nameSpan.textContent = track.name

    item.appendChild(cachedMark)
    item.appendChild(nameSpan)
    item.onclick = () => {
      apiPost('/music/play', { index: i }).then(refreshMusicStatus).catch(() => {})
    }
    container.appendChild(item)
  })
}

function updateMusicTrackHighlight() {
  document.querySelectorAll('.track-item').forEach((el, i) => {
    const t = trackList[i]
    if (t) {
      el.classList.toggle('playing', t.name === musicState.current_track)
    }
  })
}
