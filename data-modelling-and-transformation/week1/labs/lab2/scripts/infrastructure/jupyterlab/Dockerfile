FROM python:3.9

WORKDIR /app

RUN apt-get update && apt-get install -y \
    awscli \
    postgresql \ 
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install jupyter -U

COPY requirements.txt .
#COPY C4_W1_Assignment.ipynb .
#COPY images/ ./images

RUN pip install --no-cache-dir -r ./requirements.txt

# Set the default AWS region
ENV AWS_DEFAULT_REGION=us-east-1

EXPOSE 8888
EXPOSE 5432

ENTRYPOINT ["jupyter-lab","--ip=0.0.0.0", "--no-browser","--allow-root"]