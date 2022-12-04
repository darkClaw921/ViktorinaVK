import vk_api
import time
import pymysql
import traceback
from vk_api import keyboard
#import xlsxwriter 
import gspread

#from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
from termcolor import colored
from contextlib import closing
from threading import Thread
from localDataBase import sql


from pymysql.cursors import DictCursor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard 
from vk_api.utils import get_random_id
from loguru import logger
from vk_api import VkApi

vk_session = vk_api.VkApi(token = 'd79bb92ae7185ad6713ebfee080c53cb0aed9f497f7ef56ffc60a632546798aff4f03f22e74527b7afc36') # отдел
longpoll = VkLongPoll(vk_session, 90)
vk = vk_session.get_api()

#scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive'] # что то для чего-то нужно Костыль
#creds = ServiceAccountCredentials.from_json_keyfile_name("/Users/igorgerasimov/Desktop/Мусор/KGTAprojects-3bfc7b7d22f4.json", scope) # Секретынй файл json для доступа к API
# client = gspread.authorize(creds)
# sheet = client.open('intelCasino').sheet1 # Имя таблицы

# idUsers = ['147155440', '189217218', '105431859', '170735090'] 
# idUsers = ['105431859'] 
def connectionDB():
    connect = sql

    #pymysql.connect(
    #    host='31.31.198.58',
    #    user='u1280100_default',
    #    password='Ndif!!l6@1998',
    #    database='u1280100_quiz',
    #    cursorclass=DictCursor,
    #)
    return connect

connect = connectionDB()
cursor = connect.cursor()

ID_MESSAGES = []
usersId = []
adminId = []
PAYLOAD = 'TEXT'
COUNT_PEOPLES = 0
IS_REGISTER = True

def commit_DB_standUP(user_id: int, message: str, payload='REG'):
    global cursor, connect
    try: 
        userInfo = vk.users.get(user_ids=user_id, fields=['first_name', 'last_name'])
        name1 = userInfo[0]['first_name'] +'_'+ userInfo[0]['last_name']
        
        
        query = f"""INSERT into questions (id_user, name, command, payload) VALUES ("{user_id}", "{name1}", "{message}", "{payload}")"""
        cursor.execute(query)#(user_id, name, message, payload))
        connect.commit()
        print('Запись данных...  ', colored('[OK]', 'green'))

    except Exception as err:
        print('Запись данных...  ', colored('[Fail]', 'red'), traceback.format_exc())


    try: 
        query = f"""UPDATE standUP SET voice='{message}' WHERE id_user={user_id}"""
        cursor.execute(query)
        connect.commit()
        print('Редактирование данных...  ', colored('[OK]', 'green'))

    except Exception as err:
        print('Редактирование данных...  ', colored('[Fail]', 'red'))

@logger.catch
def commit_DB_question(user_id: int, message: str, payload: str):
    try:
        with closing(connectionDB()) as connect:
            with connect.cursor() as cursor:
                query = f"""UPDATE questions SET {payload}="{message}" WHERE id_user={user_id}"""
                cursor.execute(query)
                connect.commit()
                print('Запись данных...  ', colored('[OK]', 'green'))
    except Exception as err:
        print('Обновление данных...  ', colored('[Fail]', 'red'), traceback.format_exc())

def get_last_payload(user_id) -> str:
    try: 
        with closing(connectionDB()) as connect:
            with connect.cursor() as cursor:
                query = 'SELECT payload FROM questions WHERE id_user=%s ORDER BY `id` DESC LIMIT 1'
                cursor.execute(query,(user_id))
                cursor = list(cursor)
                print('Полоучение последних данных...  ', colored('[OK]', 'green'))
                return cursor[0]['payload']

    except Exception as err:
        print('Полоучение последних данных...  ', colored('[Fail]', 'red'), traceback.format_exc())
        return 'FAIL'

