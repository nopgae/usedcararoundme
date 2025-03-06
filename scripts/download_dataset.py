#!/usr/bin/env python3
"""
Script to download the Car Price dataset from Kaggle.
To use this script, you need to have the Kaggle API credentials set up.
"""

import os
import sys
from pathlib import Path
import zipfile
import shutil

# Add the project root to the path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

def download_dataset():
    """Download the car price dataset from Kaggle"""
    try:
        # Import kaggle (will fail if not installed)
        import kaggle
    except ImportError:
        print("Kaggle API package not found. Installing it now...")
        os.system("pip install kaggle")
        import kaggle

    # Create data directory if it doesn't exist
    data_dir = project_root / "data"
    os.makedirs(data_dir, exist_ok=True)

    # Check if dataset already exists
    target_file = data_dir / "CarPrice_Assignment.csv"
    if target_file.exists():
        print(f"Dataset already exists at {target_file}")
        user_input = input("Do you want to download it again? (y/n): ")
        if user_input.lower() != 'y':
            print("Download canceled.")
            return

    # Download dataset from Kaggle
    try:
        print("Downloading dataset from Kaggle...")
        # Create a temporary directory for the download
        temp_dir = data_dir / "temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Download the dataset
        kaggle.api.dataset_download_files('zabihullah18/car-price-prediction', 
                                          path=temp_dir, 
                                          unzip=True)
        
        # Check if the downloaded dataset exists
        csv_file = next(temp_dir.glob("*.csv"), None)
        if csv_file:
            # Move the CSV file to the data directory
            shutil.copy(csv_file, target_file)
            print(f"Dataset successfully downloaded to {target_file}")
        else:
            print("Error: CSV file not found in the downloaded content.")
        
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
    
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        print("\nTo manually download the dataset:")
        print("1. Go to https://www.kaggle.com/datasets/zabihullah18/car-price-prediction")
        print("2. Download the dataset")
        print(f"3. Place the CSV file at {target_file}")
        
        # Check if it might be a Kaggle authentication issue
        kaggle_dir = Path.home() / ".kaggle"
        if not (kaggle_dir / "kaggle.json").exists():
            print("\nIt seems you don't have Kaggle API credentials set up.")
            print("To set up Kaggle API credentials:")
            print("1. Create an account on Kaggle if you don't have one")
            print("2. Go to https://www.kaggle.com/account and create an API token")
            print("3. Download the kaggle.json file")
            print(f"4. Create directory {kaggle_dir} if it doesn't exist")
            print(f"5. Place the kaggle.json file in {kaggle_dir}")
            print("6. Ensure the file permissions are correct: chmod 600 ~/.kaggle/kaggle.json")

if __name__ == "__main__":
    download_dataset()