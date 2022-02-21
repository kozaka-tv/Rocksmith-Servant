import json
from urllib.request import urlopen
import requests

rs_playlist_url = "https://rsplaylist.com/ajax/playlist.php?channel=kozaka"
cookies = {'PHPSESSID': '4hsjtoq26pvtavh062jdsplfp8'}

r = requests.get(rs_playlist_url, cookies=cookies)
r_json = r.json()

# Get the dataset
# url = 'https://firebasestorage.googleapis.com/v0/b/kozaka-tv.appspot.com/o/rspl_example.json?alt=media&token=fafe71bd-90cb-4613-986a-94439612d219'
response = urlopen(url)

# Convert bytes to string type and string type to dict
read = response.read()
string = read.decode('utf-8')
json_obj = json.loads(string)

print(json_obj['playlist'])  # prints the string with 'source_name' key
