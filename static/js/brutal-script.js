document.addEventListener('DOMContentLoaded', function() {
  // Add fade-in animation to main content
  const main = document.querySelector('main');
  if (main) {
    main.classList.add('fade-in');
  }

  // Smooth scrolling for navigation links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      document.querySelector(this.getAttribute('href')).scrollIntoView({
        behavior: 'smooth'
      });
    });
  });

  // File input enhancement
  const fileInputs = document.querySelectorAll('input[type="file"]');
  fileInputs.forEach(input => {
    const fileNameDisplay = document.createElement('span');
    fileNameDisplay.classList.add('file-name-display');
    input.parentNode.insertBefore(fileNameDisplay, input.nextSibling);

    input.addEventListener('change', function(e) {
      if (this.files && this.files[0]) {
        fileNameDisplay.textContent = this.files[0].name;
      } else {
        fileNameDisplay.textContent = '';
      }
    });
  });

  // Form submission animation
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      this.classList.add('submitting');
      const submitButton = this.querySelector('button[type="submit"]');
      if (submitButton) {
        const originalText = submitButton.textContent;
        submitButton.textContent = 'Procesando...';
        setTimeout(() => {
          this.classList.remove('submitting');
          submitButton.textContent = originalText;
        }, 2000);
      }
    });
  });

  // Tiendas gourmet checkbox enhancement
  const tiendasList = document.getElementById('tiendas-list');
  if (tiendasList) {
    tiendasList.addEventListener('change', function(e) {
      if (e.target.type === 'checkbox') {
        e.target.closest('label').classList.toggle('selected', e.target.checked);
      }
    });
  }

  // Table row hover effect
  const tables = document.querySelectorAll('table');
  tables.forEach(table => {
    table.addEventListener('mouseover', function(e) {
      if (e.target.tagName === 'TD') {
        e.target.parentElement.classList.add('hover');
      }
    });
    table.addEventListener('mouseout', function(e) {
      if (e.target.tagName === 'TD') {
        e.target.parentElement.classList.remove('hover');
      }
    });
  });

  // Chart interaction (if charts are present)
  if (typeof Chart !== 'undefined') {
    const charts = document.querySelectorAll('canvas');
    charts.forEach(chart => {
      chart.addEventListener('mousemove', function(event) {
        const activePoints = Chart.getElementsAtEventForMode(event, 'nearest', { intersect: true }, true);
        if (activePoints.length > 0) {
          const firstPoint = activePoints[0];
          const label = this.chart.data.labels[firstPoint.index];
          const value = this.chart.data.datasets[firstPoint.datasetIndex].data[firstPoint.index];
          this.style.cursor = 'pointer';
          this.title = `${label}: ${value}`;
        } else {
          this.style.cursor = 'default';
          this.title = '';
        }
      });
    });
  }

  // Responsive menu toggle
  const menuToggle = document.createElement('button');
  menuToggle.textContent = '☰';
  menuToggle.classList.add('menu-toggle');
  menuToggle.setAttribute('aria-label', 'Toggle menu');
  const nav = document.querySelector('nav');
  if (nav) {
    nav.appendChild(menuToggle);
    menuToggle.addEventListener('click', function() {
      nav.classList.toggle('show-menu');
    });
  }

  // Date picker initialization
  const monthPicker = document.getElementById('month-picker');
  const feriadosPicker = document.getElementById('feriados');
  let flatpickrInstance;

  if (monthPicker && feriadosPicker) {
    monthPicker.addEventListener('change', function () {
      const [year, month] = this.value.split('-');
      const lastDay = new Date(year, month, 0).getDate();

      if (flatpickrInstance) {
        flatpickrInstance.destroy();
      }

      flatpickrInstance = flatpickr(feriadosPicker, {
        mode: "multiple",
        dateFormat: "Y-m-d",
        locale: "es",
        minDate: `${year}-${month}-01`,
        maxDate: `${year}-${month}-${lastDay}`,
        inline: true,
        onChange: function (selectedDates) {
          feriadosPicker.value = selectedDates.map(date => date.getDate()).join(',');
        }
      });
    });
  }
});

// Función para cargar tiendas
async function cargarTiendas(input) {
  const file = input.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('/obtener_tiendas', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) throw new Error('Error al cargar tiendas');

    const tiendas = await response.json();
    const container = document.getElementById('tiendas-list');
    container.innerHTML = '';

    tiendas.forEach(tienda => {
      const div = document.createElement('div');
      div.className = 'tienda-item';
      div.innerHTML = `
        <label>
          <input type="checkbox" name="tiendas_gourmet" value="${tienda}">
          <span>${tienda}</span>
        </label>
      `;
      container.appendChild(div);
    });

    document.getElementById('tiendas-container').style.display = 'block';

  } catch (error) {
    console.error('Error:', error);
    alert('Error al cargar las tiendas');
  }
}