def keyboardCreater(*args, count: int): 
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button(args[0])
    args[1:]
    
    for label in args[1:]:
        
        keyboard.add_line()
        keyboard.add_button(label)
        
    keyboard = keyboard.get_keyboard()
    return keyboard

@logger.catch
def isHE(id_user):
    global cursor 
    """
    try:
        with closing(connectionDB()) as connect:
            with connect.cursor() as cursor:
                query = f'SELECT COUNT(*) as count FROM questions WHERE id_user={id_user}'
                cursor.execute(query)
                if list(cursor)[0]['count'] > 0:
                    return True
                else:
                    return False
    except Exception as e:
        print('Ошибка: ',e) 
"""
    #iconn = connectionDB()
    #cursor = conn.cursor()
    query = f'SELECT COUNT(*) as count FROM questions WHERE id_user={id_user}'
    
    try:
        cur = cursor.execute(query)
        print(list(cur))
    
        if list(cur)[0]['count'] > 0:
            cur.close()
            return True
        else:
            cur.close()
            return False
    
    except:
        return False
        cur.close()
 
# KEYBOARD = keyboardCreater(*PEOPLES, count=2)
# keyboardAdmin = keyboardCreater(f'Начать прием ответов на {get_count_tyr()} тур', f'Закончить прием ответов на {get_count_tyr()} тур' ,'Начать регистрацию', 'Закончить регистрацию', 'Результаты', count=6)


vk.messages.send(
    user_id='105431859',
    random_id=get_random_id(),
    message = "админ [online]",
    # keyboard= keyboardAdmin,
    )

