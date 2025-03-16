import asyncio
import grpc
import message_service_pb2
import message_service_pb2_grpc
from types_pb2 import *
import queue

async def chat_stream(stub, chat_info, user_info):
    """Функция для отправки и получения сообщений в чате."""
    # username = input("Введите ваше имя: ")
    # chat_id = int(input("Введите chat_id: "))
    first_message = message_service_pb2.ChatMessage(chat=chat_info, user=user_info, message='')

    async def message_generator():
        """Генератор для отправки сообщений серверу."""
        yield first_message
        while True:
            message = await asyncio.to_thread(input, f"[{user_info.username}]: ")  # Не блокируем поток
            if message.lower() == "exit":
                print("Выход из чата.")
                return  # Прекращаем генерацию
            yield message_service_pb2.ChatMessage(chat=chat_info, user=user_info, message=message)

    async def receive_messages():
        """Обрабатывает входящие сообщения от сервера."""
        async for message in stub.ChatStream(message_generator()):
            print(f"\n[{message.user.username}]: {message.message}")

    await receive_messages()

async def main(queue):
    async with grpc.aio.insecure_channel('localhost:50052') as channel:
        stub = message_service_pb2_grpc.MessageServiceStub(channel)
        while True:
            chat_info, user_info = await queue.get()
            print(f"Получены данные из очереди: {chat_info}, {user_info}") 
            asyncio.create_task(chat_stream(stub, chat_info, user_info))

if __name__ == "__main__":
    asyncio.run(main(queue))
