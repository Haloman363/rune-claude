const ORB_DEFS = [
  { name: 'hp',     label: 'HP',   value: 99  },
  { name: 'prayer', label: 'Pray', value: 99  },
  { name: 'run',    label: 'Run',  value: 100 },
  { name: 'spec',   label: 'Spec', value: 100 },
]

function initMinimap() {
  document.querySelectorAll('.orb img[data-orb]').forEach(img => {
    const name = img.dataset.orb
    img.src = ASSETS + '/icons/ui/orbs/orb_' + name + '.png'
    img.onerror = () => { img.style.display = 'none' }
  })
}
