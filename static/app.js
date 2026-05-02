document.addEventListener('DOMContentLoaded', function () {
  const inputs = document.querySelectorAll('input[type="number"]');

  inputs.forEach(function (input) {
    let error = input.parentElement.querySelector('.error-text');

    if (!error) {
      error = document.createElement('small');
      error.className = 'error-text';
      error.style.display = 'none';
      input.parentElement.appendChild(error);
    }

    input.addEventListener('input', function () {
      const max = parseInt(this.getAttribute('max'), 10);
      let value = parseInt(this.value, 10);

      if (isNaN(value)) {
        this.classList.remove('input-error');
        error.style.display = 'none';
        error.textContent = '';
        return;
      }

      if (value > max) {
        this.value = max;
        this.classList.add('input-error');
        error.textContent = 'Los minutos no pueden superar ' + max + '.';
        error.style.display = 'block';
        return;
      }

      if (value < 0) {
        this.value = 0;
        this.classList.add('input-error');
        error.textContent = 'Los minutos no pueden ser negativos.';
        error.style.display = 'block';
        return;
      }

      this.classList.remove('input-error');
      error.style.display = 'none';
      error.textContent = '';
    });
  });
});