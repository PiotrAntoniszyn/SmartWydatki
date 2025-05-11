// Client-side validation and UX for login form
(() => {
  const form = document.getElementById('login-form');
  const emailInput = document.getElementById('login-email');
  const passwordInput = document.getElementById('login-password');
  const togglePasswordBtn = document.getElementById('togglePassword');

  if (!form) return;

  // Toggle password visibility
  togglePasswordBtn?.addEventListener('click', () => {
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);
    togglePasswordBtn.querySelector('i')?.classList.toggle('bi-eye');
    togglePasswordBtn.querySelector('i')?.classList.toggle('bi-eye-slash');
  });

  // HTML5 validation with Bootstrap styling
  form.addEventListener('submit', (event) => {
    if (!form.checkValidity()) {
      event.preventDefault();
      event.stopPropagation();
    }
    form.classList.add('was-validated');
  }, false);
})(); 