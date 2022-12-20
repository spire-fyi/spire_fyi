FROM python:3.10-slim-buster

EXPOSE 8501

ENV LANG=C.UTF-8 \
  LC_ALL=C.UTF-8 \
  PATH="${PATH}:/root/.poetry/bin"

WORKDIR /app

# #TODO: Remove poetry?
# RUN apt-get update && \
#   apt-get install -y --no-install-recommends \
#   curl \
#   && rm -rf /var/lib/apt/lists/*

# # Install Poetry
# RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 && \
#     cd /usr/local/bin && \
#     ln -s /opt/poetry/bin/poetry && \
#     poetry config virtualenvs.create false

# # Allow installing dev dependencies to run tests
# ARG INSTALL_DEV=false
# RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

COPY requirements.txt ./
RUN pip3 install  --no-cache-dir -r  requirements.txt

COPY . .

# ENTRYPOINT ["streamlit", "run", "Overview.py", "--server.port=8501", "--server.address=0.0.0.0"]
