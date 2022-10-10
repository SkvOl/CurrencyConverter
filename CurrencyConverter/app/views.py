from django.shortcuts import render
from django.http import HttpRequest
from django.http import JsonResponse
from datetime import date, timedelta, datetime
import requests
import json

def home(request):
    headers = {
                "apikey": "FTN2LmEsdv2A5Ja3Gkop4cfu5ux2eooD",
             }

    if request.method == "POST":
        val_in = request.POST.get('val_in')
        print(val_in)
       
        val_out = int(val_in) * 5  if val_in != "" else 0 



        return JsonResponse(
            {
                'val_out' : val_out,
            }, 
            safe=False
        )

    else:
        #вычисляем ip пользователя
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        #вычисляем ip пользователя

        ip = '103.250.73.178' #проверка поиска на примере Японского IP
        #вычисляем вычисляем где он живёт и находим валюту в его стране
        if ip == '127.0.0.1':
            _from = 'RUB'
        
        else:
            country = requests.get(url=f'http://ip-api.com/json/{ip}').json().get('country')

            _from = 'EUR'

            with open("app/country.json", "r") as f1:
                array_country = json.load(f1)

            for key, value in array_country.items():
                if value.find(country) != -1:
                    _from = key
                    break
        

        _to = 'RUB'
        #вычисляем вычисляем где он живёт и находим валюту в его стране
        val_out = 1

        url = f"https://api.apilayer.com/currency_data/convert?to={_from}&from={_to}&amount={val_out}"
        val_in = requests.request("GET", url, headers = headers, data = {}).json()['result']
        print(val_in)

        d_now = datetime.now()
        array_date = {}#{d_now.strftime("%Y-%m-%d") : 0}
        print(array_date)
        for i in range(30):
            d_current = (d_now - timedelta(i)).strftime("%Y-%m-%d")
            url = f"https://api.apilayer.com/currency_data/historical?date={d_current}"
            history = requests.request("GET", url, headers = headers, data = d_current).json()['quotes']
            array_date[d_current] = int(history['USD'+_from]/history['USD'+_to])

        return render(
            request,
            'app/lower_flexbox.html',
            {
                'from_curr' : _from,
                'to_curr' : _to,
                'country' : array_country.keys(), 
                'val_in' : val_in,
                'val_out' : val_out,
            },
        )
