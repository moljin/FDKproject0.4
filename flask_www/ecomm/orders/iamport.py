import datetime

import requests

from flask_www.configs import config


def get_token():
    access_data = {
        'imp_key': config.IAMPORT_KEY,
        'imp_secret': config.IAMPORT_SECRET
    }
    url = "https://api.iamport.kr/users/getToken"
    req = requests.post(url, data=access_data)
    access_res = req.json()
    print('iamport.py의 get_token: access_res;;;;;;', access_res)
    if access_res['code'] == 0:
        return access_res['response']['access_token']
    else:
        return None


def payments_prepare(merchant_order_id, amount, *args, **kwargs):
    now = datetime.datetime.now()
    access_token = get_token()
    if access_token:
        access_data = {
            'merchant_uid': merchant_order_id,# + '@' + str(uuid.uuid4()) + NOW.microsecond,#
            'amount': amount
        }
        url = "https://api.iamport.kr/payments/prepare"
        print("api 통신 접속 ok::: access_data:::", access_data)
        headers = {
            'Authorization': access_token
        }
        req = requests.post(url, data=access_data, headers=headers)
        res = req.json()
        print("req.json 할당 완료 :::res = req.json()::::", res)
        if res['code'] != 0:
            raise ValueError("API 통신 오류")
    else:
        raise ValueError("토큰 오류")


def find_transaction(order_id, *args, **kwargs):
    print('def find_transaction(order_id, *args, **kwargs): order_id', order_id)
    access_token = get_token()
    print("find_transaction 시작:::access_token", access_token)
    if access_token:
        url = "https://api.iamport.kr/payments/find/"+order_id
        headers = {
            'Authorization': access_token
        }
        req = requests.post(url, headers=headers)
        print('def find_transaction:::req:::', req)
        res = req.json()
        print('def find_transaction:::res = req.json():::', res) ## 여기서 에러가 발생
        if res['code'] == 0:
            context = {
                'imp_id': res['response']['imp_uid'],
                'merchant_order_id': res['response']['merchant_uid'],
                'amount': res['response']['amount'],
                'status': res['response']['status'],
                'type': res['response']['pay_method'],
                'receipt_url': res['response']['receipt_url']
            }
            print('**********************context', context)
            return context
        else:
            ValueError("'NoneType' object is not subscriptable %%%%%")
            return None
    else:
        raise ValueError("토큰 오류")