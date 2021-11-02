import requests
import json


url = "https://hotels4.p.rapidapi.com/locations/search"

querystring = {"query": "Санкт-Петербург", "locale": "en_US"}

headers = {
    'x-rapidapi-host': "hotels4.p.rapidapi.com",
    'x-rapidapi-key': "9a96ad3166mshcb1e0c50caf0471p18b161jsnc1276688d044"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)