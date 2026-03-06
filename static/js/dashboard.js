document.addEventListener('DOMContentLoaded', function() {
    // Chart.js Defaults
    Chart.defaults.font.family = "'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
    // use CSS variable for chart text color so dark mode applies
    const _css = getComputedStyle(document.documentElement);
    Chart.defaults.color = (_css.getPropertyValue('--text-muted') || '#777').trim();

    // 1. Category Pie Chart
    const ctxPie = document.getElementById('categoryPieChart');
    if (ctxPie) {
        const chartData = window.dashboardChartData || { categories: [], category_amounts: [] };
        
        new Chart(ctxPie.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: chartData.categories.length ? chartData.categories : ['No Data'],
                datasets: [{
                    data: chartData.category_amounts.length ? chartData.category_amounts : [1],
                    backgroundColor: chartData.categories.length ? (
                        // map to theme variables where possible, fallback to sensible defaults
                        [
                            _css.getPropertyValue('--accent-green').trim() || '#009688',
                            _css.getPropertyValue('--accent-green-dark').trim() || '#4caf50',
                            _css.getPropertyValue('--positive').trim() || '#ff9800',
                            _css.getPropertyValue('--accent-purple').trim() || '#673ab7',
                            _css.getPropertyValue('--negative').trim() || '#f44336'
                        ]
                    ) : ['#e0e0e0'],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }

    // 2. Monthly Trend Bar Chart
    const trendCanvas = document.getElementById('trendBarChart');
    if (trendCanvas) {
        // Read color variables from CSS to keep palette consistent
        const css = getComputedStyle(document.documentElement);
    const accentGreen = css.getPropertyValue('--accent-green').trim() || '#7aa57a';
    const accentPurple = css.getPropertyValue('--accent-purple').trim() || '#6b5fa3';
    const gridColor = css.getPropertyValue('--border-color').trim() || '#e9e7e5';
    const accentBlue = css.getPropertyValue('--accent-2').trim() || '#1e88e5';

        // controls
        const monthsSelect = document.getElementById('trend-months');
        const refreshBtn = document.getElementById('trend-refresh');

        function fetchAndRender(monthsCount) {
            fetch(`/api/trends?months=${monthsCount}`)
                .then(r => r.json())
                .then(trendData => {
                    const datasets = [
                        { label: 'Expenses', data: trendData.expenses, backgroundColor: accentGreen, borderRadius: 6 },
                        { label: 'Subscriptions', data: trendData.subscriptions, backgroundColor: accentPurple, borderRadius: 6 }
                    ];
                    if (trendData.incomes && trendData.incomes.some(v => v > 0)) {
                        datasets.push({ label: 'Incomes', data: trendData.incomes, backgroundColor: accentBlue, borderRadius: 6 });
                    }

                    if (window._trendChart) window._trendChart.destroy();

                    window._trendChart = new Chart(trendCanvas.getContext('2d'), {
                        type: 'bar',
                        data: {
                            labels: trendData.labels,
                            datasets: datasets
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    position: 'top',
                                    align: 'end',
                                    labels: { usePointStyle: true, pointStyle: 'circle' }
                                },
                                tooltip: {
                                    callbacks: {
                                        label: function(context) {
                                            const v = context.parsed.y || 0;
                                            return context.dataset.label + ': MAD ' + v.toLocaleString();
                                        }
                                    }
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    grid: { color: gridColor, drawBorder: false },
                                    ticks: {
                                        callback: function(value) {
                                            if (Number.isInteger(value)) return 'MAD ' + value.toLocaleString();
                                            return value;
                                        }
                                    }
                                },
                                x: { grid: { display: false, drawBorder: false } }
                            }
                        }
                    });
                })
                .catch(err => console.error('Failed to load trends', err));
        }

        // initial load
        fetchAndRender(monthsSelect ? monthsSelect.value : 6);
        if (monthsSelect) monthsSelect.addEventListener('change', function() { fetchAndRender(this.value); });
        if (refreshBtn) refreshBtn.addEventListener('click', function(e) { e.preventDefault(); fetchAndRender(monthsSelect ? monthsSelect.value : 6); });
    }
});
