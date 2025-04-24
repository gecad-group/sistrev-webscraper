FROM python:3.12-slim
LABEL authors="ruifpb"
LABEL description="SistRev's Data Cleaner module as a web app"
LABEL version="1.0"

WORKDIR /app
RUN apt update && apt install -y build-essential curl software-properties-common && rm -rf /var/lib/apt/lists/*

COPY streamlit-app.py datacleaner.py requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501

HEALTHCHECK CMD curl --fail https://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "streamlit-app.py", "--server.port=8501", "--server.address=0.0.0.0"]