import smtplib
import os
import selectel_dns_api # Установить через pip
import pymysql # Установить через pip
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def sendmail(text):
    msg = MIMEMultipart()
    msg['From'] = 'it@planetavto.ru'
    msg['To'] = 'bogdanovskyds@a-trast.ru'
    msg['Subject'] = 'Изменения в DNS'
    mail_text = MIMEText(text, 'plain')
    msg.attach(mail_text)
    mailserver = smtplib.SMTP("mail.planetavto.ru", 587)
    mailserver.starttls()
    mailserver.ehlo()
    mailserver.login('it', 'Kad866044')
    mailserver.sendmail(msg['From'], msg['To'], msg.as_string())
    mailserver.quit()

sendmail("Test")