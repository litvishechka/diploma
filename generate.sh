#!/bin/sh

python -m grpc_tools.protoc -I ./protos/ --python_out=. --pyi_out=. --grpc_python_out=. ./protos/types.proto
python -m grpc_tools.protoc -I ./protos/ --python_out=. --pyi_out=. --grpc_python_out=. ./protos/auth_service.proto
python -m grpc_tools.protoc -I ./protos/ --python_out=. --pyi_out=. --grpc_python_out=. ./protos/message_service.proto