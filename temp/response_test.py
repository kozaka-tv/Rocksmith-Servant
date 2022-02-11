import encodings

import requests

response = requests.get('http://192.168.178.48:9938/')

print("Call to: http://192.168.178.48:9938/")
print("response: " + str(response))
print("encoding: " + response.encoding)
print("headers: " + str(response.headers))
response_json = response.json()
print("response in json: " + str(response_json))

string = response.decode('utf-8')
json_obj = response_json.loads(string)

# print("---")
# print(json_obj)
# print(json_obj.encoding)
