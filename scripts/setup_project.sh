#!/bin/bash
# Full setup script for the Car Price Prediction project

# Exit on error
set -e

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Car Price Prediction Project Setup${NC}"
echo -e "${BLUE}======================================${NC}"

# Function to create necessary directories
create_directories() {
    echo -e "\n${BLUE}Creating project directories...${NC}"
    
    mkdir -p "$PROJECT_ROOT/api/models"
    mkdir -p "$PROJECT_ROOT/data"
    mkdir -p "$PROJECT_ROOT/notebooks/visualizations"
    mkdir -p "$PROJECT_ROOT/frontend/src/components"
    
    echo -e "${GREEN}Directories created successfully.${NC}"
}

# Function to set up Python environment
setup_python_env() {
    echo -e "\n${BLUE}Setting up Python environment...${NC}"
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Python 3 is not installed. Please install Python 3 and try again.${NC}"
        exit 1
    fi
    
    # Create and activate virtual environment
    if [ -d "$PROJECT_ROOT/venv" ]; then
        echo -e "${YELLOW}Virtual environment already exists.${NC}"
    else
        echo -e "${BLUE}Creating virtual environment...${NC}"
        python3 -m venv "$PROJECT_ROOT/venv"
        echo -e "${GREEN}Virtual environment created.${NC}"
    fi
    
    # Activate virtual environment
    source "$PROJECT_ROOT/venv/bin/activate"
    
    # Install dependencies
    echo -e "${BLUE}Installing Python dependencies...${NC}"
    pip install --upgrade pip
    
    # Check if requirements.txt exists, otherwise create a basic one
    if [ ! -f "$PROJECT_ROOT/requirements.txt" ]; then
        echo -e "${YELLOW}requirements.txt not found, creating one...${NC}"
        cat > "$PROJECT_ROOT/requirements.txt" << EOF
fastapi==0.95.1
uvicorn==0.22.0
pydantic==1.10.8
numpy==1.24.3
pandas==2.0.1
scikit-learn==1.2.2
joblib==1.2.0
matplotlib==3.7.1
seaborn==0.12.2
kaggle==1.5.13
python-multipart==0.0.6
pytest==7.3.1
requests==2.31.0
EOF
    fi
    
    pip install -r "$PROJECT_ROOT/requirements.txt"
    echo -e "${GREEN}Python dependencies installed.${NC}"
}

# Function to download the dataset
download_dataset() {
    echo -e "\n${BLUE}Downloading the car price dataset...${NC}"
    
    # Check if dataset already exists
    if [ -f "$PROJECT_ROOT/data/CarPrice_Assignment.csv" ]; then
        echo -e "${YELLOW}Dataset already exists. Do you want to download it again? (y/n)${NC}"
        read -r download_again
        if [ "$download_again" != "y" ]; then
            echo -e "${BLUE}Skipping dataset download.${NC}"
            return
        fi
    fi
    
    # Try to use the Python script to download
    if python "$SCRIPT_DIR/download_dataset.py"; then
        echo -e "${GREEN}Dataset downloaded successfully.${NC}"
    else
        echo -e "${YELLOW}Automatic download failed. Trying alternative method...${NC}"
        
        # Direct download using curl
        echo -e "${BLUE}Downloading dataset directly...${NC}"
        curl -o "$PROJECT_ROOT/data/CarPrice_Assignment.csv" -L "https://raw.githubusercontent.com/JWarmenhoven/ISLR-python/master/Notebooks/Data/Auto.csv" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Dataset downloaded successfully.${NC}"
        else
            echo -e "${RED}Failed to download the dataset. Please download it manually:${NC}"
            echo -e "1. Go to https://www.kaggle.com/datasets/zabihullah18/car-price-prediction"
            echo -e "2. Download the dataset"
            echo -e "3. Place the CSV file at $PROJECT_ROOT/data/CarPrice_Assignment.csv"
        fi
    fi
}

# Function to train models
train_models() {
    echo -e "\n${BLUE}Training price prediction models...${NC}"
    
    # Check if dataset exists
    if [ ! -f "$PROJECT_ROOT/data/CarPrice_Assignment.csv" ]; then
        echo -e "${RED}Dataset not found. Please download it first.${NC}"
        return 1
    fi
    
    # Ask which model to train
    echo -e "${BLUE}Which model would you like to train?${NC}"
    echo -e "1) Linear Regression (fastest)"
    echo -e "2) Ridge Regression"
    echo -e "3) Random Forest"
    echo -e "4) Gradient Boosting (best accuracy)"
    echo -e "5) All models (compare and select best)"
    read -r model_choice
    
    case $model_choice in
        1)
            python "$SCRIPT_DIR/train_model.py" --model linear --plot
            ;;
        2)
            python "$SCRIPT_DIR/train_model.py" --model ridge --tune --plot
            ;;
        3)
            python "$SCRIPT_DIR/train_model.py" --model rf --tune --plot
            ;;
        4)
            python "$SCRIPT_DIR/train_model.py" --model gbm --tune --plot
            ;;
        5)
            python "$SCRIPT_DIR/train_model.py" --model all
            ;;
        *)
            echo -e "${RED}Invalid choice. Training linear model by default.${NC}"
            python "$SCRIPT_DIR/train_model.py" --model linear
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Model training completed successfully.${NC}"
    else
        echo -e "${RED}Model training failed.${NC}"
        return 1
    fi
}

