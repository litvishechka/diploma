from concurrent import futures
import logging

from message_service_pb2 import *
import message_service_pb2
import message_service_pb2_grpc
from database_service import DatabaseService

class MessageService(message_service_pb2_grpc.MessageServiceServicer):
    def __init__(self, dbs: DatabaseService):
        super().__init__()
        self.db_service = dbs

    def CreateChat(self, request, context):
        chat_id = self.db_service.create_chat(request.chat_name)
        users_id = [user.user_id for user in request.users]
        users_id.append(request.creator.user_id)
        self.db_service.add_users_to_chat(chat_id, users_id)
        return message_service_pb2.CreateChatResponse(message=f"Чат с именем {request.chat_name} успешно создан!")
    
    def GetAllUsers(self, request, context):
        all_users = self.db_service.get_all_users(request.username)
        # for user in all_users:
        #     all_users_user_info.append(message_service_pb2.UserInfo(user_id=user[0], username=user[1]))
        return message_service_pb2.GetAllUsersResponse(users=[UserInfo(user_id=user[0], username=user[1]) for user in all_users])
    
    def GetChatList(self, request, context):
        user_chats = self.db_service.get_chats_user(request.username)
        return message_service_pb2.GetChatResponse(chats=[ChatInfo(chat_id=chat[0], chat_name=chat[1]) for chat in user_chats])