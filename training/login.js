const form = document.querySelector('#login-form');
const error = document.querySelector('#login-error');
form.addEventListener('submit', event => {
  event.preventDefault(); error.textContent = '';
  const button = form.querySelector('button[type=submit]'); button.disabled = true; button.querySelector('span').textContent = 'Проверяем…';
  if (form.username.value.trim() === 'glebadmin' && form.password.value === 'admingleb1!') {
    sessionStorage.setItem('form_demo', '1'); location.href = './app.html'; return;
  }
  error.textContent = 'Неверный код или пароль'; button.disabled = false; button.querySelector('span').textContent = 'Войти в платформу';
});
