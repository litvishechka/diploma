import logging

import grpc
import chat_pb2
import chat_pb2_grpc


def main_menu(stub):
    # Если возвращаем 0, то это выход из приложения, если - 1, то это переход в другое меню
    while True:
        print("""Выберите команду:
          0 - регистрация пользователя
          1 - авторизация
          е - выход из приложения""")
        cmd = input()
        if cmd == '0':
            username = str(input("Введите логин: "))
            password = str(input("Введите пароль: "))
            response = stub.RegisterUser(chat_pb2.RegisterRequest(username=username, password=password))
            print(response.message)
            # return 0
        elif cmd == '1':
            username = str(input("Введите логин: "))
            password = str(input("Введите пароль: "))
            response = stub.LoginUser(chat_pb2.LoginRequest(username=username, password=password))
            print(response.message)
            if response.message == "Вы успешно авторизованы!":
                return 1
        elif cmd == 'e':
            return 0


def chat_menu(stub):
    while True:
        print("""Выберите команду:
          0 - создание чата
          1 - подключение к чату 
          е - выход из аккаунта""")
        cmd = input()
        if cmd == '0':
            pass
        elif cmd == '1':
            pass
        elif cmd == 'e':
            return 0      

def run() -> None:
    with grpc.insecure_channel("localhost:50051") as channel:
        auth_stub = chat_pb2_grpc.AuthServiceStub(channel)
        chat_stub = ""

        CLOSE_CLIENT = False
        AUTH_USER = False

        while not CLOSE_CLIENT:
            if AUTH_USER:
                result = chat_menu(auth_stub)
                if result == 0:
                    AUTH_USER = False
            else:
                result = main_menu(chat_stub)
                if result == 0:
                    CLOSE_CLIENT = True
                elif result == 1:
                    AUTH_USER = True


if __name__ == "__main__":
    logging.basicConfig()
    run()