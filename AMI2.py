import telnetlib
import time
import json
import re

##
HOST = "10.10.11.101"
PORT = "5038"
user = "test"
password = "Cd12345678_er"
##

tn = telnetlib.Telnet(HOST,PORT)
tn.write("Action: login".encode('ascii') + b"\n")
username = "Username: " + user
tn.write(username.encode('ascii') + b"\n")
passWord = "Secret: " + password
string_NOW = ''
string_out = ''

tn.write(passWord.encode('ascii') + b"\n\n")


def telnet_for_string(string):
    for mes in string:
        print(string[mes])

while True:
    # time.sleep(0.1)
    string = ''
    event_string = ''
    elements_string = ''
    c = 0

    read_some = tn.read_some()

    string = read_some.decode('utf8', 'replace').replace('\r\n', '#')
    # print(string)

    if not string.endswith('##'):
        string_NOW = string_NOW + string


    if string.endswith('##'):
        string_NOW = string_NOW + string
        string_NOW = string_NOW.replace('##', '$')
        string_NOW = string_NOW.replace('\n', '#')
        string_NOW = string_NOW.replace('\r', '#')
        string_NOW = string_NOW.replace('"', '')
        string_NOW = string_NOW.replace('\\', '')


        events = re.findall(r'[A-Z][\w]+:\s[^$]+', string_NOW)
        for event in events:
            c+=1

            event_elements = re.findall(r'[A-Z][\w]+:\s[^#]+', event)
            for element in event_elements:
                element = '\"' + element.replace(': ', '\": "') + '\", '
                elements_string = elements_string + element

            event_string = event_string + '\"' + str(c) + '\": ' + '{' + elements_string + '}'

            event_string = event_string.replace('}{', '},{')
            event_string = event_string.replace(', }', '}, ')
        event_string = '{' + event_string + '}'
        event_string = event_string.replace('}, }', '}}')
        try:
            parsed_string = json.loads(event_string)
        except json.decoder.JSONDecodeError:
            print('#############################################', '\n\n\n')
            print(event_string, '\n\n\n')
            print(string_NOW, '\n\n\n')
            print('#############################################', '\n\n\n')


        telnet_for_string(parsed_string)
        string_NOW = ''