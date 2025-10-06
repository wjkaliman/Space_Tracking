import requests

username = 'wjkaliman@gmail.com'
password = 'Canon2025Ball2026'

url = 'https://www.space-track.org/basicspacedata/query/class/tle_latest/NORAD_CAT_ID/25544/format/tle'

response = requests.get(url, auth=(username, password))

print(response.text if response.ok else f"Error: {response.status_code}")

session = requests.Session()

login_url = 'https://www.space-track.org/ajaxauth/login'
login_data = {'identity': username, 'password': password}

session.post(login_url, data=login_data)

# Now use the session to make authenticated requests
tle_url = 'https://www.space-track.org/basicspacedata/query/class/tle_latest/NORAD_CAT_ID/25544/format/tle'
response = session.get(tle_url)

print(response.text if response.ok else f"Error: {response.status_code}")