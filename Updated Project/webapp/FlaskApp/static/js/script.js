// Enhanced JavaScript for the Breast Cancer Classification App

document.addEventListener('DOMContentLoaded', function () {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Form validation enhancement
    const predictionForm = document.getElementById('predictionForm');
    if (predictionForm) {
        predictionForm.addEventListener('submit', function (e) {
            const inputs = this.querySelectorAll('input[type="number"]');
            let isValid = true;

            inputs.forEach(input => {
                if (!input.value || isNaN(input.value)) {
                    isValid = false;
                    input.classList.add('is-invalid');
                } else {
                    input.classList.remove('is-invalid');
                }
            });

            if (!isValid) {
                e.preventDefault();
                showAlert('Please fill all fields with valid numerical values.', 'danger');
            }
        });
    }

    // ===== SAMPLE LOADER FOR PREDICTION PAGE =====
    function loadBenignSample() {
        const benign = {
            radius_mean: 12,
            texture_mean: 18,
            perimeter_mean: 80,
            area_mean: 500,
            radius_worst: 15,
            perimeter_worst: 95,
            area_worst: 600,
            concave_points_mean: 0.04,
            concave_points_worst: 0.05,
            area_se: 30
        };

        Object.keys(benign).forEach(key => {
            const el = document.getElementById(key);
            if (el) el.value = benign[key];
        });
    }

    function loadMalignantSample() {
        const malignant = {
            radius_mean: 17,
            texture_mean: 20,
            perimeter_mean: 110,
            area_mean: 1000,
            radius_worst: 22,
            perimeter_worst: 150,
            area_worst: 1200,
            concave_points_mean: 0.18,
            concave_points_worst: 0.25,
            area_se: 80
        };

        Object.keys(malignant).forEach(key => {
            const el = document.getElementById(key);
            if (el) el.value = malignant[key];
        });
    }


    // Auto-format feature inputs
    const featureInputs = document.querySelectorAll('.feature-input');
    featureInputs.forEach(input => {
        input.addEventListener('blur', function () {
            if (this.value) {
                this.value = parseFloat(this.value).toFixed(4);
            }
        });
    });

    // Add sample value buttons for testing
    addSampleValueButtons();

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);

    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function addSampleValueButtons() {
    const sampleValues = {
        'benign': {
            'radius_mean': '12.0',
            'texture_mean': '18.0',
            'perimeter_mean': '80.0',
            'area_mean': '500.0',
            'smoothness_mean': '0.08',
            'compactness_mean': '0.08',
            'concavity_mean': '0.05',
            'concave points_mean': '0.03'
        },
        'malignant': {
            'radius_mean': '17.0',
            'texture_mean': '20.0',
            'perimeter_mean': '110.0',
            'area_mean': '1000.0',
            'smoothness_mean': '0.10',
            'compactness_mean': '0.15',
            'concavity_mean': '0.15',
            'concave points_mean': '0.08'
        }
    };

    const form = document.getElementById('predictionForm');
    if (form) {
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'mb-3 text-center';
        buttonContainer.innerHTML = `
            <button type="button" class="btn btn-outline-success btn-sm me-2" onclick="fillSampleValues('benign')">
                <i class="fas fa-leaf me-1"></i>Load Benign Sample
            </button>
            <button type="button" class="btn btn-outline-danger btn-sm" onclick="fillSampleValues('malignant')">
                <i class="fas fa-exclamation-triangle me-1"></i>Load Malignant Sample
            </button>
        `;
        form.insertBefore(buttonContainer, form.querySelector('.mt-4'));
    }
}

function fillSampleValues(type) {
    const samples = {
        'benign': {
            'radius_mean': '12.0',
            'texture_mean': '18.0',
            'perimeter_mean': '80.0',
            'area_mean': '500.0',
            'smoothness_mean': '0.08',
            'compactness_mean': '0.08',
            'concavity_mean': '0.05',
            'concave points_mean': '0.03'
        },
        'malignant': {
            'radius_mean': '17.0',
            'texture_mean': '20.0',
            'perimeter_mean': '110.0',
            'area_mean': '1000.0',
            'smoothness_mean': '0.10',
            'compactness_mean': '0.15',
            'concavity_mean': '0.15',
            'concave points_mean': '0.08'
        }
    };

    const values = samples[type];
    for (const [feature, value] of Object.entries(values)) {
        const input = document.getElementById(feature);
        if (input) {
            input.value = value;
        }
    }

    showAlert(`${type.charAt(0).toUpperCase() + type.slice(1)} sample values loaded.`, 'info');
}

// API integration for real-time predictions
async function makePredictionAPI(featureData) {
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(featureData)
        });

        if (!response.ok) {
            throw new Error('Prediction failed');
        }

        return await response.json();
    } catch (error) {
        console.error('API Prediction Error:', error);
        throw error;
    }
}