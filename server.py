from concurrent import futures
import logging

from grpc_reflection.v1alpha import reflection

import grpc
import chat_pb2
import chat_pb2_grpc


class AuthService(chat_pb2_grpc.AuthServiceServicer):
    def RegisterUser(self, request, context):
        file = open("registered_users.txt", mode='+rt')
        for line in file:
            if request.username == line.split('^_^')[0]:
                return chat_pb2.RegisterResponse(message="Пользователь с именем %s уже существует!" % request.username)
                
        file.write(request.username + "^_^" + request.password)
        file.close()
        return chat_pb2.RegisterResponse(message="Вы успешно зарегистированы!")
    

    def LoginUser(self, request, context):
        file = open("registered_users.txt", mode='r')
        for line in file:
            username_txt = line.split('^_^')[0]
            password_txt = line.split('^_^')[1]
            if request.username == username_txt and request.password == password_txt:
                return chat_pb2.LoginResponse(message="Вы успешно авторизованы!")
            if request.username == username_txt and request.password != password_txt:
                return chat_pb2.LoginResponse(message="Неверный логин или пароль, попробуйте ещё раз!")
        
        file.close()
        return chat_pb2.LoginResponse(message="Пользователя с именем %s не существует, попробуйте зарегистрироваться!" % request.username)

    
           


def serve():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(), server)
    SERVICE_NAMES = (
        chat_pb2.DESCRIPTOR.services_by_name['AuthService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()