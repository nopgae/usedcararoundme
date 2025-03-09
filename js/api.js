/**
 * UsedCarAroundMe - API Handler
 * This file handles all interactions with the NHTSA API
 * and provides fallback mechanisms when the API is unavailable
 */

class VehicleAPI {
    constructor() {
        this.baseUrl = 'https://vpic.nhtsa.dot.gov/api/vehicles';
        this.format = 'json';
        this.usingFallback = true; // Start with fallback mode enabled for immediate testing
        // We'll initialize the modal only after the DOM is fully loaded
        this.apiErrorModal = null;
        
        // Initialize modal after DOM is loaded
        document.addEventListener('DOMContentLoaded', () => {
            const modalElement = document.getElementById('apiErrorModal');
            if (modalElement) {
                this.apiErrorModal = new bootstrap.Modal(modalElement);
            }
        });
    }

    /**
     * Get all vehicle makes
     * @returns {Promise} Promise object with vehicle makes
     */
    async getMakes() {
        try {
            const response = await fetch(`${this.baseUrl}/GetAllMakes?format=${this.format}`);
            if (!response.ok) throw new Error('API request failed');
            
            const data = await response.json();
            this.usingFallback = false;
            return data.Results;
        } catch (error) {
            console.error('Error fetching makes:', error);
            this.setUsingFallback(true);
            return fallbackData.makes;
        }
    }

    /**
     * Get all models for a specific make
     * @param {number} makeId - The ID of the make
     * @returns {Promise} Promise object with models for the make
     */
    async getModels(makeId) {
        if (this.usingFallback) {
            return fallbackData.models[makeId] || [];
        }

        try {
            const response = await fetch(`${this.baseUrl}/GetModelsForMakeId/${makeId}?format=${this.format}`);
            if (!response.ok) throw new Error('API request failed');
            
            const data = await response.json();
            return data.Results;
        } catch (error) {
            console.error('Error fetching models:', error);
            this.setUsingFallback(true);
            return fallbackData.models[makeId] || [];
        }
    }

    /**
     * Get years for a specific make/model
     * In the NHTSA API, we would use GetModelYears but for simplicity,
     * we'll use a fixed range of years for all models
     * @param {number} makeId - The ID of the make
     * @param {number} modelId - The ID of the model
     * @returns {Promise} Promise object with years
     */
    async getYears(makeId, modelId) {
        if (this.usingFallback) {
            return fallbackData.years.default;
        }

        try {
            // Ideally, we would call a specific API endpoint for model years
            // But the NHTSA API doesn't have a direct endpoint for this
            // For a real application, we might use a different API or database
            // For this demo, we'll use the fixed range of years
            
            // Simulate an API call by adding a slight delay
            await new Promise(resolve => setTimeout(resolve, 300));
            
            // Let's assume we're successful in getting years
            return fallbackData.years.default;
        } catch (error) {
            console.error('Error fetching years:', error);
            this.setUsingFallback(true);
            return fallbackData.years.default;
        }
    }

