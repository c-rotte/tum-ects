FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.11.0/wait /wait
RUN chmod +x /wait

CMD ["/bin/bash", "-c", "/wait; python3 /app/main.py"]
