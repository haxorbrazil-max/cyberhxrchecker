import requests
from config import PLUSPIX_CLIENT_ID,PLUSPIX_CLIENT_SECRET
BASE='https://api-pluspix.squareweb.app'
HEAD={'x-client-id':PLUSPIX_CLIENT_ID,'x-client-secret':PLUSPIX_CLIENT_SECRET,'Content-Type':'application/json'}
def create_deposit(cents,description):
    r=requests.post(BASE+'/api/v1/deposit',headers=HEAD,json={'amount':cents/100,'description':description,'payerName':'Cliente','payerDocument':'00000000000'},timeout=30)
    r.raise_for_status(); return r.json()
def check_transaction(tid):
    r=requests.post(BASE+'/api/transactions/check',headers=HEAD,json={'transactionId':tid},timeout=30)
    r.raise_for_status(); return r.json()
