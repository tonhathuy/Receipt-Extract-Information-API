FROM ubuntu:18.04 

RUN apt update  

RUN apt-get install -y git \
    software-properties-common \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt update && \
    apt install python3.6 -y && \
    apt install python3-distutils -y && \
    apt install python3.6-dev -y && \
    apt install build-essential -y && \
    apt-get install python3-pip -y && \
    apt update && apt install -y libsm6 libxext6 && \
    apt-get install -y libxrender-dev

COPY . /FLASK_API

RUN cd FLASK_API && \
    pip3 install -r requirements.txt

WORKDIR /FLASK_API

CMD python3 app.py
# CMD ["/bin/bash", "entrypoint.sh"]
