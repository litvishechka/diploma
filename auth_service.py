from database_service import DatabaseService
import auth_service_pb2
import auth_service_pb2_grpc

class AuthService(auth_service_pb2_grpc.AuthServiceServicer):
    def __init__(self, dbs: DatabaseService):
        super().__init__()
        self.db_service = dbs


    def RegisterUser(self, request, context):
        user_info = self.db_service.get_user_info(request.username)
        if (user_info is not None):
            return auth_service_pb2.RegisterResponse(message="Пользователь с именем %s уже существует!" % request.username)
        else:
            self.db_service.add_user(request.username, request.password) 
            return auth_service_pb2.RegisterResponse(message="Вы успешно зарегистированы!")
    

    def LoginUser(self, request, context):
        user_info = self.db_service.get_user_info(request.username)
        if user_info is None:
            return auth_service_pb2.LoginResponse(message="Пользователя с именем %s не существует, попробуйте зарегистрироваться!" % request.username)
        elif user_info[1] != request.password:
            return auth_service_pb2.LoginResponse(message="Неверный логин или пароль, попробуйте ещё раз!") 
        else: 
            return auth_service_pb2.LoginResponse(message="Вы успешно авторизованы!")