##########################################
# Скрипт для проверки доступности  и оперативного удаления и возврата DNS записей в Selectel.
# Предварительно следует создать БД MySQL с таблицей records со следующими полями:
# domain(varchar(45)), record(varchar(45)), ip(varchar(45)), domain_id(varchar(45))
# Так же установить через pip selectel-dns-api и PyMySQL
##########################################
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import smtplib
import os
import selectel_dns_api   # Установить через pip
import pymysql   # Установить через pip
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# Отправка извещений на почту
def sendmail(text):
    msg = MIMEMultipart()
    msg['From'] = 'it@planetavto.ru'
    msg['To'] = '300@a-trast.ru'
    msg['Subject'] = 'Изменения в DNS'
    mail_text = MIMEText(text, 'plain')
    msg.attach(mail_text)
    mailserver = smtplib.SMTP("mail.planetavto.ru", 587)
    mailserver.starttls()
    mailserver.ehlo()
    mailserver.login('it', 'Kad866044')
    mailserver.sendmail(msg['From'], msg['To'], msg.as_string())
    mailserver.quit()

# Функция пинга по доменному имени. -w - время ожидания ответа от сервера
def ping_test(host):
    response = os.system("ping -w 500 -n 2 " + host)
    if response == 0:
        return True
    else:
        return False
# Коннект к базе данных (Установить свои значения)
con = pymysql.connect(host='localhost', user='root', password='Kahmohs0', database='dns')

# Коннект к Selectel API
selectel_dns_api.configuration.api_key['X-Token'] = 'i2Ey2D6tAdkscxE0WAwkHvIRy_204719'
domain_api_instance = selectel_dns_api.DomainsApi()
domain_body = selectel_dns_api.Domain.name
domains = domain_api_instance.get_domains()
domain_dict = {}

# Получаем список доменов в селектеле
for domain in domains:
    domain_dict[domain.id] = domain.name
# Переменная для поработу через API
api_records = selectel_dns_api.RecordsApi()

# Проверка записей в Selectel
def check_in_selectel():
    records_list = [] # Список А-записей
# В цикле проходим по всем доменам и добавляем в список все записи
    for item in domain_dict.items():
        get_records = api_records.get_resource_records_by_domain_id(item[0])
        api_del_record = selectel_dns_api.RecordsApi()
# Проход по списку записей с проверкой доступности по ip. Если запись недоступна - добавляем в базу и удаляем в selectel
        for record in get_records:
            if record.type == "A":
                if ping_test(record.content) is False:
                    cur = con.cursor()
                    cur.execute('INSERT into records (domain, domain_id, record, ip) VALUES (%s, %s, %s, %s)',
                                (item[1], item[0], record.name, record.content))
                    api_del_record.delete_resource_record(item[0], record.id)
                    records_list.append(record.name)
# Отправка письма с оповещением об удалении записи
                    sendmail(("Удалены записи " + ', '.join(records_list)))
                    con.commit()

# Проверка доступности записей, удаленных из Selectel и добавленных в базу данных
def check_in_database():
# Извлекаем в список записи из базы
    cur = con.cursor()
    cur.execute('SELECT domain, record, ip FROM records')
    result = cur.fetchall()
    records_list = []
# Для каждой записи из базы получаем список записей Selectel
    for record in result:
        selectel_records = api_records.get_resource_records_by_domain_name(record[0])
        selectel_tuples = []
# И сравниваем с каждой записью из этого списка
        for each in selectel_records:
            selectel_tuples.append((record[0], each.name, each.content))
# Если совпадений нет, а запись из базы доступна по ip - добавляем ее в Selectel и удаляем из базы
        if record not in selectel_tuples:
            if ping_test(record[2]) is True:
                api_instance = selectel_dns_api.RecordsApi()
                body = selectel_dns_api.NewOrUpdatedRecord(name=record[1], type='A', ttl=60, content=record[2])
                api_instance.add_resource_record(body, record[0])
                cur.execute('Delete from records where domain = %s AND record = %s and ip = %s', (record[0], record[1], record[2]))
                con.commit()
                records_list.append(record[1])
# Отправка письма с оповещением о возвраате записи
                selectel_records.append(record[1])
                sendmail(("Добавлены записи: " + ', '.join(records_list)))

# Вызов функций проверки
check_in_selectel()
check_in_database()
