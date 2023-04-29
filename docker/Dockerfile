FROM python:3.10-slim-buster

ENV LANG=C.UTF-8 \
  LC_ALL=C.UTF-8

WORKDIR /app

COPY requirements.txt ./
# HACK: have to patch in some html to add in meta tags/Google Analytics
RUN pip3 install --no-cache-dir -r requirements.txt &&\
  cp /usr/local/lib/python3.10/site-packages/streamlit/static/index.html /usr/local/lib/python3.10/site-packages/streamlit/static/index.html.bak
COPY assets/index.html /usr/local/lib/python3.10/site-packages/streamlit/static/index.html
COPY . .
