# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 11:04:43 2022

@author: Cristian
"""

import pymysql



class DataBase:
    def __init__(self):
        self.connection  = pymysql.connect(
            host = 'localhost',
            user='root',
            password='',
            db='enviamas9'
        )
        
        self.cursor = self.connection.cursor()
        print('coneccion estableciada correctamente')
        
    def select_user(self, id):
        sql = 'SELECT * FROM users where id= {}'.format(id)
        try:
            self.cursor.execute(sql)
            user = self.cursor.fetchone()
            print('Id:',user[2])
            print('Id:',user[0])
        except Exception as e:
            print(e)
            raise
            
    def select_all_user(self):
        sql = 'SELECT * FROM users'
        try:
            self.cursor.execute(sql)
            users = self.cursor.fetchall()
            for user in users:
            
                print('Id:',user[2])
                print('Id:',user[0])
                print('____________\n')
                
        except Exception as e:
            print(e)
            raise

    def update_user(self, id, username):
        sql = 'UPDATE users SET username = {} where id = {}'.format(username, id)
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except Exception as e:
            print(e)
            raise
    
    def crear_sms(self, payload):
        sql = "INSERT INTO sms (credit, send_at,route_send, is_push, content, phone, status, comment, response, payload ,user_id, campaign_id, channel_id) VALUES ({},'{}','{}',{},'{}','{}','{}','{}','{}','{}',{},{},{})".format(
            payload['credit'], payload['send_at'], payload['route_send'], payload['is_push'], payload['content'], payload['phone'], payload['status'], payload['comment'], payload['response'], payload['payload'],payload['user_id'], payload['campaign_id'], payload['channel_id'])
        try:
            self.cursor.execute(sql)
            self.connection.commit()
            print('se creo sms')
            return True
        except Exception as e:
            print(e)
            return False

    def close(self):
        self.connection.close()

database = DataBase()
# database.select_user(1)
# database.select_all_user(1)

payload = {
                'credit': 100,
                "send_at": "as",
                "route_send": "as",
                "is_push": True,
                "content": "auxiliar",
                "phone": "contact[1]",
                "status": 0,
                "comment": "as",
                "response": "response[1]",
                "payload": "str(response[0])",
                "user_id": 1 ,
                "campaign_id": 1 ,
                "channel_id": 1, #user[8] = channel_id
            }

database.crear_sms(payload)


database.close()

