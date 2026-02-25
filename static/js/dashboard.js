document.addEventListener('DOMContentLoaded', function() {
    // Chart.js Defaults
    Chart.defaults.font.family = "'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
    Chart.defaults.color = '#777';

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
                    backgroundColor: chartData.categories.length ? [
                        '#009688', // Teal
                        '#4caf50', // Green
                        '#ff9800', // Orange
                        '#673ab7', // Purple
                        '#f44336'  // Red
                    ] : ['#e0e0e0'],
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
    const ctxBar = document.getElementById('trendBarChart').getContext('2d');
    new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [
                {
                    label: 'Expenses',
                    data: [1200, 1900, 1500, 1800, 1400, 2100],
                    backgroundColor: '#009688', // Teal
                    borderRadius: 4
                },
                {
                    label: 'Subscriptions',
                    data: [150, 150, 165, 165, 180, 180],
                    backgroundColor: '#673ab7', // Purple
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    align: 'end',
                    labels: {
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#e0e0e0',
                        drawBorder: false
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                },
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    }
                }
            }
        }
    });
});