    /**
     * Get vehicle details for a specific make/model/year
     * @param {string} make - The make name
     * @param {string} model - The model name
     * @param {number} year - The year
     * @returns {Promise} Promise object with vehicle details
     */
    async getVehicleDetails(makeId, modelId, year) {
        const detailKey = `${makeId}_${modelId}_${year}`;
        
        if (this.usingFallback) {
            return fallbackData.vehicleDetails[detailKey] || this.generateGenericDetails(makeId, modelId, year);
        }

        try {
            // The NHTSA API doesn't provide comprehensive vehicle details in one call
            // We need to make multiple calls to get different pieces of information
            
            // First, let's get the base vehicle info
            const response = await fetch(`${this.baseUrl}/DecodeVINValuesBatch/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                // This is a workaround - typically we'd need a VIN
                // We're providing a partial request just to get some data
                body: JSON.stringify({
                    format: 'json',
                    data: [
                        `${year}${make}${model}`
                    ]
                })
            });

            if (!response.ok) throw new Error('API request failed');
            
            // This likely won't return complete data without a real VIN
            // So we'll combine with fallback data
            let vehicleData = this.generateGenericDetails(makeId, modelId, year);
            
            try {
                const data = await response.json();
                if (data.Results && data.Results.length > 0) {
                    // Enhance our generic data with any values we get from the API
                    const apiData = data.Results[0];
                    
                    // Update specs if we get them from the API
                    if (apiData.EngineConfiguration) {
                        vehicleData.specifications.push({ 
                            name: "Engine Configuration", 
                            value: apiData.EngineConfiguration 
                        });
                    }
                    
                    if (apiData.FuelTypePrimary) {
                        vehicleData.specifications.push({ 
                            name: "Fuel Type", 
                            value: apiData.FuelTypePrimary 
                        });
                    }
                    
                    if (apiData.VehicleType) {
                        vehicleData.vehicleType = apiData.VehicleType;
                    }
                }
            } catch (e) {
                console.error('Error parsing API response:', e);
                // Continue with our fallback data
            }
            
            return vehicleData;
        } catch (error) {
            console.error('Error fetching vehicle details:', error);
            this.setUsingFallback(true);
            return fallbackData.vehicleDetails[detailKey] || this.generateGenericDetails(makeId, modelId, year);
        }
    }

    /**
     * Generate generic vehicle details when specific data is not available
     * @param {number} makeId - The ID of the make
     * @param {number} modelId - The ID of the model
     * @param {number} year - The year
     * @returns {Object} Generic vehicle details
     */
    generateGenericDetails(makeId, modelId, year) {
        // Find make and model names from our fallback data
        const make = this.findMakeName(makeId);
        const model = this.findModelName(makeId, modelId);
        
        // Calculate a simulated price based on the year
        const basePrice = this.calculateBasePrice(make, model, year);
        
        return {
            make: make,
            model: model,
            year: parseInt(year),
            vehicleType: this.determineVehicleType(model),
            basePrice: basePrice,
            specifications: [...fallbackData.defaultVehicleDetails.specifications]
        };
    }

    /**
     * Find make name from make ID
     * @param {number} makeId - The ID of the make
     * @returns {string} Make name
     */
    findMakeName(makeId) {
        const make = fallbackData.makes.find(make => make.makeId == makeId);
        return make ? make.makeName : "Unknown Make";
    }

    /**
     * Find model name from model ID
     * @param {number} makeId - The ID of the make
     * @param {number} modelId - The ID of the model
     * @returns {string} Model name
     */
    findModelName(makeId, modelId) {
        if (!fallbackData.models[makeId]) return "Unknown Model";
        
        const model = fallbackData.models[makeId].find(model => model.modelId == modelId);
        return model ? model.modelName : "Unknown Model";
    }

    /**
     * Determine vehicle type based on model name
     * This is a very simple heuristic and would be replaced with actual data in a real app
     * @param {string} modelName - The model name
     * @returns {string} Vehicle type
     */
    determineVehicleType(modelName) {
        const modelNameLower = modelName.toLowerCase();
        
        if (modelNameLower.includes('f-') || 
            modelNameLower.includes('silverado') || 
            modelNameLower.includes('sierra') ||
            modelNameLower.includes('tacoma') ||
            modelNameLower.includes('tundra') ||
            modelNameLower.includes('frontier')) {
            return "Pickup Truck";
        }
        
        if (modelNameLower.includes('suv') || 
            modelNameLower.includes('explorer') || 
            modelNameLower.includes('expedition') ||
            modelNameLower.includes('tahoe') ||
            modelNameLower.includes('suburban') ||
            modelNameLower.includes('pilot') ||
            modelNameLower.includes('pathfinder') ||
            modelNameLower.includes('highlander')) {
            return "SUV";
        }
        
        if (modelNameLower.includes('van') || 
            modelNameLower.includes('odyssey') || 
            modelNameLower.includes('sienna')) {
            return "Minivan";
        }
        
        // Default to sedan if we can't determine
        return "Sedan";
    }

    /**
     * Calculate estimated base price for a vehicle
     * This is a simulated calculation for demonstration purposes
     * @param {string} make - The make name
     * @param {string} model - The model name
     * @param {number} year - The year
     * @returns {number} Estimated base price
     */
    calculateBasePrice(make, model, year) {
        // Start with a base price between $20,000 and $30,000
        let basePrice = Math.floor(Math.random() * 10000) + 20000;
        
        // Adjust for age: newer cars cost more
        const currentYear = new Date().getFullYear();
        const age = currentYear - year;
        
        // Depreciation rate: roughly 10-15% per year
        const depreciationRate = 0.12; // 12% per year on average
        basePrice = basePrice * Math.pow(1 - depreciationRate, age);
        
        // Premium brands have higher prices
        const premiumBrands = ["BMW", "Mercedes-Benz", "Audi", "Lexus", "Porsche", "Tesla"];
        if (premiumBrands.includes(make)) {
            basePrice *= 1.6; // 60% premium
        }
        
        // Economy brands have lower prices
        const economyBrands = ["Kia", "Hyundai", "Mitsubishi", "Suzuki"];
        if (economyBrands.includes(make)) {
            basePrice *= 0.8; // 20% discount
        }
        
        // Round to nearest hundred and ensure minimum price
        basePrice = Math.max(Math.round(basePrice / 100) * 100, 1500);
        
        return basePrice;
    }

    /**
     * Set the fallback status and show the error modal if needed
     * @param {boolean} status - Whether to use fallback data
     */
    setUsingFallback(status) {
        if (status && !this.usingFallback && this.apiErrorModal) {
            // Only show the modal when first switching to fallback
            // and only if the modal is initialized
            this.apiErrorModal.show();
        }
        this.usingFallback = status;
    }

    /**
     * Format price as currency
     * @param {number} price - The price to format
     * @returns {string} Formatted price
     */
    formatPrice(price) {
        return new Intl.NumberFormat('en-US', { 
            style: 'currency', 
            currency: 'USD',
            maximumFractionDigits: 0
        }).format(price);
    }
}