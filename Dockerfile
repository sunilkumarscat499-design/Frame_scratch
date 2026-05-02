# STEP 1: Use the official Python slim image
FROM python:3.11-slim

# STEP 2: Install system dependencies required for Playwright
# This is the "Missing Link" in your original code!
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# STEP 3: Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# STEP 4: Install Playwright Browsers AND their system dependencies
# This command is much more efficient for Docker
RUN playwright install --with-deps chromium

# STEP 5: Copy project files
COPY . .

# STEP 6: Default command to run tests
CMD ["pytest", "--alluredir=reports/allure-results"]