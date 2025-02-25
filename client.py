import logging

import grpc
import chat_pb2
import chat_pb2_grpc


def run() -> None:
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = chat_pb2_grpc.AuthServiceStub(channel)
        print("Для регистрации нажмите - 0, для авторизации - 1, выхода - Ctr+C")
        while True:
            cmd = int(input())
            if cmd == 0:
                username = str(input("Введите логин: "))
                password = str(input("Введите пароль: "))
                response = stub.RegisterUser(chat_pb2.RegisterRequest(username=username, password=password))
                print(response.message)
            elif cmd == 1:
                username = str(input("Введите логин: "))
                password = str(input("Введите пароль: "))
                response = stub.LoginUser(chat_pb2.LoginRequest(username=username, password=password))
                print(response.message)



if __name__ == "__main__":
    logging.basicConfig()
    run()