from database_service import DatabaseService
import auth_service_pb2
import auth_service_pb2_grpc
from types_pb2 import *
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

class AuthService(auth_service_pb2_grpc.AuthServiceServicer):
    def __init__(self, dbs: DatabaseService):
        super().__init__()
        self.db_service = dbs


    def RegisterUser(self, request, context):
        user_info = self.db_service.get_user_info(request.username)
        if (user_info is not None):
            return auth_service_pb2.RegisterResponse(message="Пользователь с именем %s уже существует!" % request.username)
        else:
            hashed_password = ph.hash(request.password)
            print(hashed_password)
            self.db_service.add_user(request.username, hashed_password) 
            return auth_service_pb2.RegisterResponse(message="Вы успешно зарегистированы!")
    

    def LoginUser(self, request, context):
        user_info = self.db_service.get_user_info(request.username)
        # print(user_info[2])
        # print(request.password)
        # print(ph.verify(user_info[2], request.password))
        if user_info is None:
            return auth_service_pb2.LoginResponse(message="Пользователя с именем %s не существует, попробуйте зарегистрироваться!" % request.username)
        
        # elif user_info[2] != request.password:
        # elif ph.verify(user_info[2], request.password) == False:
        #     return auth_service_pb2.LoginResponse(message="Неверный логин или пароль, попробуйте ещё раз!") 
        # else: 
        #     return auth_service_pb2.LoginResponse(user=UserInfo(user_id=user_info[0], username=user_info[1]), message="Вы успешно авторизованы!")
        try:
            ph.verify(user_info[2], request.password)
            return auth_service_pb2.LoginResponse(user=UserInfo(user_id=user_info[0], username=user_info[1]), message="Вы успешно авторизованы!")
        except VerifyMismatchError:
            return auth_service_pb2.LoginResponse(message="Неверный логин или пароль, попробуйте ещё раз!")