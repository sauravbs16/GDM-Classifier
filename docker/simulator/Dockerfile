# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY ./src/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./src .

RUN ["python", "-m", "grpc_tools.protoc", "-I", "./protos", "--python_out=.", "--pyi_out=.", "--grpc_python_out=.","protos/gdm.proto"]

CMD ["python3", "gdm_simulator.py" ]