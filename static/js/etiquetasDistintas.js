document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  if (!form) return;

  form.addEventListener("submit", function (event) {
    const tec1 = document.getElementById("tecnologias").value;
    const tec2 = document.getElementById("tecnologias2").value;
    const hab1 = document.getElementById("habilidades").value;
    const hab2 = document.getElementById("habilidades2").value;

    if (tec1 && tec2 && tec1 === tec2) {
      alert("Tecnología 2 no puede ser igual a Tecnología 1");
      event.preventDefault();
      return;
    }

    if (hab1 && hab2 && hab1 === hab2) {
      alert("Habilidad 2 no puede ser igual a Habilidad 1");
      event.preventDefault();
      return;
    }
  });

  // Carrusel simple para la página de etiquetas
  // Muestra solo una tabla a la vez y navega con los botones

  const charts = document.querySelectorAll('.carousel-chart');
  let currentChartIndex = 0;

  function showChart(index) {
    charts.forEach((chart, i) => {
      chart.style.display = (i === index) ? 'block' : 'none';
    });
    document.getElementById('prevChart').disabled = index === 0;
    document.getElementById('nextChart').disabled = index === charts.length - 1;
  }

  document.getElementById('prevChart').addEventListener('click', () => {
    if (currentChartIndex > 0) {
      currentChartIndex--;
      showChart(currentChartIndex);
    }
  });

  document.getElementById('nextChart').addEventListener('click', () => {
    if (currentChartIndex < charts.length - 1) {
      currentChartIndex++;
      showChart(currentChartIndex);
    }
  });

  // Inicializa el carrusel
  showChart(currentChartIndex);
});

// Corrige el comportamiento para que solo la tabla activa esté visible
// y nunca se muestren dos a la vez

document.addEventListener('DOMContentLoaded', function () {
  const charts = document.querySelectorAll('.carousel-chart');
  let currentChartIndex = 0;

  function showChart(index) {
    charts.forEach((chart, i) => {
      chart.classList.toggle('active', i === index);
    });
    document.getElementById('prevChart').disabled = index === 0;
    document.getElementById('nextChart').disabled = index === charts.length - 1;
  }

  document.getElementById('prevChart').addEventListener('click', () => {
    if (currentChartIndex > 0) {
      currentChartIndex--;
      showChart(currentChartIndex);
    }
  });

  document.getElementById('nextChart').addEventListener('click', () => {
    if (currentChartIndex < charts.length - 1) {
      currentChartIndex++;
      showChart(currentChartIndex);
    }
  });

  // Quitar el focus visual del botón del carrusel al hacer clic
  document.querySelectorAll('.carousel-arrow').forEach(function (btn) {
    btn.addEventListener('mouseup', function () {
      this.blur();
    });
  });

  // Inicializa el carrusel
  showChart(currentChartIndex);
});
document.querySelectorAll('.input-num-custom').forEach(function(wrapper) {
  const input = wrapper.querySelector('.input-importancia');
  wrapper.querySelector('.menos').onclick = function() {
    input.stepDown();
    input.dispatchEvent(new Event('input'));
  };
  wrapper.querySelector('.mas').onclick = function() {
    input.stepUp();
    input.dispatchEvent(new Event('input'));
  };
});