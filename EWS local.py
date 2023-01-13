from exchangelib import Credentials, Account, DELEGATE, Configuration
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter

credentials = Credentials('bgd@test.loc', 'Kahmohs0')
config = Configuration(server='mx.test.loc', credentials=credentials)
account: Account = Account(primary_smtp_address='bgd@test.loc', config=config, credentials=credentials, autodiscover=False, access_type=DELEGATE)
print(account.sent.tree())
for item in account.inbox.all().order_by('-datetime_received'):
    print(item.subject, item.sender, item.datetime_received)

#print(account.root.tree())
print(account.root)
#print(project)
#for x in account.walk():
#    print(x)