document.addEventListener('DOMContentLoaded', function() {
  const inputs = document.querySelectorAll('input[type=number]');
  inputs.forEach(function(input) {
    input.addEventListener('change', function() {
      const max = parseInt(this.getAttribute('max'));
      if (parseInt(this.value) > max) {
        alert('Los minutos no pueden superar ' + max);
        this.value = max;
      }
      if (parseInt(this.value) < 0) this.value = 0;
    });
  });
});