// Chart.js configurations and utilities

// Common chart options
const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
        duration: 2000,
        easing: 'easeInOutQuart'
    },
    plugins: {
        legend: {
            position: 'bottom',
            labels: {
                font: {
                    family: "'Inter', sans-serif",
                    size: 12
                }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleFont: {
                family: "'Inter', sans-serif",
                size: 14
            },
            bodyFont: {
                family: "'Inter', sans-serif",
                size: 12
            }
        }
    }
};

// Gradient backgrounds
function createGradient(ctx, color1, color2) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, color1);
    gradient.addColorStop(1, color2);
    return gradient;
}

// Risk meter chart
function createRiskMeter(canvasId, riskScore) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Calculate angle (0 to 180 degrees, with 0 at left, 180 at right)
    const angle = (riskScore * 180) - 90;
    
    // Create gauge chart
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Low Risk', 'Medium Risk', 'High Risk'],
            datasets: [{
                data: [0.4, 0.3, 0.3],
                backgroundColor: [
                    createGradient(ctx, '#28a745', '#20c997'),
                    createGradient(ctx, '#ffc107', '#fd7e14'),
                    createGradient(ctx, '#dc3545', '#c82333')
                ],
                borderWidth: 0,
                circumference: 180,
                rotation: 270
            }]
        },
        options: {
            ...chartOptions,
            cutout: '70%',
            plugins: {
                ...chartOptions.plugins,
                tooltip: { enabled: false },
                legend: { display: false }
            }
        }
    });
    
    // Add needle
    const needle = document.createElement('div');
    needle.className = 'needle';
    needle.style.transform = `rotate(${angle}deg)`;
    document.querySelector(`#${canvasId}`).parentNode.appendChild(needle);
}

// Performance trend chart
function createTrendChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Performance',
                data: data,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 3,
                pointBackgroundColor: '#764ba2',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            ...chartOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    title: {
                        display: true,
                        text: 'Score (%)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Attendance heatmap
function createHeatmap(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Prepare data for heatmap (simplified as bar chart with gradient)
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const attendanceData = data || [85, 92, 78, 95, 88, 70, 45];
    
    const backgroundColors = attendanceData.map(value => {
        if (value >= 80) return 'rgba(40, 167, 69, 0.7)';
        if (value >= 60) return 'rgba(255, 193, 7, 0.7)';
        return 'rgba(220, 53, 69, 0.7)';
    });
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: days,
            datasets: [{
                label: 'Attendance %',
                data: attendanceData,
                backgroundColor: backgroundColors,
                borderRadius: 5
            }]
        },
        options: {
            ...chartOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Attendance %'
                    }
                }
            },
            plugins: {
                ...chartOptions.plugins,
                legend: { display: false }
            }
        }
    });
}

// Module performance comparison
function createModuleComparisonChart(canvasId, modules, averages) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: modules,
            datasets: [{
                label: 'Class Average',
                data: averages,
                backgroundColor: 'rgba(102, 126, 234, 0.2)',
                borderColor: '#667eea',
                pointBackgroundColor: '#667eea',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#667eea'
            }]
        },
        options: {
            ...chartOptions,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20
                    }
                }
            }
        }
    });
}

// Risk distribution pie chart
function createRiskPieChart(canvasId, low, medium, high) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Low Risk', 'Medium Risk', 'High Risk'],
            datasets: [{
                data: [low, medium, high],
                backgroundColor: ['#28a745', '#ffc107', '#dc3545'],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            ...chartOptions,
            plugins: {
                ...chartOptions.plugins,
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// GPA distribution histogram
function createGPAHistogram(canvasId, gpaData) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Bin the GPA data
    const bins = [0, 1, 2, 3, 4];
    const counts = new Array(bins.length - 1).fill(0);
    
    gpaData.forEach(gpa => {
        for (let i = 0; i < bins.length - 1; i++) {
            if (gpa >= bins[i] && gpa < bins[i + 1]) {
                counts[i]++;
                break;
            }
        }
    });
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['0-1.0', '1.0-2.0', '2.0-3.0', '3.0-4.0'],
            datasets: [{
                label: 'Number of Students',
                data: counts,
                backgroundColor: 'rgba(102, 126, 234, 0.7)',
                borderColor: '#667eea',
                borderWidth: 1
            }]
        },
        options: {
            ...chartOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Student Count'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'GPA Range'
                    }
                }
            }
        }
    });
}

// Export chart functions
window.Charts = {
    createRiskMeter,
    createTrendChart,
    createHeatmap,
    createModuleComparisonChart,
    createRiskPieChart,
    createGPAHistogram
};