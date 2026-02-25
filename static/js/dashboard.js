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
    const trendCanvas = document.getElementById('trendBarChart');
    if (trendCanvas) {
        // Read color variables from CSS to keep palette consistent
        const css = getComputedStyle(document.documentElement);
        const accentGreen = css.getPropertyValue('--accent-green').trim() || '#7aa57a';
        const accentPurple = css.getPropertyValue('--accent-purple').trim() || '#6b5fa3';
        const gridColor = css.getPropertyValue('--border-color').trim() || '#e9e7e5';

        const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        const trendData = window.dashboardTrendData || {
            labels: months.slice(0,6),
            expenses: [1200, 1900, 1500, 1800, 1400, 2100],
            subscriptions: [150, 150, 165, 165, 180, 180]
        };

        new Chart(trendCanvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: trendData.labels,
                datasets: [
                    {
                        label: 'Expenses',
                        data: trendData.expenses,
                        backgroundColor: accentGreen,
                        borderRadius: 6
                    },
                    {
                        label: 'Subscriptions',
                        data: trendData.subscriptions,
                        backgroundColor: accentPurple,
                        borderRadius: 6
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
                        grid: {
                            color: gridColor,
                            drawBorder: false
                        },
                        ticks: {
                            callback: function(value) {
                                // Format tick values as Moroccan Dirham (MAD)
                                if (Number.isInteger(value)) {
                                    return 'MAD ' + value.toLocaleString();
                                }
                                return value;
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
    }
});
