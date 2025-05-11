// Client-side validation for register form
(() => {
  const form = document.getElementById('register-form');
  const password = document.getElementById('register-password');
  const confirmPassword = document.getElementById('register-password-confirm');
  const togglePasswordBtn = document.getElementById('togglePasswordRegister');

  if (!form) return;

  // Toggle password visibility
  togglePasswordBtn?.addEventListener('click', () => {
    const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
    password.setAttribute('type', type);
    confirmPassword.setAttribute('type', type);
    togglePasswordBtn.querySelector('i')?.classList.toggle('bi-eye');
    togglePasswordBtn.querySelector('i')?.classList.toggle('bi-eye-slash');
  });

  // Password match validation
  const validatePasswords = () => {
    if (password.value !== confirmPassword.value) {
      confirmPassword.setCustomValidity('Hasła nie są identyczne');
    } else {
      confirmPassword.setCustomValidity('');
    }
  };

  password.addEventListener('input', validatePasswords);
  confirmPassword.addEventListener('input', validatePasswords);

  form.addEventListener('submit', (event) => {
    validatePasswords();
    if (!form.checkValidity()) {
      event.preventDefault();
      event.stopPropagation();
    }
    form.classList.add('was-validated');
  }, false);
})(); 