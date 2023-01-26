#!/usr/bin/python3
# coding=UTF-8
# файл списка контактов
contacts_file = '/var/www/html/internal/contacts.xml'
# корень просмотра Active Directory
import configparser  # импортируем библиотеку
import ldap
import xmltodict, json
from xml.dom import minidom
import xml.etree.cElementTree as ET

config = configparser.ConfigParser()  # создаём объекта парсера
config.read("ldap.env")  # читаем конфиг
ld=config['ldap']

scope = ld['basedn']
# фильтр для поиска учётных записей
ldapfilter = f"(&(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2))(!(useraccountcontrol:1.2.840.113556.1.4.803:=16))(mail=*) (displayName=*))"
#((objectClass=user)!(lockoutDuration=*)&(telephoneNumber=*))(!(userAccountControl:1.2.840.113556.1.4.803:=2))"
#(!(useraccountcontrol:1.2.840.113556.1.4.803:=16))"
# домен Active Directory
domain = ld['url']
# порт подключения LDAP
port = '389'
# имя пользователя и пароль для подключения к Active Directory
ldapbind = ld['user']
ldappassword = ld['password']

# -------------------------------
# ниже ничего менять не нужно
# -------------------------------
# подключение к Active Directory
ad = ldap.initialize(ld['url'])
ad.protocol_version=ldap.VERSION3
ad.set_option(ldap.OPT_REFERRALS, 0)
ad.simple_bind_s(ld['user'], ld['password'])

def clean_number(num): # очистка номер телефона от мусора, только цифры
  num = num.replace(' ', '').replace('(', '').replace(')', '').replace('-', '')
  return num

def replace_plus_7(num):
  num7 = num.replace('+7', '7')
  num8 = num.replace('+7', '8')
  return num7, num8

# получение списка пользователей
res = []
try:
    res=ad.search_s(scope, ldap.SCOPE_SUBTREE, ldapfilter, ["displayName","telephoneNumber","mobile","mail","title"])
    # формирование корня xml-документа с указанием интервала обновления
    root = ET.Element('contacts', refresh='86400')
    # заполнение списка контактов
    ADmobile,homePhone,ADnumber,ADname='','','',''
    for rec in res:
     try:
       ADname=rec[1]['displayName'][0].decode('utf-8')
       if 'telephoneNumber' in rec[1]:
#         print(rec[1]['displayName'][0].decode('utf-8'),rec[1]['telephoneNumber'][0].decode('utf-8'))

         if rec[1]['telephoneNumber'][0].decode('utf-8').find('+7') != -1 :
           num = rec[1]['telephoneNumber'][0].decode('utf-8')
           ET.SubElement(root, 'contact', name=ADname, number=clean_number(replace_plus_7(num)[0]), presence='1')
           ET.SubElement(root, 'contact', name=ADname, number=clean_number(replace_plus_7(num)[1]), presence='1')
         else:
           ADnumber=rec[1]['telephoneNumber'][0].decode('utf-8')
           ET.SubElement(root, 'contact', name=ADname, number=clean_number(ADnumber), presence='1')
       elif 'mobile' in rec[1]:
         if rec[1]['mobile'][0].decode('utf-8').find('+7') != -1 :
          numb=rec[1]['mobile'][0].decode('utf-8')
          ET.SubElement(root, 'contact', name=ADname, number=clean_number(replace_plus_7(numb)[0]), presence='1')
          ET.SubElement(root, 'contact', name=ADname, number=clean_number(replace_plus_7(numb)[1]), presence='1')
         else:
           ADnumber = rec[1]['mobile'][0].decode('utf-8')
           ET.SubElement(root, 'contact', name=ADname, number=clean_number(ADnumber), presence='1')
     except KeyError as e:
       print(ADname, "Exception: ", e, rec[1].decode('utf-8'))
     #print(ADname, ADnumber, homePhone, ADmobile)
    # сортировка и запись в файл
#    root[:] = sorted(root, key=lambda child: (child.tag,child.get('number')))
    root[:] = sorted(root, key=lambda child: (child.tag,child.get('name')), reverse=True)
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    with open(contacts_file, 'wb') as xml_file:
     xml_file.write(xmlstr.encode('utf-8'))
# обработка ошибок
except ldap.LDAPError as error_message:
    print("Ldaperror=",error_message)
ad.unbind_s()