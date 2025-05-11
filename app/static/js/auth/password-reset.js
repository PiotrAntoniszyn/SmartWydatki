(() => {
  const form = document.getElementById('reset-form');
  if (!form) return;
  form.addEventListener('submit', (event) => {
    if (!form.checkValidity()) {
      event.preventDefault();
      event.stopPropagation();
    }
    form.classList.add('was-validated');
  });
})(); 