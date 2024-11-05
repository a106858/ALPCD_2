import requests

url = "https://api.itjobs.pt/job/list.json?api_key=09ad1042ebaf1704533805cd2fab64f1"

payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

#aaaa