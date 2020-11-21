import requests

URL = 'https://team1-fydp.azurewebsites.net/result'
data = {"device_id": "Prototype 1 ESP32",
        "ds18b20_reservoir_temp": 24.6875,
        "ds18b20_plant_temp": 25.46875,
        "dht22_plant_hum": 67.5,
        "ds18b20_root_temp": 24.28125,
        "dht22_root_hum": 99.90001,
        "dht22_plant_temp": 24.95,
        "dht22_root_temp": 24.55,
        "time_sent": "(2020, 7, 8, 2, 18, 35, 34, 2094)"
        }

def test_put():
    r = requests.put(URL, data=data)
    assert r.status_code == 201

def test_get():
    r = requests.get(URL + '/1')
    assert r.status_code == 200
