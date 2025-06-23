from concurrent import futures
import logging

import os
from dotenv import load_dotenv

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

def run_sync_server(db_service, host, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # максимальное количество пользователей
    
    auth_service_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(db_service), server)
    
    SERVICE_NAMES = (
        auth_service_pb2.DESCRIPTOR.services_by_name['AuthService'].full_name,
        reflection.SERVICE_NAME,
    )
    
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    # server.add_insecure_port(f"{host}:{port}")
    server.add_secure_port(f"{host}:{port}", server_credentials)
    
    server.start()
    print(f"Sync AuthService server started on port {port}")
    server.wait_for_termination()


async def run_async_server(db_service, host, port):
    port = "50052"
    server = grpc.aio.server(options=[
    ('grpc.keepalive_time_ms', 10000), 
    ('grpc.keepalive_timeout_ms', 5000),  
    ('grpc.http2.max_pings_without_data', 0),  
]) 
    
    
    message_service_pb2_grpc.add_MessageServiceServicer_to_server(MessageService(db_service), server)
    
    SERVICE_NAMES = (
        message_service_pb2.DESCRIPTOR.services_by_name['MessageService'].full_name,
        reflection.SERVICE_NAME,
    )
    
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    # server.add_insecure_port(f"{host}:{port}")
    server.add_secure_port(f"{host}:{port}", server_credentials)
    
    await server.start()
    print(f"Async MessageService server started on port {port}")
    await server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig()

    load_dotenv("server.env")

    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "5432"))

    server_host = os.getenv("SERVER_HOST", "0.0.0.0")
    sync_port = int(os.getenv("SERVER_SYNC_PORT", "50051"))
    async_port = int(os.getenv("SERVER_ASYNC_PORT", "50052"))

    db_service = PostgreSQLDbService(db_name, db_user, db_password, db_host, db_port)

    sync_server_thread = futures.ThreadPoolExecutor(max_workers=10) #максимальное количество пользователей
    sync_server_thread.submit(run_sync_server, db_service, server_host, sync_port)

    asyncio.run(run_async_server(db_service, server_host, async_port))
