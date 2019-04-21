FROM python:3
RUN mkdir /httpmv
ADD . /httpmv
WORKDIR /httpmv
RUN pip install -r requirements.txt