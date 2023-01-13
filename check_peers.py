# Скрипт для проверки пира на основе данных учетной записи
# Необходимо установить через pip модуль paramiko

# -*- coding: utf-8 -*-

import ldap
from datetime import datetime, timedelta, tzinfo
import paramiko
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Для преобразования майкрософтовского формата файла
EPOCH_AS_FILETIME = 116444736000000000  # January 1, 1970 as MS file time
HUNDREDS_OF_NANOSECONDS = 10000000


def filetime_to_dt(ft):
    """Converts a Microsoft filetime number to a Python datetime. The new
    datetime object is time zone-naive but is equivalent to tzinfo=utc.
    """
    # Get seconds and remainder in terms of Unix epoch
    (s, ns100) = divmod(ft - EPOCH_AS_FILETIME, HUNDREDS_OF_NANOSECONDS)
    # Convert to datetime object
    dt = datetime.utcfromtimestamp(s)
    # Add remainder in as microseconds. Python 3.2 requires an integer
    dt = dt.replace(microsecond=(ns100 // 10))
    dt = dt.date()
    return dt

def sendmail(text):
    msg = MIMEMultipart()
    msg['From'] = 'it@planetavto.ru'
    msg['To'] = 'bogdanovskyds@a-trast.ru'
    msg['Subject'] = 'Менеджер не подключен к телефону'
    mail_text = MIMEText(text, 'plain')
    msg.attach(mail_text)
    mailserver = smtplib.SMTP("mail.planetavto.ru", 587)
    mailserver.starttls()
    mailserver.ehlo()
    mailserver.login('it', 'Kad866044')
    mailserver.sendmail(msg['From'], msg['To'], msg.as_string())
    mailserver.quit()

# Получить почту и e-mail
def get_phone_and_logon_date_by_dn(user):
    ad = ldap.initialize("ldap://10.10.10.3")
    ad.protocol_version = ldap.VERSION3
    ad.set_option(ldap.OPT_REFERRALS, 0)
    ad.simple_bind_s("ldapsearch@pa.local", "6EqYqY2Z")
    phone = ''
    result = ad.search_s(user, ldap.SCOPE_BASE,
            '(&(objectCategory=person)(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2))(telephoneNumber=*))')
    print(result)
    if result:
        for user, attrb in result:
            if attrb['lastLogon'] and attrb['telephoneNumber']:
                phone = attrb['telephoneNumber'][0].lower().decode("utf-8")
                logon_date = int(attrb['lastLogon'][0].decode("utf-8"))
                logon_date = filetime_to_dt(logon_date)
    return phone, logon_date

def salers_search():
    ad_filter = '(&(objectClass=GROUP)(cn=Менеджеры))'
    ad = ldap.initialize("ldap://10.10.10.3")
    ad.protocol_version = ldap.VERSION3
    ad.set_option(ldap.OPT_REFERRALS, 0)
    ad.simple_bind_s("ldapsearch@pa.local", "6EqYqY2Z")
    attrlist = ["member"]
    basedn = "OU=pa.local,DC=pa,DC=local"
    result = ad.search_s(basedn, ldap.SCOPE_SUBTREE, ad_filter, attrlist)
    phone_logon = []
    if result:
        if len(result[0]) >= 2 and "member" in result[0][1]:
            members = result[0][1]["member"]
            for user in members:
                attrs = get_phone_and_logon_date_by_dn(user.decode("utf-8"))
                phone_logon.append(attrs)

    return phone_logon

userlist = salers_search()

def check_in_asterisk (userlist):
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('pbx.pa.local', username='root', password='Cd12345678#')
    number_not_present = ["222", "223"]
    for record in userlist:
#        print(record)
        if record[1] == datetime.now().date():
            command = "asterisk -x 'sip show peers' | grep -m 1 " + record[0] + " | awk '{print $8}'"
            _stdin, _stdout, _stderr = client.exec_command(command)
            output = _stdout.read().decode("utf-8")
            print(record[0], output)
            if output != "OK\n":
                number_not_present.append(record[0])
    if number_not_present:
#        print("Result: ", number_not_present)
        sendmail("Менеджеры с номерами:\n" + '\n'.join(number_not_present) +
                 "\n" + "сидят без связи!")


check_in_asterisk(userlist)
