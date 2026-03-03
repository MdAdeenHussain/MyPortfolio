(function () {
    if (typeof Chart === "undefined" || typeof window.dashboardData === "undefined") {
        return;
    }

    const data = window.dashboardData;

    const defaultTextColor = getComputedStyle(document.documentElement).getPropertyValue("--text").trim() || "#dbeafe";
    const defaultGridColor = "rgba(148, 163, 184, 0.2)";

    const baseOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: defaultTextColor,
                    font: { family: "Nunito" },
                },
            },
        },
        scales: {
            x: {
                ticks: { color: defaultTextColor },
                grid: { color: defaultGridColor },
            },
            y: {
                ticks: { color: defaultTextColor },
                grid: { color: defaultGridColor },
            },
        },
    };

    const buildChart = (id, config) => {
        const node = document.getElementById(id);
        if (!node) {
            return;
        }
        new Chart(node, config);
    };

    buildChart("monthlyLeadsChart", {
        type: "line",
        data: {
            labels: data.months,
            datasets: [{
                label: "Leads",
                data: data.lead_points,
                borderColor: "#22d3ee",
                backgroundColor: "rgba(34, 211, 238, 0.2)",
                tension: 0.3,
                fill: true,
            }],
        },
        options: baseOptions,
    });

    buildChart("revenueChart", {
        type: "bar",
        data: {
            labels: data.months,
            datasets: [{
                label: "Revenue (INR)",
                data: data.revenue_points,
                backgroundColor: "rgba(139, 92, 246, 0.55)",
                borderColor: "#8b5cf6",
                borderWidth: 1,
            }],
        },
        options: baseOptions,
    });

    buildChart("planPieChart", {
        type: "pie",
        data: {
            labels: data.dist_labels,
            datasets: [{
                data: data.dist_values,
                backgroundColor: ["#22d3ee", "#8b5cf6", "#f59e0b", "#10b981", "#f43f5e", "#3b82f6"],
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: defaultTextColor },
                },
            },
        },
    });

    buildChart("serviceChart", {
        type: "doughnut",
        data: {
            labels: data.service_labels,
            datasets: [{
                data: data.service_values,
                backgroundColor: ["#22d3ee", "#a78bfa", "#fb7185", "#34d399", "#fbbf24", "#60a5fa"],
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: defaultTextColor },
                },
            },
        },
    });

    buildChart("trafficChart", {
        type: "bar",
        data: {
            labels: data.traffic.labels,
            datasets: [{
                label: "Traffic %",
                data: data.traffic.values,
                backgroundColor: "rgba(56, 189, 248, 0.45)",
                borderColor: "#22d3ee",
                borderWidth: 1,
            }],
        },
        options: baseOptions,
    });
})();
