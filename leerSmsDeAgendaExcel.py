# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 10:06:17 2022

@author: Cristian

"""
from decouple import config

import pymysql
from datetime import datetime
import openpyxl
import requests
import json
from math import ceil

class Model:

    def __init__(self):
        self.connection = pymysql.connect(
            host=config('MYSQL_HOST'),
            user=config('MYSQL_USER'),
            password=config('MYSQL_PASSWORD'),
            db=config('MYSQL_DB')
        )

        self.cursor = self.connection.cursor()
        print('coneccion estableciada correctamente')

    def select_all_campaign_agenda_excel_model(self):
        # pendiente 2 y agendado 4 el status de cada campaña
        sql = 'SELECT * FROM campaigns where (campaign_type_id = 2 || campaign_type_id = 3) and service_id = 1 and (status = 2 || status = 4) order by scheduled asc '
        # sql = 'SELECT * FROM campaigns where id=9'
        try:
            self.cursor.execute(sql)
            campaigns = self.cursor.fetchone()
            return campaigns
        except Exception as e:
            print(e)
            raise

    def select_all_contact_by_agenda_model(self, id):
        sql = 'SELECT * FROM contacts WHERE agenda_id = {} '.format(id)
        try:
            self.cursor.execute(sql)
            campaigns = self.cursor.fetchall()
            return campaigns
        except Exception as e:
            print(e)
            raise

    def select_sms_campaign_by_id(self, id):
        sql = 'SELECT * FROM sms_campaigns WHERE campaign_id = {} '.format(id)
        try:
            self.cursor.execute(sql)
            campaigns = self.cursor.fetchone()
            return campaigns
        except Exception as e:
            print(e)
            raise

    def crear_sms(self, payload):
        sql = "INSERT INTO sms (credit, send_at,route_send, is_push, content, phone, status, comment, response, payload ,user_id, campaign_id, channel_id,created_at,updated_at) VALUES ({},'{}','{}',{},'{}','{}','{}','{}','{}','{}',{},{},{},'{}','{}')".format(
            payload['credit'], payload['send_at'], payload['route_send'], payload['is_push'], payload['content'], payload['phone'], payload['status'], payload['comment'], payload['response'], payload['payload'],payload['user_id'], payload['campaign_id'], payload['channel_id'],payload['created_at'], payload['updated_at'])
        try:
            self.cursor.execute(sql)
            self.connection.commit()
            print('se creo sms')
            return True
        except Exception as e:
            print(e)
            return False

    def select_excel_sms_by_id (self,id):
        sql = 'SELECT * FROM excel_sms_campaigns WHERE campaign_id = {} '.format(id)
        try:
            self.cursor.execute(sql)
            excel_sms_campaigns = self.cursor.fetchone()
            return excel_sms_campaigns
        except Exception as e:
            print(e)
            raise

    def change_state_campaign(self, campaign_id, status):
        sql = "UPDATE campaigns SET status = {} where id = {}".format(
            status, campaign_id)
        try:
            self.cursor.execute(sql)
            self.connection.commit()
            print('se modificao el status de la campaña ' + "{}".format(status))
            return True
        except Exception as e:
            print(e)
            return False

    def select_user(self, user_id):
        sql = "SELECT * FROM users where id ={} ".format(user_id)
        try:
            self.cursor.execute(sql)
            user = self.cursor.fetchone()
            return user
        except Exception as e:
            print(e)
            return False

    def create_url(self, data):
        print('crear url')
        sql = "INSERT INTO `urls`(`name`, `short_url`, `long_url`, `user_id`, `group_url_id`, `url_id`, `status`, `state`, `created_at`, `updated_at`) VALUES ('{}','{}','{}',{},{},'{}',{},{},'{}','{}')".format(data['name'],data['short_url'],data['long_url'],data['user_id'],data['group_url_id'],data['url_id'],data['status'],data['state'],data['created_at'],data['updated_at'],)
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except Exception as e:
            print(e)
            return False

    def select_group_url(self, campaign_id):
        sql = "SELECT * FROM group_urls where campaign_id = {} ".format(campaign_id)
        try:
            self.cursor.execute(sql)
            group_url = self.cursor.fetchone()
            return group_url
        except Exception as e:
            print(e)
            return False

    def select_channel_by_id(self, channel_id):
        sql = "SELECT * FROM channels where id = {} ".format(channel_id)
        try:
            self.cursor.execute(sql)
            channel = self.cursor.fetchone()
            return channel
        except Exception as e:
            print(e)
            return False

    def select_provider_by_id(self, provider_id):
        sql = "SELECT * FROM providers where id = {} ".format(provider_id)
        try:
            self.cursor.execute(sql)
            provider = self.cursor.fetchone()
            return provider
        except Exception as e:
            print(e)
            return False

    def close(self):
        self.connection.close()


class Controller(object):
    is_scheduled2 = True

    def __init__(selft):
        selft.model = Model()
        selft.view = View()

    def send_sms_by_agenda(self, campaign, contacts_by_agenda, sms_campaign):
        #id del usuario campaign[5]
        user = self.model.select_user(campaign[5])

        key_contacts = [
            {
                "key": "[NOMBRE 1]",
                "value": 2,
            },
            {
                "key": "[NOMBRE 2]",
                "value": 3,
            },
            {
                "key": "[APELLIDO 1]",
                "value": 5,
            },
            {
                "key": "[APELLIDO 2]",
                "value": 6,
            },
            {
                "key": "[EMAIL]",
                "value": 4,
            },
            {
                "key": "[VAR1]",
                "value": 7,
            },
            {
                "key": "[VAR2]",
                "value": 8,
            },
            {
                "key": "[VAR3]",
                "value": 9,
            },
            {
                "key": "[VAR4]",
                "value": 10,
            },
        ]

        for contact in contacts_by_agenda:
            auxiliar = sms_campaign[2]
            for clave in key_contacts:
                if(clave['key'] in auxiliar and contact[clave['value']] != None) :
                    auxiliar = auxiliar.replace(clave['key'], contact[clave['value']])  
                else:
                    auxiliar=auxiliar.replace(clave['key'], "")
            # usar url individual
            auxiliar=  self.has_individual_url(sms_campaign,campaign,auxiliar)

            auxiliar = self.standardize_message(auxiliar)

            credit = self.calculate_credits(auxiliar)
            
            # seleccionar el proveedor
            response = self.select_provider(user[8],auxiliar)

            # mandar la informacion para crear el sms
            result = self.send_sms(credit,sms_campaign,auxiliar,contact[1], 1 , response, campaign,user)
            print('///////////////////////////////////')


        print(contact[0])
    
    def send_sms(self,credit, sms_campaign, auxiliar, phone,phone_status, response ,campaign,user):
        print('se envio sms')
        payload = {
                    'credit': credit,
                    "send_at":  datetime.now(),
                    "route_send": "",
                    "is_push": sms_campaign[3],
                    "content": auxiliar,
                    "phone": phone,
                    "status": phone_status,
                    "comment": "",
                    "response": response[1],
                    "payload": str(response[0]),
                    "user_id": campaign[5],
                    "campaign_id": sms_campaign[7],
                    "channel_id": user[8],
                    "created_at": datetime.now(),
                    "updated_at":datetime.now()
                }
        sms = self.model.crear_sms(payload)
        return sms
# ****************************************************************************************************************************************************
    def read_excel(self, path, sms_campaign, campaign):

        user = self.model.select_user(campaign[5])

        # leer el archivo opcion 1
        key_contacts = [
            {
                "key": "[VAR1]",
                "value": 2,
            },
            {
                "key": "[VAR2]",
                "value": 3,
            },
            {
                "key": "[VAR3]",
                "value": 4,
            },
            {
                "key": "[VAR4]",
                "value": 5,
            },
            {
                "key": "[VAR5]",
                "value": 6,
            },
            {
                "key": "[VAR6]",
                "value": 7,
            },
            {
                "key": "[VAR7]",
                "value": 8,
            },
            {
                "key": "[VAR8]",
                "value": 9,
            }
        ]

        print('excel ***********')
        # print(path)
        book = openpyxl.load_workbook(path, data_only=True)
        sheet_name = book[config('NAME_OF_ACTIVE_SHEET')]
        row_count = sheet_name.max_row
        print("###########")

        for i in range(1,row_count):
            auxiliar = sms_campaign[2]
            print(auxiliar)
            for clave in key_contacts:
                if sheet_name.cell(row=i+1,column=1).value !=None:
                    phone=(sheet_name.cell(row=i+1,column=1).value)
                    print(phone)

                if(clave['key'] in auxiliar and sheet_name.cell(row=i+1,column=clave['value']).value != None ):
                    auxiliar = auxiliar.replace(clave['key'],str(sheet_name.cell(row=i+1,column=clave['value']).value))
                else:
                    auxiliar=auxiliar.replace(clave['key'], "")

            if sheet_name.cell(row=i+1,column=1).value !=None:
                
                #Crear url individual
                auxiliar=  self.has_individual_url(sms_campaign,campaign,auxiliar)

                auxiliar = self.standardize_message(auxiliar)

                phone_status = self.validate_phone(phone)

                credit = self.calculate_credits(auxiliar)

                # seleccionar el proveedor
                # if(phone_status == 1 ):
                response = self.select_provider(user[8],auxiliar)

                #Mandar datos para crear sms
                result = self.send_sms(credit,sms_campaign,auxiliar,phone, phone_status ,response, campaign,user)

                print("cccccccccccccccccccccccccccccccccccccc")

        
    def create_cut_url(self, long_url):
        data =   json.dumps({ 'url_register' : [ { 'original_url' : long_url }] })
        response = requests.post(config('ENDPOINT_CUT_PE'),data=data, auth=(config('USER_CUT_PE'),config('PASSWORD_CUT_PE')))
        dataJson = response.json()
        
        print(dataJson['shortUrl'])
        print(dataJson['cut_url_id'])
        return dataJson
    
    def calculate_credits(self, message):
        print('calcular mensage')
        # data =   { 'message' : message }
        # # response = requests.post('localhost:8000/api/calculatecredits',data=data)
        # response = requests.post(config('ENDPOINT_CALCULATE_CREDITS'),data=data)
        # # response = requests.post('http://localhost/enviamas9_production/public/web-api/provider',data=data)
        # dataJson = response.json()
        # if (dataJson['success']):
        #     print(dataJson['data'])
        #     print(dataJson['data']['messages'])
        #     return dataJson['data']['messages']
        # else :
        #     return 0
        n=0
        m=0
        for f in message:
            if  message[n]== '|' or message[n]== '{' or message[n]== '}' or message[n]== '[' or message[n]== ']':
                m = m + 1
            n = n + 1
            m = m + 1

        if m <= 160:
            per_message = 160
        else:
            per_message = 153
        credit = int(ceil(m / float(per_message)))
        return credit


    def standardize_message(self, message):
        print('mensaje estandarizado')
        message=message.replace("'", "")
        message=message.replace("ñ", "n")
        message=message.replace("Ñ", "N")
        message=message.replace("á", "a")
        message=message.replace("Á", "A")
        message=message.replace("é", "e")
        message=message.replace("É", "E")
        message=message.replace("í", "i")
        message=message.replace("Í", "I")
        message=message.replace("ó", "o")
        message=message.replace("Ó", "O")
        message=message.replace("ú", "u")
        message=message.replace("Ú", "U")
        return message

    def validate_phone(self, phone):
        print('celular valido')
        if( len(str(phone)) == 9  and type(phone) == int):
            print('Numero valido')
            return 1
        print(type(phone))
        print( len(str(phone)))
        return 0

    def has_individual_url(self,sms_campaign,campaign, auxiliar):
        if( sms_campaign[4] == None and sms_campaign[5]!=None and ('[CUSTOM_URL]' in auxiliar)):
            print('tiene link corto')
            group_url = self.model.select_group_url(campaign[0])
            url = self.create_cut_url(sms_campaign[5])
            auxiliar = auxiliar.replace( '[CUSTOM_URL]', url['shortUrl'] )

            payload_url = {
                'name':'url individual',
                'short_url':url['shortUrl'],
                'long_url':sms_campaign[5],
                "user_id": campaign[5],
                'group_url_id':group_url[0],
                'url_id':url['cut_url_id'],
                'status':False,
                'state':True,
                'created_at':datetime.now(),
                'updated_at':datetime.now(),
            }
            new_url = self.model.create_url(payload_url)

        return auxiliar

    def select_provider(self,channel_id, auxiliar):
        print('channel_id')
        
        channel = self.model.select_channel_by_id(channel_id)
        provider = self.model.select_provider_by_id(channel[10])
        if( provider[0] == 1 ):

            payload =   {
                "dataCoding": "GSM8",
                "apiKey": channel[4],
                "country": "PE",
                "dial": channel[5],
                "message": auxiliar,
                "msisdns": "GSM8 {}",
                "tag": "GSM8",
                "msgClass": "GSM8 {}"
            }

            headers = {
                'Content-Type': "application/json",
                'Authorization': str(channel[6]),
                'cache-control': "no-cache"
                }

            response = requests.post(config('ENDPOINT_SIMULADOR'),headers=headers,data=payload)
            dataJson = response.json()
            data_text = response.text

            return json.dumps(payload), data_text, dataJson['mailingId']

        else:
            payload =   {
                "dataCoding": "SADS8",
                "apiKey": channel[4],
                "country": "PE",
                "dial": channel[5],
                "message": auxiliar,
                "msisdns": "GSrr {}",
                "tag": "Gassa",
                "msgClass": "Gasas8 {}"
            }

            headers = {
                'Content-Type': "application/json",
                'Authorization': str(channel[6]),
                'cache-control': "no-cache"
                }

            response = requests.post(config('ENDPOINT_SIMULADOR'),headers=headers,data=payload)
            dataJson = response.json()
            data_text = response.text

            return json.dumps(payload), data_text, dataJson['mailingId']



    def process_campaign(self):
        
        campaign = self.model.select_all_campaign_agenda_excel_model()
        # for campaign in campaigns:
        if(campaign != None): 
            # print(campaign[0])
            sms_campaign = self.model.select_sms_campaign_by_id( campaign[0])

            is_scheduled = True if campaign[3] != None else False
            # is_excel = True if campaign[6] == 3 else False

            if(is_scheduled):
                print(campaign[3])
                is_data_more_than_today = True if datetime.strptime("{}".format(campaign[3]), '%Y-%m-%d %H:%M:%S') > datetime.now() else False

            if(is_scheduled == False or is_data_more_than_today == True):
                is_excel = True if campaign[6] == 3 else False
                # sms_campaign = self.model.select_sms_campaign_by_id( campaign[0])

                #TODO: CAMBIAR EL STATUS DE CAMPAÑA A PROCESANDO 3
                self.model.change_state_campaign(campaign[0], 3)

                if(is_excel):
                    print('leer rows y guardarlos en una variable')
                    excel_sms_campaign = self.model.select_excel_sms_by_id(campaign[0])
                    # self.read_excel(r"C:\xampp\htdocs\enviamas9_production\public/storage/ExcelCampaing/Hola.xlsx", sms_campaign,campaign)
                    self.read_excel(config('PUBLIC_PATH') + excel_sms_campaign[1], sms_campaign,campaign)

                else:
                    print('traer contactos de agendas y guardarlos en variable')
                    contacts_by_agenda = self.model.select_all_contact_by_agenda_model(campaign[4])
                    sms_campaign = self.model.select_sms_campaign_by_id( campaign[0])
                    self.send_sms_by_agenda( campaign, contacts_by_agenda, sms_campaign)

            else:
                print("Esta agendado pero la echa programada ya paso")

            print('****************** -- for')
            # TODO: CAMBIAR EL ESTADO DE LA CAMPANA
            self.model.change_state_campaign(campaign[0], 1)

            return self.view.list_campaign(campaign)





# enviarlos datos a la vista
class View(object):

    def list_campaign(self, campaign):
        print(campaign)
        print('ver')


# El main
controlador = Controller()
controlador.process_campaign()






