import requests, json
ip = requests.get("https://api.ipify.org?format=text").text
print("当前出口 IP：", ip)
