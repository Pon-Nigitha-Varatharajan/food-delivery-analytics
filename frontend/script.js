/* ═══════════════════════════════════════════
   NEURALBITES — script.js
   Environment-aware API, Charts, IAM, City Pills
   ═══════════════════════════════════════════ */

let foodChart, restaurantChart;
let lastTotalOrders = 0;

// ── Neon color palette ──
const COLORS = [
    '#a78bfa', '#c084fc', '#818cf8',
    '#22d3ee', '#38bdf8', '#f472b6', '#fb7185'
];
function genColors(n) {
    return Array.from({ length: n }, (_, i) => COLORS[i % COLORS.length]);
}

// ── Chart.js dark theme defaults ──
Chart.defaults.color          = '#64748b';
Chart.defaults.font.family    = "'Outfit', sans-serif";
Chart.defaults.scale.grid.color = 'rgba(255,255,255,0.04)';

// ── Animated ticker counter ──
function animateCount(el, start, end, ms) {
    let t0 = null;
    const step = ts => {
        if (!t0) t0 = ts;
        const p = Math.min((ts - t0) / ms, 1);
        el.textContent = Math.floor(p * (end - start) + start).toLocaleString();
        if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
}

// ── Environment detection ──
const hostname = window.location.hostname;
const API_BASE = (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '')
    ? 'http://localhost:5000'
    : 'http://56.228.7.202:5001';

// ═══════════════════════════════════════════
//  MAIN DATA FETCH
// ═══════════════════════════════════════════
async function loadData() {
    try {

        /* ── Food Trends ── */
        const foodData = await fetch(`${API_BASE}/food_trends`).then(r => r.json());
        foodData.sort((a, b) => b.count - a.count);

        const foodLabels = foodData.map(x => x.food_item.toUpperCase());
        const foodCounts = foodData.map(x => x.count);
        const totalOrders = foodCounts.reduce((a, b) => a + b, 0);

        animateCount(document.getElementById('totalOrders'), lastTotalOrders, totalOrders, 700);
        lastTotalOrders = totalOrders;

        if (foodLabels.length > 0) {
            document.getElementById('topFood').textContent = foodLabels[0];
        }

        if (foodChart) {
            foodChart.data.labels                        = foodLabels;
            foodChart.data.datasets[0].data              = foodCounts;
            foodChart.data.datasets[0].backgroundColor   = genColors(foodLabels.length);
            foodChart.update('active');
        } else {
            foodChart = new Chart(document.getElementById('foodChart'), {
                type: 'bar',
                data: {
                    labels: foodLabels,
                    datasets: [{
                        data: foodCounts,
                        backgroundColor: genColors(foodLabels.length),
                        borderRadius: 6,
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: { duration: 700, easing: 'easeOutQuart' },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: 'rgba(7,9,19,0.95)',
                            titleColor: '#a78bfa',
                            bodyColor: '#94a3b8',
                            padding: 12,
                            borderColor: 'rgba(139,92,246,0.3)',
                            borderWidth: 1
                        }
                    },
                    scales: {
                        y: { beginAtZero: true, border: { display: false } },
                        x: { grid: { display: false }, ticks: { font: { size: 9 } } }
                    }
                }
            });
        }

        /* ── Restaurant Load ── */
        const resData = await fetch(`${API_BASE}/restaurant_load`).then(r => r.json());
        resData.sort((a, b) => b.order_count - a.order_count);

        const resLabels = resData.map(x => 'Kitchen-' + x.restaurant_id);
        const resCounts = resData.map(x => x.order_count);

        document.getElementById('totalRestaurants').textContent = resData.length;

        if (restaurantChart) {
            restaurantChart.data.labels                      = resLabels;
            restaurantChart.data.datasets[0].data            = resCounts;
            restaurantChart.data.datasets[0].backgroundColor = genColors(resLabels.length);
            restaurantChart.update('active');
        } else {
            restaurantChart = new Chart(document.getElementById('restaurantChart'), {
                type: 'doughnut',
                data: {
                    labels: resLabels,
                    datasets: [{
                        data: resCounts,
                        backgroundColor: genColors(resLabels.length),
                        borderWidth: 2,
                        borderColor: '#070913',
                        hoverOffset: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: { duration: 700 },
                    cutout: '72%',
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: 'rgba(7,9,19,0.95)',
                            bodyColor: '#94a3b8',
                            padding: 10
                        }
                    }
                }
            });
        }

        /* ── Insights (IAM protected) ── */
        const insights = await fetch(`${API_BASE}/insights`).then(r => r.json());

        if (insights.high_demand_food) {
            document.getElementById('highDemand').textContent =
                insights.high_demand_food.food_item.toUpperCase();
        }
        if (insights.overloaded_restaurant) {
            document.getElementById('overloaded').textContent =
                `Kitchen-${insights.overloaded_restaurant.restaurant_id}`;
        }

        if (window.iamRole === 'admin') {
            if (insights.prediction) {
                document.getElementById('prediction').textContent = insights.prediction;
            }
            if (insights.load_balancing) {
                const lb = document.getElementById('loadBalance');
                lb.textContent = insights.load_balancing.message;
                lb.className = insights.load_balancing.status === 'CRITICAL'
                    ? 'icard-value red'
                    : 'icard-value cyan';
            }
        }

        /* ── City Pills ── */
        if (insights.city_wise_demand && insights.city_wise_demand.length > 0) {
            const sorted = [...insights.city_wise_demand].sort((a, b) => b.count - a.count);
            const cityList = document.getElementById('cityList');
            cityList.innerHTML = '';
            sorted.forEach(c => {
                const pill = document.createElement('div');
                pill.className = 'city-pill';
                pill.innerHTML =
                    `<span class="pill-city">${c.city}</span>` +
                    `<span class="pill-food">${c.top_food}</span>` +
                    `<span class="pill-count">${c.count}</span>`;
                cityList.appendChild(pill);
            });
        }

    } catch (err) {
        console.error('API error:', err);
    }
}

// ═══════════════════════════════════════════
//  IAM AUTHENTICATION
// ═══════════════════════════════════════════
window.iamRole = null;

function authenticateBase() {
    const user = document.getElementById('iamUsername').value.trim().toLowerCase();

    if (user === 'admin') {
        window.iamRole = 'admin';
        unlockDashboard();

    } else if (user === 'employee' || user === 'user') {
        window.iamRole = 'employee';

        // Block sensitive fields immediately
        ['prediction', 'loadBalance'].forEach(id => {
            const el = document.getElementById(id);
            el.textContent = '🔒 Blocked by IAM Policy';
            el.className = 'icard-value red';
        });

        unlockDashboard();

    } else {
        document.getElementById('iamError').style.display = 'block';
    }
}

function unlockDashboard() {
    document.getElementById('iamLoginOverlay').style.display = 'none';
    document.getElementById('dashboardWrapper').style.display = 'flex';
    loadData();
    if (window.dataInterval) clearInterval(window.dataInterval);
    window.dataInterval = setInterval(loadData, 3000);
}