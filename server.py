from concurrent import futures
import logging

from database_service import DatabaseService, PostgreSQLDbService

import grpc
import chat_pb2
import chat_pb2_grpc
from grpc_reflection.v1alpha import reflection


class AuthService(chat_pb2_grpc.AuthServiceServicer):
    def __init__(self, dbs: DatabaseService):
        super().__init__()
        self.db_service = dbs


    def RegisterUser(self, request, context):
        user_info = self.db_service.get_user_info(request.username)
        if (user_info is not None):
            return chat_pb2.RegisterResponse(message="Пользователь с именем %s уже существует!" % request.username)
        else:
            self.db_service.add_user(request.username, request.password) 
            return chat_pb2.RegisterResponse(message="Вы успешно зарегистированы!")
    

    def LoginUser(self, request, context):
        user_info = self.db_service.get_user_info(request.username)
        if user_info is None:
            return chat_pb2.LoginResponse(message="Пользователя с именем %s не существует, попробуйте зарегистрироваться!" % request.username)
        elif user_info[1] != request.password:
            return chat_pb2.LoginResponse(message="Неверный логин или пароль, попробуйте ещё раз!") 
        else: 
            return chat_pb2.LoginResponse(message="Вы успешно авторизованы!")
        

def serve():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # dbService = TextDbService("registered_users.txt")
    dbService = PostgreSQLDbService("habrdb", "habrpguser", "pgpwd4habr", "127.0.0.1", "5432")
    chat_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(dbService), server)
    SERVICE_NAMES = (
        chat_pb2.DESCRIPTOR.services_by_name['AuthService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    server.add_insecure_port("0.0.0.0:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()