const grid = document.querySelector('#workout-grid');
const dialog = document.querySelector('#workout-dialog');
let workouts = [];

function card(w) {
  return `<article class="workout-card" data-category="${w.category}" tabindex="0"><div class="poster ${w.color}"><span class="poster-number">${w.id}</span><div class="poster-figure"><i></i><i></i><i></i></div>${w.completed ? '<span class="done">✓</span>' : ''}<button class="play" aria-label="Открыть тренировку">▶</button></div><div class="card-copy"><div><h3>${w.title}</h3><p>${w.group}</p></div><div class="meta"><span>${w.duration} мин</span><span>${w.level}</span></div></div></article>`;
}
function render(filter='all') {
  const visible = filter === 'all' ? workouts : workouts.filter(w => w.category === filter);
  grid.innerHTML = visible.map(card).join('');
  document.querySelector('#counter').textContent = `${visible.length} ${visible.length === 1 ? 'программа' : 'программ'}`;
  grid.querySelectorAll('.workout-card').forEach((el, i) => { el.onclick = () => openWorkout(visible[i]); el.onkeydown = e => e.key === 'Enter' && openWorkout(visible[i]); });
}
function openWorkout(w) {
  document.querySelector('#dialog-content').innerHTML = `<div class="dialog-poster ${w.color}"><span>${w.id}</span><button>▶</button></div><span class="eyebrow">${w.group}</span><h2>${w.title}</h2><p>${w.description}</p><div class="dialog-stats"><span><b>${w.duration}</b> минут</span><span><b>${w.exercises}</b> упражнений</span><span><b>${w.level}</b> уровень</span></div><button class="primary-button">Начать тренировку <b>→</b></button>`;
  dialog.showModal();
}
document.querySelector('.dialog-close').onclick = () => dialog.close();
dialog.onclick = e => { if (e.target === dialog) dialog.close(); };
document.querySelectorAll('.filter').forEach(button => button.onclick = () => { document.querySelector('.filter.active').classList.remove('active'); button.classList.add('active'); render(button.dataset.filter); });
document.querySelector('#logout').onclick = () => { sessionStorage.removeItem('form_demo'); location.href='./'; };
workouts = window.WORKOUTS || []; render();

