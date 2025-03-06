# Car Price Prediction API

This repository contains a machine learning API that predicts car prices based on various specifications, powered by data from Geely Auto.

## Features

- **Price Prediction**: Get estimated prices for cars based on specifications
- **Feature Importance**: Understand which factors most influence car prices
- **REST API**: Easy integration with any frontend application
- **Docker Support**: Simple deployment with containerization
- **CI/CD**: Automated testing and deployment pipeline with GitHub Actions

## Getting Started

### Prerequisites

- Python 3.9+
- Git
- Docker (optional, for containerized deployment)
- Kaggle API credentials (to download the dataset)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/car-price-prediction.git
   cd car-price-prediction
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Download the dataset:
   ```bash
   # Option 1: Using Kaggle API (requires Kaggle credentials)
   mkdir -p data
   kaggle datasets download -d zabihullah18/car-price-prediction -p data
   unzip -o data/car-price-prediction.zip -d data
   
   # Option 2: Manual download
   # Download from https://www.kaggle.com/datasets/zabihullah18/car-price-prediction
   # and place CarPrice_Assignment.csv in the data/ directory
   ```

4. Train the model:
   ```bash
   python scripts/train_model.py
   ```

5. Run the API:
   ```bash
   uvicorn api.main:app --reload
   ```

### Running with Docker

1. Build the Docker image:
   ```bash
   docker build -t car-price-api .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 car-price-api
   ```

## API Documentation

Once the API is running, visit `http://localhost:8000/docs` for the OpenAPI documentation.

### Endpoints

- `GET /`: Welcome message
- `POST /predict/`: Get a price prediction for a car
- `GET /models/info`: Get information about the ML model being used

### Example Request

```bash
curl -X POST "http://localhost:8000/predict/" \
  -H "Content-Type: application/json" \
  -d '{
    "fueltype": "gas",
    "aspiration": "std",
    "doornumber": "four",
    "carbody": "sedan",
    "drivewheel": "fwd",
    "enginelocation": "front",
    "wheelbase": 98.8,
    "carlength": 174.2,
    "carwidth": 66.9,
    "carheight": 54.3,
    "curbweight": 2337,
    "enginetype": "ohc",
    "cylindernumber": "four",
    "enginesize": 109,
    "fuelsystem": "mpfi",
    "boreratio": 3.19,
    "stroke": 3.40,
    "compressionratio": 9.0,
    "horsepower": 85,
    "peakrpm": 5800,
    "citympg": 27,
    "highwaympg": 32
  }'
```

## Frontend Integration

This API is designed to be easily integrated with any frontend application. Here's a simple example using JavaScript:

```javascript
async function predictCarPrice(carSpecs) {
  const response = await fetch('http://your-api-url/predict/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(carSpecs),
  });
  
  return await response.json();
}

// Example usage
const carSpecs = {
  fueltype: "gas",
  aspiration: "std",
  // ... other specifications
};

predictCarPrice(carSpecs)
  .then(result => {
    console.log(`Predicted Price: $${result.predicted_price.toFixed(2)}`);
    console.log('Important Features:', result.important_features);
  })
  .catch(error => console.error('Error:', error));
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Dataset from [Kaggle](https://www.kaggle.com/datasets/zabihullah18/car-price-prediction)
- Analysis by [zabihullah18](https://www.kaggle.com/zabihullah18)