while True:
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                # lastPayload = get_last_payload(event.user_id)
                text = event.text.lower()
                # print(text)
                if text == 'a':
                    if isHE(event.user_id):
                        vk.messages.send(
                            user_id=event.user_id,
                            random_id=get_random_id(),
                            message='Вы уже начали/закончили проходить викторину',
                        ) 
                        continue   
                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message='Поехали',
                    )
                    PAYLOAD = 'payload'
                    # commit_DB_question(event.user_id, 'REG', 'payload')
                    commit_DB_standUP(event.user_id, event.text)
            
                if isHE(event.user_id):
                    lastPayload = get_last_payload(event.user_id)
                    if lastPayload == 'REG':
                        vk.messages.send(
                            user_id=event.user_id,
                            random_id=get_random_id(),
                            # attachment='photo-194390511_457239189',
                            message = "Повар спрашивает повара… Ой, о чем это я… Привет, меня зовут Семён, и я бот-студент. Сегодня наш с тобой праздник - День российского студенчества. И я бы очень хотел задать тебе пару вопросов, чтобы проверить твои знания. Ну что, приступим? \n Готов?"
                            # keyboard = keyboardCreater('Меч','Циркуль','Ракета','Танк', count=4),
                        )
                        commit_DB_question(event.user_id, 'question1', 'payload')
                    
                    if lastPayload == "question1":
                        commit_DB_question(event.user_id, event.text, 'question1')
                        vk.messages.send(
                            user_id=event.user_id,
                            random_id=get_random_id(),
                            message = "Начнем с простого: как зовут ректора нашей академии?",
                            # keyboard = keyboardCreater('9','12','4','3', count=4),
                        )
                        commit_DB_question(event.user_id, 'question2', 'payload')

                    if lastPayload == "question2":
                        commit_DB_question(event.user_id, event.text, 'question2')
                        vk.messages.send(
                            user_id=event.user_id,
                            random_id=get_random_id(),
                            message = "Ну это было легко, а ты попробуй скажи кто был первым ректором нашей академии? ",
                            # keyboard = keyboardCreater('9','12','4','3', count=4),
                        )
                        commit_DB_question(event.user_id, 'question3', 'payload')

                    if lastPayload == "question3":
                        commit_DB_question(event.user_id, event.text, 'question3')
                        vk.messages.send(
                            user_id=event.user_id,
                            random_id=get_random_id(),
                            message = "Ну хватит про академию. Сегодня, 25 января, в день российского студенчества отмечает день рождения ВУЗ, занимающий 74 место в мировом рейтинге ВУЗов. Как же он называется?",
                            # keyboard = keyboardCreater('9','12','4','3', count=4),
                        )
                        commit_DB_question(event.user_id, 'question4', 'payload')

                    if lastPayload == "question4":
                        commit_DB_question(event.user_id, event.text, 'question4')
                        vk.messages.send(
                            user_id=event.user_id,
                            random_id=get_random_id(),
                            message = "Сколько факультетов в КГТА?",
                            # keyboard = keyboardCreater('9','12','4','3', count=4),
                        )
                        commit_DB_question(event.user_id, 'question5', 'payload')
                    
                    if lastPayload == "question5":
                        commit_DB_question(event.user_id, event.text, 'question5')
                        vk.messages.send(
                            user_id=event.user_id,
                            random_id=get_random_id(),
                            message = "Правильный ответ 8, а может и нет, я же бот, я не умею считать, а мы переходим дальше. \n\n Как известно, настоящий доктор не откажет в помощи всем нуждающимся, даже если страждущие ни о чём таком не просили, да и вообще если это не люди. Наверное, примерно такими соображениями руководствуются московские студенты медики, когда после выпускного отправляются бинтовать… кого?",
                            # keyboard = keyboardCreater('9','12','4','3', count=4),
                        )
                        commit_DB_question(event.user_id, 'question7', 'payload')

                    
                    if lastPayload == "question7":
                        commit_DB_question(event.user_id, event.text, 'question7')
                        vk.messages.send(
                            user_id=event.user_id,
                            random_id=get_random_id(),
                            message = "Как-то я опять разошелся… давай снова упростим задачу. \n 1+1+1+1+1+1+1+1*0+1",
                            # keyboard = keyboardCreater('9','12','4','3', count=4),
                        )
                        commit_DB_question(event.user_id, 'question9', 'payload')

                    
                    if lastPayload == "question9":
                        commit_DB_question(event.user_id, event.text, 'question9')
                        vk.messages.send(
                            user_id=event.user_id,
                            random_id=get_random_id(),
                            attachment='photo-194390511_457239191',
                            message = " Cамый важный вопрос во всей нашей викторине. Кто это?",
                            # keyboard = keyboardCreater('9','12','4','3', count=4),
                        )
                        commit_DB_question(event.user_id, 'question10', 'payload')

                    if lastPayload == "question10":
                        commit_DB_question(event.user_id, event.text, 'question10')
                        vk.messages.send(
                            user_id=event.user_id,
                            random_id=get_random_id(),
                            message = "Для тех, кто не знал, я специально написал – это Герасимов Игорь. Мой создатель, поэтому если я плохо работаю – виноват он. \n Ну и последний наш сегодняшний вопрос. \n\n Я уверен, каждый слышал гимн нашей любимой академии, а знаете ли вы сколько в нём строк? ",
                            # keyboard = keyboardCreater('9','12','4','3', count=4),
                        )    
                        commit_DB_question(event.user_id, 'question11', 'payload')
                    
                    if lastPayload == "question11": 
                        commit_DB_question(event.user_id, event.text, 'question11')
                        vk.messages.send(
                            user_id=event.user_id,
                            random_id=get_random_id(),
                            message = "На сегодня все =)",
                            # keyboard = keyboardCreater('9','12','4','3', count=4),
                        )    
                        commit_DB_question(event.user_id, 'question12', 'payload')    
                else:
                #    Если человека нет

                    continue


            # commit_DB_queue(event.user_id, event.text, PAYLOAD)
    except Exception as e:
        print(e, traceback.print_exc())
        vk.messages.send(
            user_id='105431859',
            random_id=get_random_id(),
            message = "админ [offline]",
            # keyboard= keyboardAdmin,
            )
        vk.messages.send(
            user_id='105431859',
            random_id=get_random_id(),
            message = (e, traceback.print_exc()),
            # keyboard= keyboardAdmin,
            )
        
        continue



