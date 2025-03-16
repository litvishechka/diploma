import logging

import grpc
import auth_service_pb2
import auth_service_pb2_grpc
import message_service_pb2
import message_service_pb2_grpc
from types_pb2 import *
from async_client import *
import queue


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
        elif cmd == '1':
            username = str(input("Введите логин: "))
            password = str(input("Введите пароль: "))
            response = stub.LoginUser(auth_service_pb2.LoginRequest(username=username, password=password))
            print(response.message)
            if response.message == "Вы успешно авторизованы!":
                return 1, response.user
        elif cmd == 'e':
            return 0, ""


def chat_menu(stub, creator_info):
    queue = asyncio.Queue()
    while True:
        print("""Выберите команду:
          0 - создание чата
          1 - подключение к чату 
          е - выход из аккаунта""")
        cmd = input()
        if cmd == '0':
            chat_name = input("Введите название чата: ")
            response = stub.GetAllUsers(message_service_pb2.GetAllUsersRequest(username=creator_info.username))
            users = []
            input_value = -1
            dictionary_users = {user.username: user for user in response.users}

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
                        chat_menu(stub, creator_info)    
            create_chat_response = stub.CreateChat(message_service_pb2.CreateChatRequest(creator=creator_info, chat_name=chat_name, users=users))
            print(create_chat_response.message)
        elif cmd == '1':
            response = stub.GetChatList(message_service_pb2.GetChatRequest(username=creator_info.username))
            print("Выберите чат, к которому хотите подключиться из представленных ниже и напишите его index: ")
            dictionary_chats = dict(enumerate(response.chats))
            for key in dictionary_chats:
                print(f"{key} - {dictionary_chats[key].chat_name}")
            input_index = int(input("Введите индекс чата, к которому хотите подключиться: ")) #TODO сделать, чтобы пользователи могли вводить только int значения
            if input_index in dictionary_chats.keys():
                asyncio.run(queue.put((dictionary_chats[input_index], creator_info)))
                asyncio.run(main(queue))
                print("+")
                # asyncio.create_task(chat_stream(stub, dictionary_chats[input_index], creator_info))
                # asyncio.run(chat_stream(stub, dictionary_chats[input_index], creator_info))

                # pass
                # # print(dictionary_chats[input_index].chat_id)
                # response = stub.ConnectToChat(message_service_pb2.ConnectRequest(chat=dictionary_chats[input_index], user=creator_info))
                # print(response.message + " Чтобы выйти из чата - напишите exit.")
                # def message_iterator():
                #     while True:
                #         message = input("Введите сообщение: ")
                #         if message.lower() == 'exit':
                #             print("Выход из чата...")
                #             break
                #         # Отправляем сообщение
                #         yield message_service_pb2.StreamRequest(chat=dictionary_chats[input_index], user=creator_info, message=message)
                
                # # Получаем поток сообщений
                # for response in stub.ChatStream(message_iterator()):
                #     print(response.user.username)
                #     if response.user.username == creator_info.username:
                #         print(f"\n[Вы]: {response.message}")
                #     else:
                #         print(f"\n[{response.user.username}]: {response.message}")
                #     # print(f"Новое сообщение от {response.user.username}: {response.message}")
                #     # send_thread = threading.Thread(target=send_messages, args=(stub, creator_info, dictionary_chats[input_index]))
                #     # receive_thread = threading.Thread(target=receive_messages, args=(stub, creator_info, dictionary_chats[input_index]))
            
                #     # send_thread.start()
                #     # receive_thread.start()

                #     # # Дожидаемся завершения потоков
                #     # send_thread.join()
                #     # receive_thread.join()
            else:
                print("Данный индекс не найден, попробуйте ещё раз!")
        elif cmd == 'e':
            return 0      


def run() -> None:
    with grpc.insecure_channel("localhost:50051") as auth_channel, grpc.insecure_channel("localhost:50052") as chat_channel:
        auth_stub = auth_service_pb2_grpc.AuthServiceStub(auth_channel)
        chat_stub = message_service_pb2_grpc.MessageServiceStub(chat_channel)

        CLOSE_CLIENT = False
        AUTH_USER = False
        user_auth_info = UserInfo()

        while not CLOSE_CLIENT:
            if AUTH_USER and len(user_auth_info.username) != 0:
                result = chat_menu(chat_stub, user_auth_info)
                if result == 0:
                    AUTH_USER = False
                    user_auth_info = UserInfo()
            else:
                result, user_auth_info = main_menu(auth_stub)
                if result == 0:
                    CLOSE_CLIENT = True
                elif result == 1:
                    AUTH_USER = True


if __name__ == "__main__":
    logging.basicConfig()
    run()


