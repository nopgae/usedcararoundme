FROM python:3.9-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Download the dataset if it doesn't exist
RUN mkdir -p data
RUN if [ ! -f data/CarPrice_Assignment.csv ]; then \
    pip install --no-cache-dir kaggle && \
    mkdir -p ~/.kaggle && \
    echo '{"username":"YOUR_KAGGLE_USERNAME","key":"YOUR_KAGGLE_KEY"}' > ~/.kaggle/kaggle.json && \
    chmod 600 ~/.kaggle/kaggle.json && \
    kaggle datasets download -d zabihullah18/car-price-prediction -p data && \
    unzip -o data/car-price-prediction.zip -d data; \
    fi

# Train the model (if it doesn't exist)
RUN if [ ! -f models/car_price_model.pkl ]; then \
    python scripts/train_model.py; \
    fi

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]