// Hauptskript für die RitterDigitalAuswertung-Anwendung

document.addEventListener('DOMContentLoaded', function() {
    // Initialisierungen nach dem Laden des DOMs
    initStandortDropdown();
    initDataTable();
    initExportButtons();
    initFilterFunctions();

    // Bei Seitenstart prüfen, ob bereits Charts gezeichnet werden können
    if (document.getElementById('bereich-chart') ||
        document.getElementById('rg-chart') ||
        document.getElementById('etage-chart')) {
        createCharts();
    }
});

// Initialisiert die Standort-Dropdown mit Event-Listener
function initStandortDropdown() {
    const standortSelect = document.getElementById('standort-select');
    if (!standortSelect) return;

    standortSelect.addEventListener('change', function() {
        const standortId = this.value;
        if (standortId) {
            document.getElementById('standort-form').submit();
        }
    });
}

// Initialisiert DataTable für bessere Tabellenfunktionalität (wenn vorhanden)
function initDataTable() {
    const dataTable = document.getElementById('raumbuch-table');
    if (!dataTable) return;

    // Falls jQuery und DataTables vorhanden sind, initialisiere DataTable
    if (typeof $ !== 'undefined' && $.fn.DataTable) {
        // Prüfen, ob die Tabelle bereits als DataTable initialisiert wurde
        if ($.fn.DataTable.isDataTable('#raumbuch-table')) {
            // Tabelle bereits initialisiert, nichts tun
            console.log('DataTable bereits initialisiert');
            return;
        }

        // Tabelle initialisieren
        $('#raumbuch-table').DataTable({
            responsive: true,
            lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "Alle"]],
            language: {
                url: '//cdn.datatables.net/plug-ins/1.10.25/i18n/German.json'
            },
            initComplete: function() {
                // Nach der Initialisierung kann man weitere Anpassungen vornehmen
                $('#raumbuch-table_wrapper').addClass('table-responsive');
            }
        });
    } else {
        // Fallback-Funktionalität, wenn DataTables nicht verfügbar ist
        // Einfache Suchfunktion
        const searchInput = document.getElementById('table-search');
        if (searchInput) {
            searchInput.addEventListener('keyup', function() {
                filterTable(this.value.toLowerCase());
            });
        }
    }
}

// Einfache Tabellenfilterung für Nicht-DataTables-Ansicht
function filterTable(query) {
    const table = document.getElementById('raumbuch-table');
    if (!table) return;

    const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

    for (let i = 0; i < rows.length; i++) {
        const rowText = rows[i].textContent.toLowerCase();
        rows[i].style.display = rowText.includes(query) ? '' : 'none';
    }
}

// Initialisiert Export-Buttons
function initExportButtons() {
    const exportExcelBtn = document.getElementById('export-excel');
    const exportPdfBtn = document.getElementById('export-pdf');

    if (exportExcelBtn) {
        exportExcelBtn.addEventListener('click', function() {
            const standortId = document.getElementById('standort-id')?.value ||
                               document.getElementById('standort-select')?.value;
            if (standortId) {
                window.location.href = `/export/excel/${standortId}`;
            } else {
                alert('Bitte wählen Sie zuerst einen Standort aus.');
            }
        });
    }

    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', function() {
            const standortId = document.getElementById('standort-id')?.value ||
                               document.getElementById('standort-select')?.value;
            if (standortId) {
                window.location.href = `/export/pdf/${standortId}`;
            } else {
                alert('Bitte wählen Sie zuerst einen Standort aus.');
            }
        });
    }
}

// Initialisiert Filter-Funktionen
function initFilterFunctions() {
    const filterForm = document.getElementById('filter-form');
    if (!filterForm) return;

    // Zurücksetzen-Button
    const resetFilterBtn = document.getElementById('reset-filter');
    if (resetFilterBtn) {
        resetFilterBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const formElements = filterForm.elements;
            for (let i = 0; i < formElements.length; i++) {
                if (formElements[i].type !== 'submit' && formElements[i].type !== 'button') {
                    formElements[i].value = '';
                }
            }
            filterForm.submit();
        });
    }

    // Automatisches Absenden nach Änderung eines Filters
    const filterInputs = filterForm.querySelectorAll('select, input:not([type="submit"]):not([type="button"])');
    filterInputs.forEach(input => {
        input.addEventListener('change', function() {
            filterForm.submit();
        });
    });
}

// Chart-Erstellung mit Chart.js (wenn verfügbar)
function createCharts() {
    if (typeof Chart === 'undefined') return;

    // Bereich-Chart (Tortendiagramm)
    createBereichChart();

    // Reinigungsgruppen-Chart (Balkendiagramm)
    createRgChart();

    // Etagen-Chart (Balkendiagramm)
    createEtageChart();
}

