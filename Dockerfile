FROM python:latest
LABEL author="André Matias dev.andrematias@gmail.com"
WORKDIR /usr/src/uploader
COPY . . 

RUN echo "America/Sao_Paulo" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
RUN python -m pip install -r requirements.txt

WORKDIR /usr/src/uploader/src

CMD ["python", "uploader.py"]
