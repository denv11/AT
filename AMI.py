import os
import time


from asterisk.ami import AMIClient

def event_notification(source, event):
    os.system('notify-send "%s" "%s"' % (event.name, str(event)))


client = AMIClient(address='10.10.11.101', port=5038)
future = client.login(username='test', secret='Cd12345678_er')
if future.response.is_error():
    raise Exception(str(future.response))
os.system("chcp 65001")
client.add_event_listener(event_notification)

try:
    while True:
        time.sleep(10)
except (KeyboardInterrupt, SystemExit):
    client.logoff()