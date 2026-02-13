FROM mcr.microsoft.com/playwright/python:v1.57.0-jammy

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Run the bot
EXPOSE 7860
CMD ["python", "main.py"]
