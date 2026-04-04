let foodChart, restaurantChart;

async function loadData() {

    console.log("Updated at:", new Date().toLocaleTimeString());

    try {
        // 🔹 FOOD DATA
        let foodRes = await fetch("http://localhost:5001/food_trends");
        let foodData = await foodRes.json();

        let foodLabels = foodData.map(x => x.food_item);
        let foodCounts = foodData.map(x => x.count);

        let totalOrders = foodCounts.reduce((a,b) => a+b, 0);
        let maxIndex = foodCounts.indexOf(Math.max(...foodCounts));

        document.getElementById("totalOrders").innerText = totalOrders;
        document.getElementById("topFood").innerText = foodLabels[maxIndex];

        // 🍕 FOOD CHART
        if (foodChart) {
            foodChart.data.labels = foodLabels;
            foodChart.data.datasets[0].data = foodCounts;
            foodChart.update('none');
        } else {
            foodChart = new Chart(document.getElementById("foodChart"), {
                type: 'bar',
                data: {
                    labels: foodLabels,
                    datasets: [{
                        data: foodCounts,
                        backgroundColor: ["#38bdf8","#6366f1","#22c55e","#facc15"]
                    }]
                },
                options: {
                    animation: false,
                    plugins: { legend: { display: false } }
                }
            });
        }

        // 🔹 RESTAURANT DATA
        let resRes = await fetch("http://localhost:5001/restaurant_load");
        let resData = await resRes.json();

        let resLabels = resData.map(x => "R" + x.restaurant_id);
        let resCounts = resData.map(x => x.order_count);

        document.getElementById("totalRestaurants").innerText = resData.length;

        if (restaurantChart) {
            restaurantChart.data.labels = resLabels;
            restaurantChart.data.datasets[0].data = resCounts;
            restaurantChart.update('none');
        } else {
            restaurantChart = new Chart(document.getElementById("restaurantChart"), {
                type: 'doughnut',
                data: {
                    labels: resLabels,
                    datasets: [{
                        data: resCounts,
                        backgroundColor: ["#38bdf8","#6366f1","#22c55e","#facc15","#f97316"]
                    }]
                },
                options: {
                    animation: false
                }
            });
        }

        // 🧠 INSIGHTS
        let insightRes = await fetch("http://localhost:5001/insights");
        let insights = await insightRes.json();

        document.getElementById("highDemand").innerText =
            ` High Demand: ${insights.high_demand_food.food_item}`;

        document.getElementById("overloaded").innerText =
            ` Overloaded Restaurant: R${insights.overloaded_restaurant.restaurant_id}`;

        document.getElementById("prediction").innerText =
            ` Prediction: ${insights.prediction}`;

        // 📍 CITY DATA
        let cityList = document.getElementById("cityList");
        cityList.innerHTML = "";

        insights.city_wise_demand.forEach(c => {
            let li = document.createElement("li");
            li.innerText = `${c.city} → ${c.top_food} (${c.count})`;
            cityList.appendChild(li);
        });

    } catch (err) {
        console.error(err);
    }
}

// 🔥 Refresh every 1 minute
if (window.dataInterval) clearInterval(window.dataInterval);
window.dataInterval = setInterval(loadData, 60000);

loadData();