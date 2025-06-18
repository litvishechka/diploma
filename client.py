import logging
import asyncio

import grpc
import auth_service_pb2
import auth_service_pb2_grpc
import message_service_pb2
import message_service_pb2_grpc
from types_pb2 import UserInfo
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout


with open("ssl/server.crt", "rb") as f:
    trusted_certs = f.read()

credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)

def main_menu(stub):
    # Если возвращаем 0, то это выход из приложения, если - 1, то это переход в другое меню
    while True:
        print("""Выберите команду:
          0 - регистрация пользователя
          1 - авторизация
          е - выход из приложения""")
        cmd = input()
        if cmd == '0':
            username = str(input("Введите логин: ").encode("utf-8", errors="ignore").decode("utf-8"))
            password = str(input("Введите пароль: ").encode("utf-8", errors="ignore").decode("utf-8"))
            response = stub.RegisterUser(auth_service_pb2.RegisterRequest(username=username, password=password))
            print(response.message)
        elif cmd == '1':
            username = str(input("Введите логин: ").encode("utf-8", errors="ignore").decode("utf-8"))
            password = str(input("Введите пароль: ").encode("utf-8", errors="ignore").decode("utf-8"))
            response = stub.LoginUser(auth_service_pb2.LoginRequest(username=username, password=password))
            print(response.message)
            if response.message == "Вы успешно авторизованы!":
                return 1, response.user
        elif cmd == 'e':
            return 0, ""


async def chat_menu(creator_info):
    # async with grpc.aio.insecure_channel("localhost:50052") as async_channel:
    async with grpc.aio.secure_channel("localhost:50052", credentials) as async_channel:
        stub = message_service_pb2_grpc.MessageServiceStub(async_channel)
        while True:
            print("""Выберите команду:
            0 - создание чата
            1 - подключение к чату 
            е - выход из аккаунта""")
            cmd = input()
            if cmd == '0':
                await create_chat(stub, creator_info)
            elif cmd == '1':
                response = await stub.GetChatList(message_service_pb2.GetChatRequest(username=creator_info.username))
                print("Выберите чат, к которому хотите подключиться из представленных ниже и напишите его index: ")
                dictionary_chats = dict(enumerate(response.chats))
                for key in dictionary_chats:
                    print(f"{key} - {dictionary_chats[key].chat_name}")
                input_index = int(input("Введите индекс чата, к которому хотите подключиться: ").encode("utf-8", errors="ignore").decode("utf-8"))
                if input_index in dictionary_chats.keys(): 
                    number_messages = int(input("Введите количество сообщений, которые хотите подгрузить: ").encode("utf-8", errors="ignore").decode("utf-8"))
                    async for message in stub.UploadMessages(message_service_pb2.UploadRequest(chat=dictionary_chats[input_index],  number_messages=number_messages)):
                        print(f"[{message.user.username}]: {message.message}")
                    print("Чтобы выйти из чата - напишите exit.")
                    await chat_stream(stub, dictionary_chats[input_index], creator_info)
                else:
                    print("Данный индекс не найден, попробуйте ещё раз!")
            elif cmd == 'e':
                return 0    

async def create_chat(stub, creator_info):
    chat_name = input("Введите название чата: ")
    response = await stub.GetAllUsers(message_service_pb2.GetAllUsersRequest(username=creator_info.username))
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
                return 0    
    create_chat_response = await stub.CreateChat(message_service_pb2.CreateChatRequest(creator=creator_info, chat_name=chat_name, users=users))
    print(create_chat_response.message)  

async def chat_stream(stub, chat_info, user_info):
    """Функция для отправки и получения сообщений в чате."""
    first_message = message_service_pb2.ChatMessage(chat=chat_info, user=user_info, message='')

    async def message_generator():
        """Генератор для отправки сообщений серверу."""
        yield first_message
        session = PromptSession()
        while True:
            with patch_stdout():
                message = await session.prompt_async(">>> ")
            print('\033[1A' + '\033[K', end="", flush=True)
            if message.lower() == "exit":
                print("Выход из чата.")
                yield message_service_pb2.ChatMessage(chat=chat_info, user=user_info, message=message)
                return 
            yield message_service_pb2.ChatMessage(chat=chat_info, user=user_info, message=message)

    async def receive_messages():
        """Обрабатывает входящие сообщения от сервера."""
        async for message in stub.ChatStream(message_generator()):
            print(f"[{message.user.username}]: {message.message}")

    await receive_messages()

def run() -> None:
    # with grpc.insecure_channel("localhost:50051") as sync_channel:
    with grpc.secure_channel("localhost:50051", credentials) as sync_channel:
        auth_stub = auth_service_pb2_grpc.AuthServiceStub(sync_channel)

        CLOSE_CLIENT = False
        AUTH_USER = False
        user_auth_info = UserInfo()

        while not CLOSE_CLIENT:
            if AUTH_USER and len(user_auth_info.username) != 0:
                result = asyncio.run(chat_menu(user_auth_info))
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
