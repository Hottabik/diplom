import paramiko
import pymysql
from sshtunnel import SSHTunnelForwarder
from getpass import getpass

# Учетные данные для SSH
ssh_host = '5.35.73.210'  # Адрес удаленного сервера
ssh_port = 23000                   # Порт SSH
ssh_user = 'asd'           # Имя пользователя SSH
ssh_password = 12345

# Учетные данные для MySQL
mysql_host = 'localhost'        # На удаленном сервере подключаемся к localhost
mysql_port = 6603               # Порт MySQL
mysql_user = 'abbas'          # Пользователь MySQL
mysql_password = 'Password123!'  # Пароль MySQL
mysql_db = 'diplom'      # Имя базы данных

def create_ssh_mysql_connect():
    try:
        # Создаем SSH туннель
        with SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_username=ssh_user,
            ssh_password=ssh_password,
            remote_bind_address=(mysql_host, mysql_port)
        ) as tunnel:
            print(f"SSH tunnel established on local port: {tunnel.local_bind_port}")
            
            # Подключаемся к MySQL через SSH туннель
            connection = pymysql.connect(
                host='127.0.0.1',          # Подключаемся к localhost (через туннель)
                port=tunnel.local_bind_port, # Используем локальный порт туннеля
                user=mysql_user,
                passwd=mysql_password,
                db=mysql_db,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        
        return connection
        
                
    except Exception as e:
        print(f"An error occurred: {str(e)}")