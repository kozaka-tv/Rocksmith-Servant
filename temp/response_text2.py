from urllib.request import urlopen
import json

# Get the dataset
url = 'http://192.168.178.48:9938/'
response = urlopen(url)

# Convert bytes to string type and string type to dict
string = response.read().decode('utf-8')
json_obj = json.loads(string)

print("response: " + str(response))
print("headers: " + str(response.headers))
print("response in json: " + str(json_obj))

# print(json_obj['album_name']) # prints the string with 'source_name' key