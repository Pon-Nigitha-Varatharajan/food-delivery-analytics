let foodChart, restaurantChart;

// Dynamic neon color generator for the charts
function generateColors(count) {
    const baseColors = [
        '#a78bfa', // Lavender
        '#c084fc', // Neon purple
        '#818cf8', // Indigo
        '#22d3ee', // Cyan
        '#38bdf8', // Sky Blue
        '#f472b6', // Pink
        '#fb7185', // Rose
    ];
    let colors = [];
    for(let i = 0; i < count; i++) {
        colors.push(baseColors[i % baseColors.length]);
    }
    return colors;
}

// Chart.js global defaults for Dark Theme
Chart.defaults.color = '#94a3b8';
Chart.defaults.font.family = "'Outfit', sans-serif";
Chart.defaults.scale.grid.color = 'rgba(255,255,255,0.05)';

// Animated number tick counter
function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = Math.floor(progress * (end - start) + start).toLocaleString();
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

let lastTotalOrders = 0;

// 🔥 AUTOMATIC ENVIRONMENT DETECTION
const hostname = window.location.hostname;
const API_BASE = (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '') 
    ? 'http://localhost:5000'   // Local Flask API runs on 5000
    : 'http://56.228.7.202:5001'; // Cloud Docker Flask API

async function loadData() {
    try {
        // 🔹 FOOD DATA
        let foodRes = await fetch(`${API_BASE}/food_trends`);
        let foodData = await foodRes.json();

        // Sort food ascending because we want largest bar at bottom or top, etc.
        // Actually, sort descending to show biggest trends
        foodData.sort((a, b) => b.count - a.count);

        let foodLabels = foodData.map(x => x.food_item.toUpperCase());
        let foodCounts = foodData.map(x => x.count);

        let totalOrders = foodCounts.reduce((a,b) => a+b, 0);

        // Animate the Top Orders counter instead of just replacing
        const totalOrdersEl = document.getElementById("totalOrders");
        animateValue(totalOrdersEl, lastTotalOrders, totalOrders, 800);
        lastTotalOrders = totalOrders;

        if (foodLabels.length > 0) {
            document.getElementById("topFood").innerText = foodLabels[0];
        }

        // 🍕 FOOD CHART (Bar)
        if (foodChart) {
            foodChart.data.labels = foodLabels;
            foodChart.data.datasets[0].data = foodCounts;
            foodChart.data.datasets[0].backgroundColor = generateColors(foodLabels.length);
            // Smooth update animation
            foodChart.update();
        } else {
            foodChart = new Chart(document.getElementById("foodChart"), {
                type: 'bar',
                data: {
                    labels: foodLabels,
                    datasets: [{
                        data: foodCounts,
                        backgroundColor: generateColors(foodLabels.length),
                        borderRadius: 6,
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: { duration: 800, easing: 'easeOutQuart' },
                    plugins: { 
                        legend: { display: false },
                        tooltip: { backgroundColor: 'rgba(11, 17, 35, 0.9)', titleColor: '#a78bfa', padding: 12 }
                    },
                    scales: {
                        y: { beginAtZero: true, border: {display: false} },
                        x: { grid: { display: false }, ticks: { font: {size: 10} } }
                    }
                }
            });
        }

        // 🔹 RESTAURANT DATA
        let resRes = await fetch(`${API_BASE}/restaurant_load`);
        let resData = await resRes.json();
        
        // Sort restaurants to make doughnut chart look cleaner
        resData.sort((a,b) => b.order_count - a.order_count);

        let resLabels = resData.map(x => "Kitchen-" + x.restaurant_id);
        let resCounts = resData.map(x => x.order_count);

        document.getElementById("totalRestaurants").innerText = resData.length;

        if (restaurantChart) {
            restaurantChart.data.labels = resLabels;
            restaurantChart.data.datasets[0].data = resCounts;
            restaurantChart.data.datasets[0].backgroundColor = generateColors(resLabels.length);
            restaurantChart.update();
        } else {
            restaurantChart = new Chart(document.getElementById("restaurantChart"), {
                type: 'doughnut',
                data: {
                    labels: resLabels,
                    datasets: [{
                        data: resCounts,
                        backgroundColor: generateColors(resLabels.length),
                        borderWidth: 2,
                        borderColor: '#0b1123',
                        hoverOffset: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: { duration: 800 },
                    cutout: '75%',
                    plugins: {
                        legend: { display: false },
                        tooltip: { backgroundColor: 'rgba(11, 17, 35, 0.9)' }
                    }
                }
            });
        }

        // 🧠 INSIGHTS (IAM Protected)
        let insightRes = await fetch(`${API_BASE}/insights`);
        let insights = await insightRes.json();

        if (insights.high_demand_food) {
            document.getElementById("highDemand").innerText = insights.high_demand_food.food_item.toUpperCase();
        }
        if (insights.overloaded_restaurant) {
            document.getElementById("overloaded").innerText = `Kitchen-${insights.overloaded_restaurant.restaurant_id}`;
        }
        
        // Populate prediction if allowed
        if (window.iamRole === "admin" && insights.prediction) {
            document.getElementById("prediction").innerText = insights.prediction;
        }

        // 🤖 AGENTIC AI: Populate Load Balancing Action if allowed
        if (window.iamRole === "admin" && insights.load_balancing) {
            let lbElement = document.getElementById("loadBalance");
            lbElement.innerText = insights.load_balancing.message;
            if (insights.load_balancing.status === "CRITICAL") {
                lbElement.className = "value highlight-warn text-glow pulse";
            } else {
                lbElement.className = "value highlight-neon";
            }
        }

        // 📍 CITY DATA
        let cityList = document.getElementById("cityList");
        cityList.innerHTML = "";

        if (insights.city_wise_demand) {
            // Sort by counts descending
            let sortedCities = insights.city_wise_demand.sort((a, b) => b.count - a.count);

            sortedCities.forEach(c => {
                let pill = document.createElement("div");
                pill.className = "city-pill";
                pill.innerHTML = `<span class="city-name">${c.city}</span> <span class="city-food">${c.top_food} (${c.count})</span>`;
                cityList.appendChild(pill);
            });
        }

    } catch (err) {
        console.error("API Fetch Error:", err);
    }
}

// --- IAM AUTHENTICATION LOGIC ---
window.iamRole = null;

function authenticateBase() {
    const user = document.getElementById("iamUsername").value.toLowerCase();
    
    if (user === "admin") {
        window.iamRole = "admin";
        unlockDashboard();
    } else if (user === "employee" || user === "user") {
        window.iamRole = "employee";
        
        // Instantly block UI elements before API even loads
        document.getElementById("prediction").innerText = "🔒 Blocked by IAM Policy";
        document.getElementById("prediction").className = "value highlight-warn";
        
        document.getElementById("loadBalance").innerText = "🔒 Blocked by IAM Policy";
        document.getElementById("loadBalance").className = "value highlight-warn";
        
        unlockDashboard();
    } else {
        document.getElementById("iamError").style.display = "block";
    }
}

function unlockDashboard() {
    document.getElementById("iamLoginOverlay").style.display = "none";
    document.getElementById("dashboardWrapper").style.display = "flex";
    
    // Initial Load & Refresh
    loadData();
    if (window.dataInterval) clearInterval(window.dataInterval);
    window.dataInterval = setInterval(loadData, 3000);
}