# -------------------------------
# Step 1: Use official lightweight Python image
# -------------------------------
FROM python:3.11-slim

# -------------------------------
# Step 2: Environment setup
# -------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# -------------------------------
# Step 3: Set working directory
# -------------------------------
WORKDIR /app

# -------------------------------
# Step 4: Install dependencies
# -------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# -------------------------------
# Step 5: Copy and install Python packages
# -------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------------
# Step 6: Copy application code
# -------------------------------
COPY . .

# -------------------------------
# Step 7: Expose FastAPI port
# -------------------------------
EXPOSE 8000

# -------------------------------
# Step 8: Default command (use Uvicorn)
# -------------------------------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
