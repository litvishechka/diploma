from concurrent import futures
import logging

import asyncio
import grpc
from message_service_pb2 import *
import message_service_pb2
import message_service_pb2_grpc
from database_service import DatabaseService
from types_pb2 import *
from datetime import datetime
import pytz


class MessageService(message_service_pb2_grpc.MessageServiceServicer):
    def __init__(self, dbs: DatabaseService):
        super().__init__()
        self.db_service = dbs
        self.clients: dict[int, set] = {}

    async def CreateChat(self, request, context):
        chat_id = self.db_service.create_chat(request.chat_name)
        users_id = [user.user_id for user in request.users]
        users_id.append(request.creator.user_id)
        self.db_service.add_users_to_chat(chat_id, users_id)
        return message_service_pb2.CreateChatResponse(message=f"Чат с именем {request.chat_name} успешно создан!")
    
    async def GetAllUsers(self, request, context):
        all_users = self.db_service.get_all_users(request.username)
        return message_service_pb2.GetAllUsersResponse(users=[UserInfo(user_id=user[0], username=user[1]) for user in all_users])
    
    async def GetChatList(self, request, context):
        user_chats = self.db_service.get_chats_user(request.username)
        return message_service_pb2.GetChatResponse(chats=[ChatInfo(chat_id=chat[0], chat_name=chat[1]) for chat in user_chats])
    
    async def ConnectToChat(self, request, context):
        # print(request.chat.chat_id)
        if request.chat.chat_id not in self.active_chats_users:
            self.active_chats_users[request.chat.chat_id] = []

        if request.user.user_id not in self.active_chats_users[request.chat.chat_id]:
            self.active_chats_users[request.chat.chat_id].append(request.user)

        print(self.active_chats_users)
        return message_service_pb2.ConnectResponse(message="Вы успешно подключились к чату!")
    
    async def UploadMessages(self, request, context):
        messages = self.db_service.upload_messages(request.chat.chat_id, request.number_messages)
        for message in messages:
            print(message)
            yield message_service_pb2.ChatMessage(chat=ChatInfo(chat_id=message[0], chat_name=message[1]), user=UserInfo(user_id=message[2], username=message[3]), message=message[4])
        print(messages)

    async def ChatStream(self, request_iterator, context):
        """Обрабатывает поток сообщений от клиентов и рассылает другим клиентам."""
        first_message = await anext(request_iterator, None)
        print(f"Recieve {first_message=}")
        if not first_message or not first_message.chat.chat_id:
            raise ValueError("Вы не указали идентификатор чата.")  

        chat_id = first_message.chat.chat_id
        queue = asyncio.Queue() 
        if not chat_id in self.clients.keys():
            self.clients[chat_id] = set([queue])
        else:
            self.clients[chat_id].add(queue)  
        print("Новый клиент подключен")

        async def send_messages():
            """Отправляет клиенту новые сообщения."""
            try:
                while True:
                    message = await queue.get()  
                    if message is None:
                        break
                    yield message  
            except asyncio.CancelledError:
                print("Отключение клиента...")
            finally:
                if chat_id in self.clients.keys():
                    self.clients[chat_id].discard(queue)  # Безопасное удаление
                    if not self.clients[chat_id]:  # Если чата больше нет, удаляем ключ
                        del self.clients[chat_id]
                    

        async def receive_messages():
            """Принимает сообщения от клиента и рассылает другим."""
            try:
                async for message in request_iterator:
                    if message.message != "exit":
                        local_time = datetime.now()
                        utc_time = local_time.astimezone(pytz.utc)
                        self.db_service.add_message(message.user.user_id, message.chat.chat_id, message.message, utc_time)
                    if message.message.lower() == "exit":  # Клиент отправил команду выхода
                        print(f"Клиент {message.user.username} выходит из чата {chat_id}")
                        break

                    print(f"[{message.user.username}]: {message.message}")
                    for client_queue in self.clients[message.chat.chat_id]:
                        # if client_queue is not queue:
                        await client_queue.put(message)
            except grpc.aio.AioRpcError as e:
                print(f"Ошибка gRPC: {e.details()}")
            except Exception as e:
                print(f"Ошибка сервера: {e}")
            finally:
                self.clients[chat_id].discard(queue)  
                if not self.clients[chat_id]:  
                    del self.clients[chat_id]
                await queue.put(None)  

        receive_task = asyncio.create_task(receive_messages())

        try:
            async for message in send_messages():
                yield message
        except asyncio.CancelledError:
            pass
        finally:
            receive_task.cancel()  