import logging

import grpc
import auth_service_pb2
import auth_service_pb2_grpc
import message_service_pb2
import message_service_pb2_grpc



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
            response = stub.RegisterUser(auth_service_pb2.RegisterRequest(username=username, password=password))
            print(response.message)
            # return 0
        elif cmd == '1':
            username = str(input("Введите логин: "))
            password = str(input("Введите пароль: "))
            response = stub.LoginUser(auth_service_pb2.LoginRequest(username=username, password=password))
            print(response.message)
            if response.message == "Вы успешно авторизованы!":
                return 1, username
        elif cmd == 'e':
            return 0, ""


def chat_menu(stub, creator):
    while True:
        print("""Выберите команду:
          0 - создание чата
          1 - подключение к чату 
          е - выход из аккаунта""")
        cmd = input()
        if cmd == '0':
            chat_name = input("Введите название чата: ")
            response = stub.GetAllUsers(message_service_pb2.GetAllUsersRequest(username=creator))
            users = []
            input_value = -1
            dictionary_users = {user.username: user for user in response.users}
            creator_info = dictionary_users[creator]
            print(dictionary_users)
            while input_value != 1: 
                username = input("Введите username пользователя, которого хотите добавить в чат: ")
                if username in dictionary_users.keys():
                        users.append(dictionary_users[username])
                        print("Пользователь добавлен в список!") # TODO: Поправить сообщение
                        print("""Выберите команду: 
                            0 - добавить ещё одного пользователя
                            1 - завершить создание чата""")
                        input_value = int(input())
                else: 
                    print("Такой пользователь не найден!")
                    print("""Выберите команду:
                        0 - попробовать ещё раз
                        1 - выйти в меню пользователя""")
                    input_value = int(input())
                    if input_value == 1:
                        chat_menu(stub, creator)    
            create_chat_response = stub.CreateChat(message_service_pb2.CreateChatRequest(creator=creator_info, chat_name=chat_name, users=users))
            print(create_chat_response.message)
        elif cmd == '1':
            response = stub.GetChatList(message_service_pb2.GetChatRequest(username=creator))
            print("Выберите чат, к которому хотите подключиться из представленных ниже и напишите его index: ")
            # dictionary_chats = {chat.chat_name: chat for chat in response.chats}
            dictionary_chats = dict(enumerate(response.chats))
            for key in dictionary_chats:
                print(f"{key} - {dictionary_chats[key].chat_name}")
            input_index = int(input("Введите индекс чата, к которому хотите подключиться: "))
            if input_index in dictionary_chats.keys():
                pass
                #запрос на подключение
            else:
                print("Данный индекс не найден, попробуйте ещё раз!")
        elif cmd == 'e':
            return 0      

def run() -> None:
    with grpc.insecure_channel("localhost:50051") as channel:
        auth_stub = auth_service_pb2_grpc.AuthServiceStub(channel)
        chat_stub = message_service_pb2_grpc.MessageServiceStub(channel)

        CLOSE_CLIENT = False
        AUTH_USER = False
        username_auth = ""

        while not CLOSE_CLIENT:
            if AUTH_USER and len(username_auth) != 0:
                result = chat_menu(chat_stub, username_auth)
                if result == 0:
                    AUTH_USER = False
                    username_auth = ""
            else:
                result, username_auth = main_menu(auth_stub)
                if result == 0:
                    CLOSE_CLIENT = True
                elif result == 1:
                    AUTH_USER = True


if __name__ == "__main__":
    logging.basicConfig()
    run()