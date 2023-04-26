FROM python:3.10

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.11.0/wait /wait
RUN chmod +x /wait

CMD ["/bin/bash", "-c", "/wait; python3 main.py"]