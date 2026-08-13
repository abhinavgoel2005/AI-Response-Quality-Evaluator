document.addEventListener("DOMContentLoaded", function () {

    // =========================================================
    // ELEMENT REFERENCES
    // =========================================================

    const singleModeBtn = document.getElementById("singleModeBtn");
    const batchModeBtn = document.getElementById("batchModeBtn");

    const singleEvaluationMode =
        document.getElementById("singleEvaluationMode");

    const batchEvaluationMode =
        document.getElementById("batchEvaluationMode");

    const csvFileInput =
        document.getElementById("csvFileInput");

    const csvUploadArea =
        document.getElementById("csvUploadArea");

    const selectedFileCard =
        document.getElementById("selectedFileCard");

    const selectedFileName =
        document.getElementById("selectedFileName");


    // =========================================================
    // MODE SWITCHING
    // =========================================================

    function activateSingleMode() {

        if (!singleModeBtn || !batchModeBtn) {
            return;
        }

        singleModeBtn.classList.add("active");
        batchModeBtn.classList.remove("active");

        if (singleEvaluationMode) {
            singleEvaluationMode.classList.remove("mode-hidden");
        }

        if (batchEvaluationMode) {
            batchEvaluationMode.classList.add("mode-hidden");
        }
    }


    function activateBatchMode() {

        if (!singleModeBtn || !batchModeBtn) {
            return;
        }

        batchModeBtn.classList.add("active");
        singleModeBtn.classList.remove("active");

        if (batchEvaluationMode) {
            batchEvaluationMode.classList.remove("mode-hidden");
        }

        if (singleEvaluationMode) {
            singleEvaluationMode.classList.add("mode-hidden");
        }
    }


    if (singleModeBtn) {

        singleModeBtn.addEventListener(
            "click",
            activateSingleMode
        );
    }


    if (batchModeBtn) {

        batchModeBtn.addEventListener(
            "click",
            activateBatchMode
        );
    }


    // =========================================================
    // PRESERVE MODE AFTER FLASK FORM SUBMISSION
    // =========================================================

    /*
        If Flask renders batch results, the HTML should contain:

        <body data-active-mode="batch">

        Otherwise:

        <body data-active-mode="single">

        We read that value here.
    */

    const activeMode =
        document.body.dataset.activeMode;


    if (activeMode === "batch") {

        activateBatchMode();

    } else {

        activateSingleMode();
    }


    // =========================================================
    // FILE DISPLAY
    // =========================================================

    function displaySelectedFile(file) {

        if (!file) {
            return;
        }


        // Only allow CSV files

        if (!file.name.toLowerCase().endsWith(".csv")) {

            alert("Please select a CSV file.");

            if (csvFileInput) {
                csvFileInput.value = "";
            }

            return;
        }


        if (selectedFileName) {
            selectedFileName.textContent = file.name;
        }


        if (selectedFileCard) {
            selectedFileCard.classList.remove("file-hidden");
        }
    }


    // =========================================================
    // STANDARD FILE SELECTION
    // =========================================================

    if (csvFileInput) {

        csvFileInput.addEventListener(
            "change",
            function () {

                const file =
                    csvFileInput.files[0];

                displaySelectedFile(file);
            }
        );
    }


    // =========================================================
    // DRAG AND DROP
    // =========================================================

    if (csvUploadArea && csvFileInput) {

        // Prevent browser from opening dropped files

        ["dragenter", "dragover"].forEach(
            function (eventName) {

                csvUploadArea.addEventListener(
                    eventName,
                    function (event) {

                        event.preventDefault();
                        event.stopPropagation();

                        csvUploadArea.classList.add(
                            "drag-active"
                        );
                    }
                );
            }
        );


        ["dragleave", "drop"].forEach(
            function (eventName) {

                csvUploadArea.addEventListener(
                    eventName,
                    function (event) {

                        event.preventDefault();
                        event.stopPropagation();

                        csvUploadArea.classList.remove(
                            "drag-active"
                        );
                    }
                );
            }
        );


        // Handle dropped file

        csvUploadArea.addEventListener(
            "drop",
            function (event) {

                const files =
                    event.dataTransfer.files;


                if (!files || files.length === 0) {
                    return;
                }


                const file = files[0];


                if (!file.name.toLowerCase().endsWith(".csv")) {

                    alert(
                        "Only CSV files are supported."
                    );

                    return;
                }


                /*
                    File input files cannot be assigned
                    directly in every browser.

                    DataTransfer provides a safe way
                    to populate the input.
                */

                const dataTransfer =
                    new DataTransfer();

                dataTransfer.items.add(file);

                csvFileInput.files =
                    dataTransfer.files;


                displaySelectedFile(file);
            }
        );
    }


    // =========================================================
    // EXPAND / COLLAPSE BATCH RESULT DETAILS
    // =========================================================

    const detailButtons =
        document.querySelectorAll(
            ".details-toggle"
        );


    detailButtons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    const targetId =
                        button.dataset.target;


                    if (!targetId) {
                        return;
                    }


                    const detailRow =
                        document.getElementById(
                            targetId
                        );


                    if (!detailRow) {
                        return;
                    }


                    const isOpen =
                        detailRow.classList.contains(
                            "detail-open"
                        );


                    if (isOpen) {

                        detailRow.classList.remove(
                            "detail-open"
                        );

                        button.textContent =
                            "View Details";

                    } else {

                        detailRow.classList.add(
                            "detail-open"
                        );

                        button.textContent =
                            "Hide Details";
                    }
                }
            );
        }
    );


    // =========================================================
    // CLOSE DETAILS BUTTON
    // =========================================================

    const closeButtons =
        document.querySelectorAll(
            ".close-details-btn"
        );


    closeButtons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    const targetId =
                        button.dataset.target;


                    if (!targetId) {
                        return;
                    }


                    const detailRow =
                        document.getElementById(
                            targetId
                        );


                    if (!detailRow) {
                        return;
                    }


                    detailRow.classList.remove(
                        "detail-open"
                    );


                    // Restore corresponding button text

                    const toggleButton =
                        document.querySelector(
                            `.details-toggle[data-target="${targetId}"]`
                        );


                    if (toggleButton) {

                        toggleButton.textContent =
                            "View Details";
                    }


                    // Scroll back to result row

                    const resultRow =
                        detailRow.previousElementSibling;


                    if (resultRow) {

                        resultRow.scrollIntoView({
                            behavior: "smooth",
                            block: "center"
                        });
                    }
                }
            );
        }
    );


    // =========================================================
    // SCROLL TO RESULTS AFTER EVALUATION
    // =========================================================

    /*
        After Flask renders results, automatically move
        the user to the relevant results section.
    */

    const batchResultsSection =
        document.querySelector(
            ".batch-results-section"
        );


    const singleDashboard =
        document.querySelector(
            ".dashboard"
        );


    if (
        activeMode === "batch" &&
        batchResultsSection
    ) {

        setTimeout(
            function () {

                batchResultsSection.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            },
            200
        );

    } else if (
        activeMode === "single" &&
        document.body.dataset.hasResults === "true" &&
        singleDashboard
    ) {

        setTimeout(
            function () {

                singleDashboard.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            },
            200
        );
    }

});
/* ==========================================
   BATCH CHARTS
========================================== */

