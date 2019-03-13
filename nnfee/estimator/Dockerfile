FROM python:3.6.3

RUN mkdir /myapp
WORKDIR /myapp

COPY requirements.txt /myapp/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5000

COPY . /myapp
