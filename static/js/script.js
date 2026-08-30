/**
 * Student Data Analysis Studio – Client JavaScript
 * Interactive Chart.js rendering, dynamic section/grade filtering, search, and UI state.
 */

// Theme Toggle
function initThemeToggle() {
    const savedTheme = localStorage.getItem("theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
    
    const themeBtn = document.getElementById("themeToggleBtn");
    if (themeBtn) {
        themeBtn.innerHTML = savedTheme === "light" ? "🌙" : "☀️";
        themeBtn.addEventListener("click", () => {
            const currentTheme = document.documentElement.getAttribute("data-theme");
            const newTheme = currentTheme === "light" ? "dark" : "light";
            document.documentElement.setAttribute("data-theme", newTheme);
            localStorage.setItem("theme", newTheme);
            themeBtn.innerHTML = newTheme === "light" ? "🌙" : "☀️";
            // Re-render charts with appropriate theme colors if on dashboard
            if (window.renderDashboardCharts) {
                window.renderDashboardCharts();
            }
        });
    }
}

// Tab Switching
function initTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetId = btn.getAttribute("data-tab");
            
            tabBtns.forEach(b => b.classList.remove("active"));
            tabContents.forEach(c => c.style.display = "none");

            btn.classList.add("active");
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.style.display = "block";
            }
        });
    });
}

// Student Roster Dynamic Filtering & Search
function initStudentTableFilter() {
    const searchInput = document.getElementById("studentSearchInput");
    const sectionFilter = document.getElementById("sectionFilterSelect");
    const gradeFilter = document.getElementById("gradeFilterSelect");
    const statusFilter = document.getElementById("statusFilterSelect");
    const tableBody = document.getElementById("studentTableBody");

    if (!tableBody) return;

    function applyFilters() {
        const query = (searchInput ? searchInput.value : "").toLowerCase().trim();
        const selectedSec = sectionFilter ? sectionFilter.value : "ALL";
        const selectedGrade = gradeFilter ? gradeFilter.value : "ALL";
        const selectedStatus = statusFilter ? statusFilter.value : "ALL";

        const rows = tableBody.querySelectorAll("tr");
        let visibleCount = 0;

        rows.forEach(row => {
            const name = row.getAttribute("data-name") || "";
            const id = row.getAttribute("data-id") || "";
            const sec = row.getAttribute("data-section") || "";
            const grade = row.getAttribute("data-grade") || "";
            const status = row.getAttribute("data-status") || "";

            const matchesQuery = query === "" || name.includes(query) || id.includes(query);
            const matchesSec = selectedSec === "ALL" || sec === selectedSec;
            const matchesGrade = selectedGrade === "ALL" || grade === selectedGrade;
            const matchesStatus = selectedStatus === "ALL" || status === selectedStatus;

            if (matchesQuery && matchesSec && matchesGrade && matchesStatus) {
                row.style.display = "";
                visibleCount++;
            } else {
                row.style.display = "none";
            }
        });

        const countBadge = document.getElementById("studentVisibleCount");
        if (countBadge) {
            countBadge.innerText = `${visibleCount} students shown`;
        }
    }

    if (searchInput) searchInput.addEventListener("input", applyFilters);
    if (sectionFilter) sectionFilter.addEventListener("change", applyFilters);
    if (gradeFilter) gradeFilter.addEventListener("change", applyFilters);
    if (statusFilter) statusFilter.addEventListener("change", applyFilters);
}

// Drag and Drop File Upload
function initDropzone() {
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("fileInput");
    const fileNameDisplay = document.getElementById("fileNameDisplay");
    const uploadForm = document.getElementById("uploadForm");

    if (!dropzone || !fileInput) return;

    ["dragenter", "dragover"].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add("drag-active");
        });
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove("drag-active");
        });
    });

    dropzone.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            fileInput.files = files;
            updateFileName(files[0].name);
        }
    });

    dropzone.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            updateFileName(fileInput.files[0].name);
        }
    });

    function updateFileName(name) {
        if (fileNameDisplay) {
            fileNameDisplay.innerHTML = `<span class="badge badge-blue">Selected: ${name}</span>`;
        }
    }
}

