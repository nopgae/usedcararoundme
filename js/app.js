/**
 * usedcararoundme - Main Application
 * This file handles all the user interface logic and connects
 * the UI with the API services
 * 
 * Author: nopgae
 * GitHub: https://github.com/nopgae/usedcararoundme
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the API service
    const vehicleAPI = new VehicleAPI();
    
    // UI Elements
    const makeSelect = document.getElementById('makeSelect');
    const modelSelect = document.getElementById('modelSelect');
    const yearSelect = document.getElementById('yearSelect');
    const searchButton = document.getElementById('searchButton');
    const carSearchForm = document.getElementById('carSearchForm');
    const alertArea = document.getElementById('alertArea');
    const loadingResults = document.getElementById('loadingResults');
    const resultsContent = document.getElementById('resultsContent');
    const noResults = document.getElementById('noResults');
    const retryButton = document.getElementById('retryButton');
    
    // Spinners
    const makeSpinner = document.getElementById('makeSpinner');
    const modelSpinner = document.getElementById('modelSpinner');
    const yearSpinner = document.getElementById('yearSpinner');
    
    // Results Elements
    const vehicleTitle = document.getElementById('vehicleTitle');
    const vehicleMake = document.getElementById('vehicleMake');
    const vehicleModel = document.getElementById('vehicleModel');
    const vehicleYear = document.getElementById('vehicleYear');
    const vehicleType = document.getElementById('vehicleType');
    const vehiclePrice = document.getElementById('vehiclePrice');
    const vehicleSpecs = document.getElementById('vehicleSpecs');
    
    // Initialize the application
    init();
    
    /**
     * Initialize the application
     */
    async function init() {
        // Enable all select elements by default
        if (makeSelect) makeSelect.disabled = false;
        if (modelSelect) modelSelect.disabled = false;
        if (yearSelect) yearSelect.disabled = false;
        
        // Hide all models except those for the first make (Toyota)
        document.querySelectorAll('#modelSelect option:not(.make-1)').forEach(option => {
            if (!option.value) return; // Skip the default "Select Model" option
            option.style.display = 'none';
        });
        
        // Load makes if API is available
        try {
            await loadMakes();
        } catch (error) {
            console.error("Error loading makes:", error);
        }
        
        // Set up event listeners
        if (makeSelect) makeSelect.addEventListener('change', handleMakeChange);
        if (modelSelect) modelSelect.addEventListener('change', handleModelChange);
        if (carSearchForm) carSearchForm.addEventListener('submit', handleSearch);
        if (retryButton) retryButton.addEventListener('click', handleRetryConnection);
        
        // Show a sample result
        showSampleResult();
    }
    
    /**
     * Load vehicle makes into the dropdown
     */
    async function loadMakes() {
        if (makeSpinner) {
            showSpinner(makeSpinner);
        }
        
        try {
            const makes = await vehicleAPI.getMakes();
            
            // Sort makes alphabetically
            makes.sort((a, b) => a.MakeName ? a.MakeName.localeCompare(b.MakeName) : a.makeName.localeCompare(b.makeName));
            
            // Clear and populate the select
            if (makeSelect) {
                makeSelect.innerHTML = '<option value="">Select Make</option>';
                
                makes.forEach(make => {
                    const makeId = make.MakeId || make.makeId;
                    const makeName = make.MakeName || make.makeName;
                    
                    const option = document.createElement('option');
                    option.value = makeId;
                    option.textContent = makeName;
                    makeSelect.appendChild(option);
                });
                
                makeSelect.disabled = false;
            }
        } catch (error) {
            console.error('Error loading makes:', error);
            showAlert('Error loading vehicle makes. Please try again later.', 'danger');
        } finally {
            if (makeSpinner) {
                hideSpinner(makeSpinner);
            }
        }
    }
    
    /**
     * Handle make selection change
     */
    async function handleMakeChange() {
        if (!makeSelect) return;
        const selectedMakeId = makeSelect.value;
        
        // Reset and hide all model options
        document.querySelectorAll('#modelSelect option').forEach(option => {
            if (!option.value) return; // Skip the default "Select Model" option
            option.style.display = 'none';
        });
        
        // Show only models for the selected make
        document.querySelectorAll(`#modelSelect option.make-${selectedMakeId}`).forEach(option => {
            option.style.display = '';
        });
        
        // Reset the model select to the default option
        if (modelSelect) modelSelect.value = '';
        
        // Reset the year select to the default option
        if (yearSelect) yearSelect.value = '';
        
        // If no make is selected, stop here
        if (!selectedMakeId) {
            return;
        }
        
        // Try to load models from API (will use fallback if API fails)
        if (modelSpinner) {
            showSpinner(modelSpinner);
        }
        
        try {
            const models = await vehicleAPI.getModels(selectedMakeId);
            // We won't update the dropdown here since we're using pre-populated options for testing
        } catch (error) {
            console.error('Error loading models:', error);
        } finally {
            if (modelSpinner) {
                hideSpinner(modelSpinner);
            }
        }
    }
    
    /**
     * Handle model selection change
     */
    async function handleModelChange() {
        // If no model is selected, stop here
        if (!modelSelect || !modelSelect.value) {
            return;
        }
        
        // We already have years pre-populated in the HTML,
        // so we don't need to fetch them from the API for testing purposes
    }
    
    /**
     * Handle search form submission
     * @param {Event} event - The form submit event
     */
    async function handleSearch(event) {
        // Prevent form submission
        if (event) {
            event.preventDefault();
        }
        
        // Hide any previous results
        hideResults();
        clearAlerts();
        
        // Validate form
        if (!makeSelect || !modelSelect || !yearSelect || 
            !makeSelect.value || !modelSelect.value || !yearSelect.value) {
            showAlert('Please select a make, model, and year to search.', 'warning');
            return;
        }
        
        // Show loading state
        if (loadingResults) {
            loadingResults.classList.remove('d-none');
        }
        
        try {
            // Get vehicle details
            const vehicleDetails = await vehicleAPI.getVehicleDetails(
                makeSelect.value,
                modelSelect.value,
                yearSelect.value
            );
            
            // Display results
            displayVehicleDetails(vehicleDetails);
            
            // Show the results section
            if (resultsContent) {
                resultsContent.classList.remove('d-none');
            }
            
            // Scroll to results
            if (resultsContent) {
                resultsContent.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        } catch (error) {
            console.error('Error searching for vehicle:', error);
            showAlert('Error loading vehicle details. Please try again later.', 'danger');
            if (noResults) {
                noResults.classList.remove('d-none');
            }
        } finally {
            // Hide loading state
            if (loadingResults) {
                loadingResults.classList.add('d-none');
            }
        }
    }
    
    /**
     * Show a sample vehicle result for immediate testing
     */
    function showSampleResult() {
        // Display the results content section
        if (resultsContent) {
            resultsContent.classList.remove('d-none');
        }
        
        // Set sample data in the result fields
        if (vehicleTitle) vehicleTitle.textContent = '2022 Toyota Camry';
        if (vehicleMake) vehicleMake.textContent = 'Toyota';
        if (vehicleModel) vehicleModel.textContent = 'Camry';
        if (vehicleYear) vehicleYear.textContent = '2022';
        if (vehicleType) vehicleType.textContent = 'Sedan';
        if (vehiclePrice) vehiclePrice.textContent = '$25,500';
        
        // Clear and populate specifications
        if (vehicleSpecs) {
            vehicleSpecs.innerHTML = '';
            
            const specs = [
                { name: "Engine", value: "2.5L 4-Cylinder" },
                { name: "Transmission", value: "8-Speed Automatic" },
                { name: "Drivetrain", value: "Front-Wheel Drive" },
                { name: "Fuel Economy", value: "28 City / 39 Highway" },
                { name: "Horsepower", value: "203 hp" },
                { name: "Seating Capacity", value: "5" },
                { name: "Cargo Space", value: "15.1 cu ft" },
                { name: "NHTSA Safety Rating", value: "5 Stars" }
            ];
            
            specs.forEach(spec => {
                const row = document.createElement('tr');
                
                const nameCell = document.createElement('th');
                nameCell.scope = 'row';
                nameCell.textContent = spec.name;
                
                const valueCell = document.createElement('td');
                valueCell.textContent = spec.value;
                
                row.appendChild(nameCell);
                row.appendChild(valueCell);
                vehicleSpecs.appendChild(row);
            });
        }
    }
    
    /**
     * Display vehicle details in the UI
     * @param {Object} vehicle - The vehicle details
     */
    function displayVehicleDetails(vehicle) {
        // Display overview information
        if (vehicleTitle) vehicleTitle.textContent = `${vehicle.year} ${vehicle.make} ${vehicle.model}`;
        if (vehicleMake) vehicleMake.textContent = vehicle.make;
        if (vehicleModel) vehicleModel.textContent = vehicle.model;
        if (vehicleYear) vehicleYear.textContent = vehicle.year;
        if (vehicleType) vehicleType.textContent = vehicle.vehicleType || 'Not Available';
        if (vehiclePrice) vehiclePrice.textContent = vehicleAPI.formatPrice(vehicle.basePrice) || 'Not Available';
        
        // Clear and populate specifications
        if (vehicleSpecs) {
            vehicleSpecs.innerHTML = '';
            
            if (vehicle.specifications && vehicle.specifications.length > 0) {
                vehicle.specifications.forEach(spec => {
                    const row = document.createElement('tr');
                    
                    const nameCell = document.createElement('th');
                    nameCell.scope = 'row';
                    nameCell.textContent = spec.name;
                    
                    const valueCell = document.createElement('td');
                    valueCell.textContent = spec.value;
                    
                    row.appendChild(nameCell);
                    row.appendChild(valueCell);
                    vehicleSpecs.appendChild(row);
                });
            } else {
                const row = document.createElement('tr');
                const cell = document.createElement('td');
                cell.colSpan = 2;
                cell.textContent = 'No specifications available';
                cell.className = 'text-center';
                row.appendChild(cell);
                vehicleSpecs.appendChild(row);
            }
        }
        
        // Add a class to animate the appearance
        if (resultsContent) {
            resultsContent.classList.add('fade-in');
        }
    }
    
    /**
     * Handle retry connection button click
     */
    function handleRetryConnection() {
        // Reset the API fallback state
        vehicleAPI.setUsingFallback(false);
        
        // Reload makes to test connection
        loadMakes();
        
        // Hide the modal
        const apiErrorModal = document.getElementById('apiErrorModal');
        if (apiErrorModal) {
            const modal = bootstrap.Modal.getInstance(apiErrorModal);
            if (modal) {
                modal.hide();
            }
        }
        
        // Show a message
        showAlert('Attempting to reconnect to the NHTSA API...', 'info');
    }
    
    /**
     * Populate models dropdown with fallback data
     * @param {string} makeId - The ID of the selected make
     */
    function populateFallbackModels(makeId) {
        if (!modelSelect) return;
        
        // Clear and reset the models dropdown
        modelSelect.innerHTML = '<option value="">Select Model</option>';
        
        // Get the models for the selected make from fallback data
        const models = fallbackData.models[makeId] || [];
        
        // Populate the models dropdown
        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model.modelId;
            option.textContent = model.modelName;
            modelSelect.appendChild(option);
        });
        
        modelSelect.disabled = false;
    }
    
    /**
     * Populate years dropdown with fallback data
     */
    function populateFallbackYears() {
        if (!yearSelect) return;
        
        // Clear and reset the years dropdown
        yearSelect.innerHTML = '<option value="">Select Year</option>';
        
        // Get years from fallback data
        const years = fallbackData.years.default || [];
        
        // Populate the years dropdown
        years.forEach(yearObj => {
            const year = yearObj.year;
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            yearSelect.appendChild(option);
        });
        
        yearSelect.disabled = false;
    }
    
    /**
     * Show a spinner
     * @param {HTMLElement} spinner - The spinner element
     */
    function showSpinner(spinner) {
        if (spinner) {
            spinner.classList.remove('d-none');
        }
    }
    
    /**
     * Hide a spinner
     * @param {HTMLElement} spinner - The spinner element
     */
    function hideSpinner(spinner) {
        if (spinner) {
            spinner.classList.add('d-none');
        }
    }
    
    /**
     * Hide all results sections
     */
    function hideResults() {
        if (resultsContent) {
            resultsContent.classList.add('d-none');
        }
        
        if (noResults) {
            noResults.classList.add('d-none');
        }
    }
    
    /**
     * Show an alert message
     * @param {string} message - The message to display
     * @param {string} type - The alert type (success, info, warning, danger)
     */
    function showAlert(message, type = 'info') {
        clearAlerts();
        
        if (!alertArea) return;
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.role = 'alert';
        
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        alertArea.appendChild(alert);
    }
    
    /**
     * Clear all alerts
     */
    function clearAlerts() {
        if (alertArea) {
            alertArea.innerHTML = '';
        }
    }
});