FROM python:3.12-slim

ADD ./protos /protos
ADD ./ssl /ssl
COPY requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

RUN python -m grpc_tools.protoc -I ./protos/ --python_out=. --pyi_out=. --grpc_python_out=. ./protos/types.proto
RUN python -m grpc_tools.protoc -I ./protos/ --python_out=. --pyi_out=. --grpc_python_out=. ./protos/auth_service.proto
RUN python -m grpc_tools.protoc -I ./protos/ --python_out=. --pyi_out=. --grpc_python_out=. ./protos/message_service.proto

ADD database_service.py /
ADD auth_service.py /
ADD message_service.py /

ADD server.py /

CMD ["python", "./server.py"]