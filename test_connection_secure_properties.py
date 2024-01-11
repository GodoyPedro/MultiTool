import http.client
import mimetypes
from codecs import encode

# conn = http.client.HTTPSConnection("secure-properties-api.us-e1.cloudhub.io")
dataList = []
boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'

json_data = {'operation': 'encrypt',
'algorithm': 'Blowfish',
'mode': 'CBC',
'key': 'b3rg3Mul3s@ft!',
'value': 'hola',
'method': 'string'}

for key, data in json_data.items():
    dataList.append(encode('--' + boundary))
    dataList.append(encode(f'Content-Disposition: form-data; name={key};'))
    dataList.append(encode('Content-Type: {}'.format('text/plain')))
    dataList.append(encode(''))
    dataList.append(encode(data))

dataList.append(encode('--'+boundary+'--'))
dataList.append(encode(''))
print(dataList)
body = b'\r\n'.join(dataList)
print(body)
payload = body
headers = {
  'Accept': '*/*',
  'Accept-Language': 'es-419,es;q=0.9',
  'Connection': 'keep-alive',
  'Origin': 'https://secure-properties-api.us-e1.cloudhub.io',
  'Referer': 'https://secure-properties-api.us-e1.cloudhub.io/',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'Content-type': 'multipart/form-data; boundary={}'.format(boundary)
}
# conn.request("POST", "/api/string", payload, headers)
# res = conn.getresponse()
# data = res.read()
# print(data.decode("utf-8"))



import requests

files=[

]

url = "https://secure-properties-api.us-e1.cloudhub.io/api/string"

response = requests.request("POST", url, headers=headers, data=payload, files=files)

print(response.text)
