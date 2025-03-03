import psycopg2

class DatabaseService:
    def get_user_info(self, username: str)-> tuple[str, str]: 
        """
            Этот метод возвращает пару (username, password) для заданного username, 
            если такая пара находится в базе данных.
            Иначе возвращается None.
        """
        raise NotImplementedError("Метод get_user_info не реализован.")
    
    def add_user(self, username: str, password: str) -> bool:
        """
            Этот метод добавляет новую пару (username, password) в хранилище.
            Возвращает булевое значение в зависимости от успешности записи в БД.
        """
        raise NotImplementedError("Метод add_user не реализован.")
    
    def create_chat(self, chat_name: str):
        """
            Этот метод создаёт чат, добавляет его в хранилище.
            Возращает его id.
        """
        raise NotImplementedError("Метод create_chat не реализован.")
    
    def get_all_users(self, username: str):
        """Метод возвращает всех пользователей."""
        raise NotImplementedError("Метод get_all_users не реализован.")
    
    def add_users_to_chat(self, creator: str, chat_name: str, users: list):
        """
            Этот метод добавляет пользователей в нужный чат.
        """
        raise NotImplementedError("Метод add_to_chat не реализован.")
    
class TextDbService(DatabaseService):
    def __init__(self, filename):
        self.filename = filename
        self.delimeter = "^_^"


    def get_user_info(self, username: str)-> tuple[str, str]: 
        file = open(self.filename, mode='r')
        found_username = ""
        found_password = ""
        for line in file:
            line = line.strip()

            if username == line.split(self.delimeter)[0]:
                found_username = line.split(self.delimeter)[0]
                found_password = line.split(self.delimeter)[1]
                break

        if len(found_username) != 0 and len(found_password) != 0:
            return found_username, found_password
        return None  
    

    def add_user(self, username: str, password: str) -> bool:
        file = open(self.filename, mode='a')
        file.write(username + self.delimeter + password+ "\n")
        file.close()
        return True    

            
class PostgreSQLDbService(DatabaseService):
    def __init__(self, dbname, user, password, host, port):
        # Создание соединение с базой данных и сохрание переменной в данном экземпляре (self)
        self.connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        self.__create_tables()

    def __del__(self):
        self.connection.close()


    def __create_tables(self):
        # Создание таблиц, если они ещё не были созданы
        commands = (
        """ CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            user_name VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(50) NOT NULL
        )
        """,
        """ CREATE TABLE IF NOT EXISTS chat(
                chat_id SERIAL PRIMARY KEY,
                chat_name VARCHAR(50) NOT NULL
                )
        """,
        """
        CREATE TABLE IF NOT EXISTS user_chat(
                user_chat_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                FOREIGN KEY (user_id)
                    REFERENCES users (user_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (chat_id)
                    REFERENCES chat (chat_id)
                    ON UPDATE CASCADE ON DELETE CASCADE    
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS message(
                message_id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                date_created DATE NOT NULL,
                FOREIGN KEY (user_id)
                    REFERENCES users (user_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (chat_id)
                    REFERENCES chat (chat_id)
                    ON UPDATE CASCADE ON DELETE CASCADE   
        )
        """)
        cursor = self.connection.cursor()
        for command in commands:
            cursor.execute(command)
        cursor.close()
        self.connection.commit()
        # pass


    def get_user_info(self, username: str)-> tuple[str, str]: 
        cursor = self.connection.cursor()
        cursor.execute("SELECT user_name, password FROM users")
        users_passwords = cursor.fetchall()
        for row in users_passwords:
            found_username = row[0] 
            found_password = row[1]
            if found_username == username:
                return found_username, found_password
        return None
        # pass


    def add_user(self, username: str, password: str) -> bool:
        cursor = self.connection.cursor()
        cursor.execute(f"INSERT INTO users(user_name, password) VALUES (\'{username}\', \'{password}\')")
        self.connection.commit()
        cursor.close()

    def create_chat(self, chat_name):
        cursor = self.connection.cursor()
        cursor.execute(f"INSERT INTO chat(chat_name) VALUES (\'{chat_name}\')")
        self.connection.commit()
        cursor.execute(f"SELECT chat_id FROM chat WHERE chat_name = \'{chat_name}\' ORDER BY chat_id DESC LIMIT 1")
        result = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return result
    
    def get_all_users(self, username: str):
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT user_id, user_name FROM users")
        result = cursor.fetchall()
        # for i in range(len(result)):
        #     if result[i][1] == username:
        #         temp = list(result[i])
        #         temp[1] += " (вы)"
        #         result[i] = tuple(temp)
        return result    
    
    def add_users_to_chat(self, chat_id, users: list[int]):
        #chat_id приходит как элемент листа
        values = []
        for user_id in users:
            values.append(tuple([user_id, chat_id[0]]))
        # print(values)
        cursor = self.connection.cursor()
        cursor.executemany("INSERT INTO user_chat(user_id, chat_id) VALUES(%s,%s)", values)
        self.connection.commit()
        cursor.close()
