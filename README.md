# My diploma project

Для генерации кода:
```
python -m grpc_tools.protoc -I ~/diploma --python_out=. --pyi_out=. --grpc_python_out=. ~/diploma/chat.proto
```

Для запуска клиента:
'''
grpcui -plaintext localhost:your_value
'''