from concurrent import futures
import logging

from database_service import PostgreSQLDbService

import grpc
import asyncio
import auth_service_pb2
import auth_service_pb2_grpc
from grpc_reflection.v1alpha import reflection
from auth_service import AuthService
from message_service import MessageService
import message_service_pb2
import message_service_pb2_grpc

from concurrent import futures

with open("ssl/server.key", "rb") as f:
    private_key = f.read()
with open("ssl/server.crt", "rb") as f:
    certificate_chain = f.read()

server_credentials = grpc.ssl_server_credentials(((private_key, certificate_chain),))

def run_sync_server():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # максимальное количество пользователей
    dbService = PostgreSQLDbService("habrdb", "habrpguser", "pgpwd4habr", "127.0.0.1", "5432")
    
    auth_service_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(dbService), server)
    
    SERVICE_NAMES = (
        auth_service_pb2.DESCRIPTOR.services_by_name['AuthService'].full_name,
        reflection.SERVICE_NAME,
    )
    
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    # server.add_insecure_port(f"0.0.0.0:{port}")
    server.add_secure_port(f"0.0.0.0:{port}", server_credentials)
    
    server.start()
    print(f"Sync AuthService server started on port {port}")
    server.wait_for_termination()


async def run_async_server():
    port = "50052"
    server = grpc.aio.server(options=[
    ('grpc.keepalive_time_ms', 10000), 
    ('grpc.keepalive_timeout_ms', 5000),  
    ('grpc.http2.max_pings_without_data', 0),  
]) 
    
    dbService = PostgreSQLDbService("habrdb", "habrpguser", "pgpwd4habr", "127.0.0.1", "5432")
    message_service_pb2_grpc.add_MessageServiceServicer_to_server(MessageService(dbService), server)
    
    SERVICE_NAMES = (
        message_service_pb2.DESCRIPTOR.services_by_name['MessageService'].full_name,
        reflection.SERVICE_NAME,
    )
    
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    # server.add_insecure_port(f"0.0.0.0:{port}")
    server.add_secure_port(f"0.0.0.0:{port}", server_credentials)
    
    await server.start()
    print(f"Async MessageService server started on port {port}")
    await server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig()

    sync_server_thread = futures.ThreadPoolExecutor(max_workers=10) #максимальное количество пользователей
    sync_server_thread.submit(run_sync_server)

    asyncio.run(run_async_server())
