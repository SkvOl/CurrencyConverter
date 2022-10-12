from django.shortcuts import render
from django.http import HttpRequest
from django.http import JsonResponse
import plotly.graph_objects as go
from datetime import timedelta, datetime
from .forms import input_value
import requests
import json

def create_graph(headers, _to, _from, date_start, date_end):

    url = f"https://api.apilayer.com/currency_data/timeframe?start_date={date_start}&end_date={date_end.strftime('%Y-%m-%d')}&currencies={_to}&source={_from}"
    timeframe = requests.request("GET", url, headers = headers, data = {}).json()['quotes']
        
    x = timeframe.keys()
    y = [] 
    for item in timeframe.values():
        y.append(item[_from + _to])

    fig = go.Figure([go.Scatter(x = tuple(x), y = tuple(y))])
    fig.update_layout(autosize=False, width=1600, height=700)
    fig.write_html("static/app/content/graph.html")

def home(request):
    headers = {
                "apikey": "lrNtlKpIAVhJ6JrHHhPltV6AjUX6ozmj",
              }

    if request.method == "POST":
        val_in = request.POST.get('val_in')
        _from = request.POST.get('from_curr')
        _to = request.POST.get('to_curr')

        if _from != _to:
            url = f"https://api.apilayer.com/currency_data/convert?to={_to}&from={_from}&amount={val_in}"
            val_out = requests.request("GET", url, headers = headers, data = {}).json()
            print(val_out)
            print(val_out['result'])

            date_end = datetime.now()
            date_start = (date_end - timedelta(30)).strftime("%Y-%m-%d")
        
            create_graph(headers, _to, _from, date_start, date_end)

            return JsonResponse(
                {
                    'val_out' : val_out['result'],
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
        print(f"ip: {ip}")
        #ip = '103.250.73.178' #проверка поиска на примере Японского IP
        #ip = '144.123.46.90' #проверка поиска на примере Китайского IP (не работает)
        #ip = '94.181.131.229'
        
        #вычисляем вычисляем где он живёт и находим валюту в его стране
        with open("app/country.json", "r") as f1:
                array_country = json.load(f1)

        if ip == '127.0.0.1':
            _from = 'RUB'
        
        else:
            country = requests.get(url=f'http://ip-api.com/json/{ip}').json().get('country')

            _from = 'EUR'
            
            for key, value in array_country.items():
                if value.find(country) != -1:
                    _from = key
                    break
        

        if _from == 'RUB':
            _to = 'USD'
        else:
           _to = 'RUB'

        #вычисляем вычисляем где он живёт и находим валюту в его стране
        val_out = 1;

        url = f"https://api.apilayer.com/currency_data/convert?to={_from}&from={_to}&amount={val_out}"
        val_in = requests.request("GET", url, headers = headers, data = {}).json()['result']


        date_end = datetime.now()
        date_start = (date_end - timedelta(30)).strftime("%Y-%m-%d")
        
        create_graph(headers, _to, _from, date_start, date_end)
        form = input_value()
        return render(
            request,
            'app/lower_flexbox.html',
            {
                'from_curr' : _from,
                'to_curr' : _to,
                'country' : array_country.keys(), 
                'val_in' : val_in,
                'val_out' : val_out,
                'form' : form,
            },
        )
