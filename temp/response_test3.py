#!/usr/bin/env python3
import json
from urllib.request import urlopen

with urlopen('http://192.168.178.48:9938/') as response:
    result = json.loads(response.read().decode(response.headers.get_content_charset('utf-8')))

print(result['songDetails']['songName'])