// Chart.js Visualizations
window.chartInstances = {};

function renderDashboardCharts(chartData) {
    if (!chartData && window.DASHBOARD_CHART_DATA) {
        chartData = window.DASHBOARD_CHART_DATA;
    }
    if (!chartData || typeof Chart === "undefined") return;

    const isLight = document.documentElement.getAttribute("data-theme") === "light";
    const textColor = isLight ? "#1E293B" : "#F8FAFC";
    const gridColor = isLight ? "#E2E8F0" : "rgba(255, 255, 255, 0.08)";

    Chart.defaults.color = textColor;
    Chart.defaults.borderColor = gridColor;
    Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";

    // 1. Section Performance Chart
    const ctxSec = document.getElementById("chartSectionPerformance");
    if (ctxSec) {
        if (window.chartInstances.section) window.chartInstances.section.destroy();
        window.chartInstances.section = new Chart(ctxSec, {
            type: "bar",
            data: {
                labels: chartData.section_labels,
                datasets: [
                    {
                        label: "Average Score (%)",
                        data: chartData.section_avg,
                        backgroundColor: "rgba(59, 130, 246, 0.8)",
                        borderColor: "#3B82F6",
                        borderWidth: 1.5,
                        borderRadius: 6
                    },
                    {
                        label: "Pass Rate (%)",
                        data: chartData.section_pass,
                        backgroundColor: "rgba(16, 185, 129, 0.8)",
                        borderColor: "#10B981",
                        borderWidth: 1.5,
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, max: 100, ticks: { callback: v => v + "%" } }
                }
            }
        });
    }

    // 2. Subject Performance Chart
    const ctxSub = document.getElementById("chartSubjectPerformance");
    if (ctxSub) {
        if (window.chartInstances.subject) window.chartInstances.subject.destroy();
        window.chartInstances.subject = new Chart(ctxSub, {
            type: "bar",
            data: {
                labels: chartData.subject_labels,
                datasets: [
                    {
                        label: "Subject Average",
                        data: chartData.subject_avg,
                        backgroundColor: "rgba(139, 92, 246, 0.8)",
                        borderColor: "#8B5CF6",
                        borderWidth: 1.5,
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, max: 100 }
                }
            }
        });
    }

    // 3. Grade Distribution Doughnut Chart
    const ctxGrade = document.getElementById("chartGradeDist");
    if (ctxGrade) {
        if (window.chartInstances.grade) window.chartInstances.grade.destroy();
        window.chartInstances.grade = new Chart(ctxGrade, {
            type: "doughnut",
            data: {
                labels: chartData.grade_labels,
                datasets: [
                    {
                        data: chartData.grade_counts,
                        backgroundColor: [
                            "#10B981", "#34D399", "#3B82F6", "#60A5FA", "#F59E0B", "#FB923C", "#EF4444"
                        ],
                        borderWidth: 2,
                        borderColor: isLight ? "#FFFFFF" : "#111827"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "right" }
                }
            }
        });
    }

    // 4. Top Students Chart
    const ctxTop = document.getElementById("chartTopStudents");
    if (ctxTop) {
        if (window.chartInstances.top) window.chartInstances.top.destroy();
        window.chartInstances.top = new Chart(ctxTop, {
            type: "bar",
            data: {
                labels: chartData.top_labels,
                datasets: [
                    {
                        axis: 'y',
                        label: "Percentage Score (%)",
                        data: chartData.top_percentages,
                        backgroundColor: "rgba(6, 182, 212, 0.8)",
                        borderColor: "#06B6D4",
                        borderWidth: 1.5,
                        borderRadius: 6
                    }
                ]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { beginAtZero: true, max: 100, ticks: { callback: v => v + "%" } }
                }
            }
        });
    }
}

// Global initialization on DOM load
document.addEventListener("DOMContentLoaded", () => {
    initThemeToggle();
    initTabs();
    initDropzone();
    initStudentTableFilter();

    if (window.DASHBOARD_CHART_DATA) {
        renderDashboardCharts(window.DASHBOARD_CHART_DATA);
    }
});
