# Use an official Python image as the base
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose necessary ports
EXPOSE 5000  

# Start both Flask and Streamlit using a process manager
CMD ["sh", "-c", "python api.py & streamlit run app.py --server.port 8501 --server.address 0.0.0.0"]
