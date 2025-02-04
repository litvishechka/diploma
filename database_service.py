class DatabaseService:
    def get_user_info(self, username: str, password: str)-> tuple[str, str]: 
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
    
class TextDbService(DatabaseService):
    def __init__(self, filename):
        self.filename = filename
        self.delimeter = "^_^"
        
    def get_user_info(self, username: str, password: str)-> tuple[str, str]: 
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

            


