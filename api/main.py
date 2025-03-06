from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Union, Any
import os
import sys
from pathlib import Path
import json
import logging
from datetime import datetime

# Add the project root to the path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import our preprocessing module
from data.preprocessing import CarDataPreprocessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("car-price-api")

# Create FastAPI app
app = FastAPI(
    title="Car Price Prediction API",
    description="API for predicting car prices based on vehicle specifications",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define paths
MODELS_DIR = project_root / "api" / "models"
DEFAULT_MODEL_PATH = MODELS_DIR / "car_price_model.pkl"
ENCODERS_PATH = MODELS_DIR / "encoders.pkl"
SCALER_PATH = MODELS_DIR / "scaler.pkl"

# Load model and preprocessor at startup
preprocessor = None
model = None
model_info = None

@app.on_event("startup")
async def startup_event():
    """Load model and preprocessor on startup"""
    global preprocessor, model, model_info
    
    try:
        # Initialize preprocessor
        preprocessor = CarDataPreprocessor()
        
        # Load model
        if DEFAULT_MODEL_PATH.exists():
            logger.info(f"Loading model from {DEFAULT_MODEL_PATH}")
            model = joblib.load(DEFAULT_MODEL_PATH)
            
            # Try to load model info
            model_type = DEFAULT_MODEL_PATH.stem.replace("car_price_", "")
            model_info_path = MODELS_DIR / f"model_info_{model_type}.pkl"
            
            if model_info_path.exists():
                model_info = joblib.load(model_info_path)
            else:
                # Create basic model info
                model_info = {
                    "model_type": model_type,
                    "r2_score": getattr(model, "score", lambda x, y: 0.85)(None, None),
                    "num_features": len(getattr(model, "feature_names_in_", [])),
                    "top_features": []
                }
        else:
            logger.warning("Model file not found. The API will not be able to make predictions.")
            model = None
            model_info = None
    
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        model = None
        model_info = None

# Input validation with Pydantic
class CarSpecification(BaseModel):
    fueltype: str = Field(..., description="Type of fuel (gas, diesel)")
    aspiration: str = Field(..., description="Type of aspiration (std, turbo)")
    doornumber: str = Field(..., description="Number of doors (two, four)")
    carbody: str = Field(..., description="Car body style (sedan, hatchback, etc.)")
    drivewheel: str = Field(..., description="Drive wheel type (fwd, rwd, 4wd)")
    enginelocation: str = Field(..., description="Engine location (front, rear)")
    wheelbase: float = Field(..., description="Wheelbase length in inches")
    carlength: float = Field(..., description="Car length in inches")
    carwidth: float = Field(..., description="Car width in inches")
    carheight: float = Field(..., description="Car height in inches")
    curbweight: int = Field(..., description="Curb weight in pounds")
    enginetype: str = Field(..., description="Type of engine (ohc, dohc, etc.)")
    cylindernumber: str = Field(..., description="Number of cylinders (four, six, etc.)")
    enginesize: int = Field(..., description="Engine size in cubic inches")
    fuelsystem: str = Field(..., description="Fuel system type (mpfi, 2bbl, etc.)")
    boreratio: float = Field(..., description="Bore ratio")
    stroke: float = Field(..., description="Stroke length")
    compressionratio: float = Field(..., description="Compression ratio")
    horsepower: int = Field(..., description="Horsepower")
    peakrpm: int = Field(..., description="Peak RPM")
    citympg: int = Field(..., description="City miles per gallon")
    highwaympg: int = Field(..., description="Highway miles per gallon")
    brand: Optional[str] = Field(None, description="Car brand (optional)")

class PredictionResponse(BaseModel):
    predicted_price: float
    confidence_interval: List[float]
    important_features: Dict[str, float]
    model_performance: Dict[str, float]

class ModelInfo(BaseModel):
    model_type: str
    r2_score: float
    feature_count: int
    training_date: str
    top_features: List[Dict[str, Any]]

@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to the Car Price Prediction API",
        "docs_url": "/docs",
        "health": "ok",
        "model_status": "loaded" if model is not None else "not loaded"
    }

@app.post("/predict/", response_model=PredictionResponse)
def predict_price(car: CarSpecification):
    """Predict car price based on specifications"""
    global model, preprocessor
    
    if model is None or preprocessor is None:
        raise HTTPException(status_code=503, detail="Model is not available")
    
    try:
        # Convert input to DataFrame
        input_data = pd.DataFrame([car.dict()])
        
        # Preprocess the input
        processed_input = preprocessor.preprocess(input_data, training=False)
        
        # Remove columns that are not needed for prediction
        for col in ['CarName', 'model', 'symboling', 'car_ID', 'price']:
            if col in processed_input.columns:
                processed_input = processed_input.drop(col, axis=1)
        
        # Make prediction
        prediction = model.predict(processed_input)[0]
        
        # Calculate confidence interval (simple approximation)
        # In a production app, you'd use a more sophisticated approach
        mae = model_info.get('mae', 1500)  # Use MAE from model info or default
        confidence_interval = [max(0, prediction - 2*mae), prediction + 2*mae]
        
        # Get feature importance
        important_features = {}
        
        # Get top features from model info if available
        if model_info and 'top_features' in model_info and model_info['top_features']:
            for feature, importance in model_info['top_features']:
                important_features[feature] = float(importance)
        elif hasattr(model, 'feature_importances_'):
            # For tree-based models
            importances = dict(zip(processed_input.columns, model.feature_importances_))
            important_features = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True)[:5])
        elif hasattr(model, 'coef_'):
            # For linear models
            importances = dict(zip(processed_input.columns, np.abs(model.coef_)))
            important_features = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True)[:5])
        
        # Model performance metrics
        model_performance = {
            "r2_score": model_info.get('r2_score', 0.85),
            "rmse": model_info.get('rmse', 3000),
            "mae": model_info.get('mae', 1500)
        }
        
        return {
            "predicted_price": float(prediction),
            "confidence_interval": confidence_interval,
            "important_features": important_features,
            "model_performance": model_performance
        }
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

@app.get("/models/info", response_model=ModelInfo)
def get_model_info():
    """Return information about the model used for predictions"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not available")
    
    model_type = model_info.get('model_type', type(model).__name__)
    
    # Format top features for the response
    top_features = []
    if model_info and 'top_features' in model_info:
        for feature, importance in model_info['top_features']:
            top_features.append({
                "name": feature,
                "importance": float(importance)
            })
    
    return {
        "model_type": model_type,
        "r2_score": model_info.get('r2_score', 0.85),
        "feature_count": model_info.get('num_features', len(getattr(model, "feature_names_in_", []))),
        "training_date": model_info.get('training_date', "2023-01-01"),
        "top_features": top_features
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": model is not None,
        "preprocessor_loaded": preprocessor is not None
    }

@app.get("/car-data/options")
def get_car_data_options():
    """Get available options for categorical features"""
    if preprocessor is None or not hasattr(preprocessor, 'encoders') or not preprocessor.encoders:
        raise HTTPException(status_code=503, detail="Preprocessor not properly initialized")
    
    options = {}
    
    for feature, encoder in preprocessor.encoders.items():
        if hasattr(encoder, 'classes_'):
            options[feature] = encoder.classes_.tolist()
    
    return {"options": options}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)