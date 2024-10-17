import requests

url = "https://digital-twin.expangea.com/rack/5BTG/3/10/"

payload = {}
headers = {
  'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
