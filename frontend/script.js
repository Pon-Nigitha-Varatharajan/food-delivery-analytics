let foodChart, restaurantChart;

// Dynamic neon color generator
function generateColors(count) {
    const baseColors = [
        '#a78bfa',
        '#c084fc',
        '#818cf8',
        '#22d3ee',
        '#38bdf8',
        '#f472b6',
        '#fb7185',
    ];
    let colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(baseColors[i % baseColors.length]);
    }
    return colors;
}

// Chart defaults
Chart.defaults.color = '#94a3b8';
Chart.defaults.font.family = "'Outfit', sans-serif";
Chart.defaults.scale.grid.color = 'rgba(255,255,255,0.05)';

// Counter animation
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

async function loadData() {
    try {
        // 🔹 FOOD DATA
        let foodRes = await fetch("http://localhost:5001/food_trends");
        let foodData = await foodRes.json();

        foodData.sort((a, b) => b.count - a.count);

        let foodLabels = foodData.map(x => x.food_item.toUpperCase());
        let foodCounts = foodData.map(x => x.count);

        let totalOrders = foodCounts.reduce((a, b) => a + b, 0);

        animateValue(document.getElementById("totalOrders"), lastTotalOrders, totalOrders, 800);
        lastTotalOrders = totalOrders;

        if (foodLabels.length > 0) {
            document.getElementById("topFood").innerText = foodLabels[0];
        }

        // 🍕 FOOD CHART
        if (foodChart) {
            foodChart.data.labels = foodLabels;
            foodChart.data.datasets[0].data = foodCounts;
            foodChart.data.datasets[0].backgroundColor = generateColors(foodLabels.length);
            foodChart.update();
        } else {
            foodChart = new Chart(document.getElementById("foodChart"), {
                type: 'bar',
                data: {
                    labels: foodLabels,
                    datasets: [{
                        data: foodCounts,
                        backgroundColor: generateColors(foodLabels.length),
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: { duration: 800 },
                    plugins: { legend: { display: false } }
                }
            });
        }

        // 🔹 RESTAURANT DATA
        let resRes = await fetch("http://localhost:5001/restaurant_load");
        let resData = await resRes.json();

        resData.sort((a, b) => b.order_count - a.order_count);

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
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '75%',
                    plugins: { legend: { display: false } }
                }
            });
        }

        // 🧠 INSIGHTS (🔥 AGENTIC AI)
        let insightRes = await fetch("http://localhost:5001/insights");
        let insights = await insightRes.json();

        if (insights.high_demand_food) {
            document.getElementById("highDemand").innerText =
                insights.high_demand_food.food_item.toUpperCase();
        }

        if (insights.overloaded_restaurant) {
            document.getElementById("overloaded").innerText =
                `Kitchen-${insights.overloaded_restaurant.restaurant_id}`;
        }

        if (insights.prediction) {
            document.getElementById("prediction").innerText =
                insights.prediction;
        }

        // 🤖 LOAD BALANCING DISPLAY (NEW)
        if (insights.load_balancing) {
            document.getElementById("loadBalance").innerText =
                insights.load_balancing.message;
        } else {
            document.getElementById("loadBalance").innerText =
                "All kitchens operating normally ✅";
        }

        // 📍 CITY DATA
        let cityList = document.getElementById("cityList");
        cityList.innerHTML = "";

        let sortedCities = insights.city_wise_demand.sort((a, b) => b.count - a.count);

        sortedCities.forEach(c => {
            let li = document.createElement("li");

            let cityName = document.createElement("span");
            cityName.innerText = c.city;

            let dishWrap = document.createElement("span");
            dishWrap.innerHTML =
                `<span style="color:#a78bfa; font-weight:600;">${c.top_food.toUpperCase()}</span> (${c.count})`;

            li.appendChild(cityName);
            li.appendChild(dishWrap);
            cityList.appendChild(li);
        });

    } catch (err) {
        console.error("API Fetch Error:", err);
    }
}

// 🔥 REAL-TIME REFRESH
if (window.dataInterval) clearInterval(window.dataInterval);
window.dataInterval = setInterval(loadData, 3000);

// Initial load
setTimeout(loadData, 500);