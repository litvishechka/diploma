from concurrent import futures
import logging

from database_service import PostgreSQLDbService

import grpc
import auth_service_pb2
import auth_service_pb2_grpc
from grpc_reflection.v1alpha import reflection
from auth_service import AuthService
from message_service import MessageService
import message_service_pb2
import message_service_pb2_grpc

def run():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # dbService = TextDbService("registered_users.txt")
    dbService = PostgreSQLDbService("habrdb", "habrpguser", "pgpwd4habr", "127.0.0.1", "5432")
    auth_service_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(dbService), server)
    message_service_pb2_grpc.add_MessageServiceServicer_to_server(MessageService(dbService), server)
    SERVICE_NAMES = (
        auth_service_pb2.DESCRIPTOR.services_by_name['AuthService'].full_name,
        message_service_pb2.DESCRIPTOR.services_by_name['MessageService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    server.add_insecure_port("0.0.0.0:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    run()