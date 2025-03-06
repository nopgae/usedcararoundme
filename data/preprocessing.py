import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from pathlib import Path
import sys
import joblib

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

class CarDataPreprocessor:
    """Class to handle preprocessing of car price dataset"""
    
    def __init__(self):
        self.encoders = {}
        self.scaler = StandardScaler()
        self.models_dir = project_root / "api" / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Define column groups
        self.categorical_columns = [
            'fueltype', 'aspiration', 'doornumber', 'carbody', 'drivewheel',
            'enginelocation', 'enginetype', 'cylindernumber', 'fuelsystem', 'brand'
        ]
        
        self.numerical_columns = [
            'wheelbase', 'carlength', 'carwidth', 'carheight', 'curbweight',
            'enginesize', 'boreratio', 'stroke', 'compressionratio', 'horsepower',
            'peakrpm', 'citympg', 'highwaympg'
        ]
    
    def load_data(self, filepath=None):
        """Load the car price dataset"""
        if filepath is None:
            filepath = project_root / "data" / "CarPrice_Assignment.csv"
        
        print(f"Loading data from {filepath}")
        return pd.read_csv(filepath)
    
    def extract_brands(self, df):
        """Extract brand and model from CarName"""
        print("Extracting brands from car names...")
        
        # Extract brand (first word of CarName)
        df['brand'] = df['CarName'].apply(lambda x: x.split(' ')[0].lower())
        
        # Clean and standardize brand names
        brand_mapping = {
            'maxda': 'mazda',
            'porcshce': 'porsche',
            'toyouta': 'toyota',
            'vokswagen': 'volkswagen',
            'vw': 'volkswagen'
        }
        
        df['brand'] = df['brand'].replace(brand_mapping)
        
        # Extract model (everything after the first word)
        df['model'] = df['CarName'].apply(lambda x: ' '.join(x.split(' ')[1:]))
        
        return df
    
    def encode_categorical(self, df):
        """Encode categorical features"""
        print("Encoding categorical features...")
        
        for column in self.categorical_columns:
            if column in df.columns:
                encoder = LabelEncoder()
                df[column] = encoder.fit_transform(df[column])
                self.encoders[column] = encoder
        
        # Save encoders
        joblib.dump(self.encoders, self.models_dir / "encoders.pkl")
        return df
    
    def create_features(self, df):
        """Create engineered features"""
        print("Creating engineered features...")
        
        # Power-to-weight ratio
        df['power_to_weight_ratio'] = df['horsepower'] / df['curbweight']
        
        # Price-to-horsepower ratio (for training data only)
        if 'price' in df.columns:
            df['price_per_hp'] = df['price'] / df['horsepower']
        
        # Squared terms for important features
        for column in ['enginesize', 'horsepower', 'curbweight']:
            df[f'{column}_squared'] = df[column] ** 2
        
        # Log transformations
        df['log_enginesize'] = np.log1p(df['enginesize'])
        df['log_horsepower'] = np.log1p(df['horsepower'])
        
        # Efficiency ratio
        df['highway_city_ratio'] = df['highwaympg'] / df['citympg']
        
        # Engine size per cylinder (proxy for cylinder volume)
        df['engine_size_per_cylinder'] = df.apply(
            lambda x: x['enginesize'] / self._get_cylinder_count(x['cylindernumber']) 
            if self._get_cylinder_count(x['cylindernumber']) > 0 else 0, 
            axis=1
        )
        
        return df
    
    def _get_cylinder_count(self, cylinder_value):
        """Convert cylinder number to actual count (used when dealing with encoded values)"""
        # When using raw string values
        if isinstance(cylinder_value, str):
            cylinder_map = {
                'two': 2, 'three': 3, 'four': 4, 'five': 5,
                'six': 6, 'eight': 8, 'twelve': 12
            }
            return cylinder_map.get(cylinder_value.lower(), 0)
        
        # When using encoded values, we need to map back through the encoder
        if hasattr(self, 'encoders') and 'cylindernumber' in self.encoders:
            # Get the original category name
            try:
                category_name = self.encoders['cylindernumber'].inverse_transform([cylinder_value])[0]
                return self._get_cylinder_count(category_name)
            except:
                # Default fallback if encoding mapping fails
                return 4  # Most common number of cylinders
        
        return cylinder_value  # If it's already a number
    
    def scale_numerical(self, df):
        """Scale numerical features"""
        print("Scaling numerical features...")
        
        # Only fit the scaler during training
        df[self.numerical_columns] = self.scaler.fit_transform(df[self.numerical_columns])
        
        # Save scaler
        joblib.dump(self.scaler, self.models_dir / "scaler.pkl")
        
        return df
    
    def preprocess(self, df, training=True):
        """Full preprocessing pipeline"""
        print("Starting preprocessing pipeline...")
        
        # Extract brands
        df = self.extract_brands(df)
        
        # Encode categorical features
        df = self.encode_categorical(df)
        
        # Create engineered features
        df = self.create_features(df)
        
        # Scale numerical features
        if training:
            df = self.scale_numerical(df)
        else:
            # For inference, use the saved scaler
            scaler_path = self.models_dir / "scaler.pkl"
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
                df[self.numerical_columns] = self.scaler.transform(df[self.numerical_columns])
            else:
                print("Warning: Scaler not found. Using unscaled features.")
        
        print("Preprocessing complete.")
        return df

if __name__ == "__main__":
    # Example usage
    preprocessor = CarDataPreprocessor()
    df = preprocessor.load_data()
    processed_df = preprocessor.preprocess(df)
    
    # Show the processed data
    print("\nProcessed Data Preview:")
    print(processed_df.head())
    
    # Show feature list
    print("\nTotal features after preprocessing:", processed_df.shape[1])
    print("\nFeature list:")
    for column in processed_df.columns:
        print(f"- {column}")