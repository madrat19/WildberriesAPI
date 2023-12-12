import requests
import time
import random
import urllib
import json


# Делает GET запрос, отлавливая ошибки и неправильные коды ответа
# В случае неудачи ждет несколько секунд и пробует снова до 4 раз 
def resumable_request(url, auth={}, data={}, headers={}, params={}, right_code=200):
    MAX_RETRIES = 4
    RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
    status_code = 0
    error = None
    retry = 0
    while status_code != right_code:
        try:
            responce = requests.get(url, auth=auth, data=data, headers=headers, params=params)

            status_code = responce.status_code
            if status_code == right_code:
                return responce
            else:
                print("The request failed with an unexpected code: %s" % status_code)

        except urllib.error.HTTPError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (
                    e.resp.status,
                    e.content,
                )
            else:
                raise

        except Exception as e:

            error = "A retriable error occurred: %s" % type(e).__name__

        if error is not None or status_code != right_code:
            if error is not None:
                print(error)
            retry += 1
            if retry > MAX_RETRIES:
                return False

            max_sleep = 2**retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)

# Получает список заказов 
def get_orders(token, dateFrom):
    url='https://statistics-api.wildberries.ru/api/v1/supplier/orders'
    headers = {"Authorization": token}
    response = resumable_request(url=url, headers=headers, params={'dateFrom': dateFrom}, right_code=200)
    return response

# Тестовый код:
#    получает список заказов с 2023-11-01 и сохраняет его в файл orders.json 
if __name__ == '__main__':
    import keys
    token = keys.token

    responce = get_orders(token=token, dateFrom='2023-11-01')
    if responce == False:
        print('REQUEST FAILED!')
    else:
        with open('orders.json', "w") as f:
            json.dump(responce.json(), f)