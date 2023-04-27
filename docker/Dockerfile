FROM python:3.10-slim-buster

ENV LANG=C.UTF-8 \
  LC_ALL=C.UTF-8

WORKDIR /app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
COPY index.html /usr/local/lib/python3.10/site-packages/streamlit/static/index.html

# ENTRYPOINT ["streamlit", "run", "Overview.py", "--server.port=8501", "--server.address=0.0.0.0"]