document.addEventListener("DOMContentLoaded", () => {

    if (!window.batchAnalytics) return;

    const analytics = window.batchAnalytics;
    const verdicts = window.batchVerdicts;
    // -----------------------------
    // Dimension Bar Chart
    // -----------------------------

    const dimensionCanvas =
        document.getElementById("dimensionChart");

    if (dimensionCanvas) {

        new Chart(dimensionCanvas, {

            type: "bar",

            data: {

                labels: [
                    "Relevance",
                    "Accuracy",
                    "Hallucination",
                    "Completeness"
                ],

                datasets: [{

                    label: "Average Score",

                    data: [

                        analytics.average_relevance,
                        analytics.average_accuracy,
                        analytics.average_hallucination,
                        analytics.average_completeness

                    ],

                    backgroundColor: [

                        "#22c55e",   // Relevance

                        "#3b82f6",   // Accuracy

                        "#f97316",   // Hallucination

                        "#8b5cf6"    // Completeness

                    ],

                    borderColor: [
                        "#16a34a",
                        "#2563eb",
                        "#ea580c",
                        "#7c3aed"
                    ],

                    borderWidth: 2,

                    borderRadius: 8

                }]

            },

            options: {

                responsive: true,

                scales: {

                    y: {

                        beginAtZero: true,

                        max: 10

                    }

                }

            }

        });

    }

    // -----------------------------
    // Verdict Pie
    // -----------------------------

    const verdictCanvas =
        document.getElementById("verdictChart");

    if (verdictCanvas) {

        new Chart(verdictCanvas, {

            type: "pie",

            data: {

                labels: [

                    "Pass",

                    "Needs Improvement",

                    "Fail"

                ],

                datasets: [{

                    data: [

                        verdicts.Pass || 0,
                        verdicts["Needs Improvement"] || 0,
                        verdicts.Fail || 0

                    ],

                    backgroundColor: [

                        "#22c55e",      

                        "#6366f1",      

                        "#ef4444"       

                    ],

                    borderColor: "#ffffff",

                    borderWidth: 3

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {

                        position: "bottom"
                    },

                    tooltip: {

                        enabled: true

                    }

                }

            }

        });

    }

    // -----------------------------
    // Quality Trend
    // -----------------------------

    const trendCanvas =
        document.getElementById("qualityTrendChart");

    if (trendCanvas) {

        new Chart(trendCanvas, {

            type: "line",

            data: {

                labels:

                    analytics.quality_trend.map(
                        (_, i) => "Row " + (i + 1)
                    ),

                datasets: [{

                    label: "Overall Score",

                    data:
                        analytics.quality_trend,

                    borderColor: "#4f46e5",

                    backgroundColor: "rgba(79,70,229,0.15)",

                    pointBackgroundColor: "#4f46e5",

                    pointBorderColor: "#ffffff",

                    pointRadius: 6,

                    pointHoverRadius: 8,

                    borderWidth: 4,

                    tension: 0,

                    fill: true

                }]

            },

            options: {

                responsive: true,

                interaction: {

                    mode: "nearest",

                    intersect: true

                },

                plugins: {

                    tooltip: {

                        mode: "nearest",

                        intersect: true

                    }

                },

                scales: {

                    y: {

                        beginAtZero: true,

                        max: 10

                    }

                }

            }
        });

    }

});