// Erstellt ein Tortendiagramm für die Verteilung nach Bereichen
function createBereichChart() {
    const bereichChartElement = document.getElementById('bereich-chart');
    if (!bereichChartElement) return;

    // Daten aus data-Attribut extrahieren
    const chartData = JSON.parse(bereichChartElement.dataset.chartData || '{}');
    if (!Object.keys(chartData).length) return;

    const labels = Object.keys(chartData);
    const values = Object.values(chartData);

    // Zufällige Farben für die Chart-Segmente generieren
    const backgroundColors = labels.map(() => getRandomColor());

    // Chart erstellen
    new Chart(bereichChartElement, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: backgroundColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            title: {
                display: true,
                text: 'Verteilung nach Bereichen (qm)'
            },
            tooltips: {
                callbacks: {
                    label: function(tooltipItem, data) {
                        const value = data.datasets[0].data[tooltipItem.index];
                        const label = data.labels[tooltipItem.index];
                        return `${label}: ${value.toFixed(2)} qm`;
                    }
                }
            }
        }
    });
}

// Erstellt ein Balkendiagramm für die Reinigungsgruppen
function createRgChart() {
    const rgChartElement = document.getElementById('rg-chart');
    if (!rgChartElement) return;

    // Daten aus data-Attribut extrahieren
    const chartData = JSON.parse(rgChartElement.dataset.chartData || '{}');
    if (!Object.keys(chartData).length) return;

    const labels = Object.keys(chartData);
    const values = Object.values(chartData);

    // Chart erstellen
    new Chart(rgChartElement, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Wert pro Monat (€)',
                data: values,
                backgroundColor: '#f08c00',
                borderColor: '#d97e00',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            title: {
                display: true,
                text: 'Wert pro Monat nach Reinigungsgruppe'
            },
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        callback: function(value) {
                            return value.toFixed(2) + ' €';
                        }
                    }
                }]
            },
            tooltips: {
                callbacks: {
                    label: function(tooltipItem) {
                        return tooltipItem.yLabel.toFixed(2) + ' €';
                    }
                }
            }
        }
    });
}

// Erstellt ein Balkendiagramm für die Etagen
function createEtageChart() {
    const etageChartElement = document.getElementById('etage-chart');
    if (!etageChartElement) return;

    // Daten aus data-Attribut extrahieren
    const chartData = JSON.parse(etageChartElement.dataset.chartData || '{}');
    if (!Object.keys(chartData).length) return;

    const labels = Object.keys(chartData);
    const values = Object.values(chartData);

    // Chart erstellen
    new Chart(etageChartElement, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Stunden pro Monat',
                data: values,
                backgroundColor: '#003366',
                borderColor: '#002244',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            title: {
                display: true,
                text: 'Stunden pro Monat nach Etage'
            },
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        callback: function(value) {
                            return value.toFixed(2) + ' h';
                        }
                    }
                }]
            },
            tooltips: {
                callbacks: {
                    label: function(tooltipItem) {
                        return tooltipItem.yLabel.toFixed(2) + ' h';
                    }
                }
            }
        }
    });
}

// Hilfsfunktionen
function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

// Dynamisches Nachladen der Standortdaten
function loadStandorte() {
    const standortSelect = document.getElementById('standort-select');
    if (!standortSelect) return;

    // Nur nachladen, wenn keine Optionen vorhanden sind (außer der Placeholder)
    if (standortSelect.options.length <= 1) {
        fetch('/api/standorte')
            .then(response => response.json())
            .then(data => {
                // Optionen hinzufügen
                data.forEach(standort => {
                    const option = document.createElement('option');
                    option.value = standort.ID;
                    option.textContent = standort.Bezeichnung;
                    standortSelect.appendChild(option);
                });
            })
            .catch(error => console.error('Fehler beim Laden der Standorte:', error));
    }
}

// CSV-Export-Funktion
function exportTableToCSV(filename) {
    const table = document.getElementById('raumbuch-table');
    if (!table) return;

    const rows = table.querySelectorAll('tr');
    const csv = [];

    for (let i = 0; i < rows.length; i++) {
        const row = [], cols = rows[i].querySelectorAll('td, th');

        for (let j = 0; j < cols.length; j++) {
            // CSV-Zellenwert escapen
            let data = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, '').replace(/(\s\s)/gm, ' ');
            data = data.replace(/"/g, '""');
            row.push('"' + data + '"');
        }

        csv.push(row.join(','));
    }

    // CSV-Datei herunterladen
    downloadCSV(csv.join('\n'), filename);
}

function downloadCSV(csv, filename) {
    const csvFile = new Blob([csv], {type: "text/csv"});
    const downloadLink = document.createElement("a");

    // Dateinamen setzen
    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = "none";

    // Link zum DOM hinzufügen und klicken
    document.body.appendChild(downloadLink);
    downloadLink.click();

    // Link entfernen
    document.body.removeChild(downloadLink);
}