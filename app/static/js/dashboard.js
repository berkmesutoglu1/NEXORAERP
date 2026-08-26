// NEXORA ERP - Dashboard Chart.js Initialization Script

document.addEventListener('DOMContentLoaded', function () {
  const salesChartCtx = document.getElementById('monthlySalesChart');
  const topProductsChartCtx = document.getElementById('topProductsChart');
  const categoryChartCtx = document.getElementById('categorySalesChart');
  const warehouseChartCtx = document.getElementById('warehouseStockChart');

  if (!salesChartCtx) return; // Exit if not on dashboard

  fetch('/api/charts/dashboard-analytics')
    .then(response => response.json())
    .then(data => {
      renderMonthlySalesChart(salesChartCtx, data.monthly_sales);
      renderTopProductsChart(topProductsChartCtx, data.top_products);
      renderCategorySalesChart(categoryChartCtx, data.category_sales);
      renderWarehouseStockChart(warehouseChartCtx, data.warehouse_stocks);
    })
    .catch(error => console.error("Error loading dashboard analytics charts:", error));
});

function renderMonthlySalesChart(ctx, salesData) {
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: salesData.labels,
      datasets: [{
        label: 'Aylık Satış Tutarı (₺)',
        data: salesData.data,
        borderColor: '#2563eb',
        backgroundColor: 'rgba(37, 99, 235, 0.1)',
        fill: true,
        tension: 0.35,
        borderWidth: 3,
        pointBackgroundColor: '#2563eb',
        pointRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) { return '₺' + value.toLocaleString('tr-TR'); }
          }
        }
      }
    }
  });
}

function renderTopProductsChart(ctx, productData) {
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: productData.labels,
      datasets: [{
        label: 'Satılan Miktar',
        data: productData.data,
        backgroundColor: '#0d9488',
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } }
    }
  });
}

function renderCategorySalesChart(ctx, catData) {
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: catData.labels,
      datasets: [{
        data: catData.data,
        backgroundColor: [
          '#2563eb', '#0d9488', '#7c3aed', '#f59e0b', '#ef4444', '#10b981'
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  });
}

function renderWarehouseStockChart(ctx, whData) {
  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: whData.labels,
      datasets: [{
        data: whData.data,
        backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6']
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  });
}