# Function to set up frontend
setup_frontend() {
    echo -e "\n${BLUE}Setting up frontend...${NC}"
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        echo -e "${RED}Node.js is not installed. Skipping frontend setup.${NC}"
        echo -e "${YELLOW}To set up the frontend, install Node.js and npm, then run:${NC}"
        echo -e "cd $PROJECT_ROOT/frontend && npm install"
        return
    fi
    
    # Check if frontend exists
    if [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
        echo -e "${YELLOW}Frontend already set up. Do you want to reinstall dependencies? (y/n)${NC}"
        read -r reinstall
        if [ "$reinstall" != "y" ]; then
            echo -e "${BLUE}Skipping frontend setup.${NC}"
            return
        fi
    else
        # Create React app or copy template
        echo -e "${BLUE}Initializing React frontend...${NC}"
        
        # Check if create-react-app is installed
        if ! command -v create-react-app &> /dev/null; then
            echo -e "${YELLOW}create-react-app not found. Installing globally...${NC}"
            npm install -g create-react-app
        fi
        
        # Create React app
        cd "$PROJECT_ROOT"
        npx create-react-app frontend
    fi
    
    # Install frontend dependencies
    cd "$PROJECT_ROOT/frontend"
    echo -e "${BLUE}Installing frontend dependencies...${NC}"
    npm install axios recharts tailwindcss @headlessui/react
    
    # Setup Tailwind CSS
    npx tailwindcss init
    
    # Create a basic tailwind config
    cat > "$PROJECT_ROOT/frontend/tailwind.config.js" << EOF
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF
    
    # Add Tailwind directives to CSS
    cat > "$PROJECT_ROOT/frontend/src/index.css" << EOF
@tailwind base;
@tailwind components;
@tailwind utilities;
EOF
    
    echo -e "${GREEN}Frontend setup completed.${NC}"
}

# Function to start the services
start_services() {
    echo -e "\n${BLUE}Starting services...${NC}"
    
    # Start backend in the background
    echo -e "${BLUE}Starting API server...${NC}"
    cd "$PROJECT_ROOT"
    source "$PROJECT_ROOT/venv/bin/activate"
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 &
    API_PID=$!
    
    # Start frontend in the background if it exists
    if [ -d "$PROJECT_ROOT/frontend" ]; then
        echo -e "${BLUE}Starting frontend development server...${NC}"
        cd "$PROJECT_ROOT/frontend"
        npm start &
        FRONTEND_PID=$!
    fi
    
    echo -e "${GREEN}Services started!${NC}"
    echo -e "${BLUE}API is running at: ${GREEN}http://localhost:8000${NC}"
    echo -e "${BLUE}API Documentation: ${GREEN}http://localhost:8000/docs${NC}"
    if [ -d "$PROJECT_ROOT/frontend" ]; then
        echo -e "${BLUE}Frontend is running at: ${GREEN}http://localhost:3000${NC}"
    fi
    
    echo -e "\n${YELLOW}Press Ctrl+C to stop the services${NC}"
    
    # Wait for user to press Ctrl+C
    trap "kill $API_PID 2>/dev/null; kill $FRONTEND_PID 2>/dev/null; echo -e '\n${GREEN}Services stopped.${NC}'" INT
    wait
}

# Main function to orchestrate the setup
main() {
    create_directories
    
    echo -e "\n${YELLOW}What would you like to set up?${NC}"
    echo -e "1) Complete setup (Python + Dataset + Models + Frontend)"
    echo -e "2) Python environment only"
    echo -e "3) Download dataset only"
    echo -e "4) Train models only"
    echo -e "5) Frontend setup only"
    echo -e "6) Start services"
    read -r setup_choice
    
    case $setup_choice in
        1)
            setup_python_env
            download_dataset
            train_models
            setup_frontend
            start_services
            ;;
        2)
            setup_python_env
            ;;
        3)
            setup_python_env
            download_dataset
            ;;
        4)
            setup_python_env
            train_models
            ;;
        5)
            setup_frontend
            ;;
        6)
            start_services
            ;;
        *)
            echo -e "${RED}Invalid choice.${NC}"
            exit 1
            ;;
    esac
}

# Execute main function
main

exit 0