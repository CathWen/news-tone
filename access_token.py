import urllib, urllib3, sys
from urllib import request
from urllib.request import urlopen
import urllib.error
import ssl

# client_id 为官网获取的AK， client_secret 为官网获取的SK
host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=i1RVfu7Bazbf6zD22cbERKP0&client_secret=ccesNDkICGhj5lLkNbdvzdobnMR9pDbP'
request = request.Request(host)
request.add_header('Content-Type', 'application/json; charset=UTF-8')
context = ssl._create_unverified_context()
response = urlopen(request,context=context)
content = response.read()
if (content):
    print(content)

    # python用requests请求百度接口报“SSL: CERTIFICATE_VERIFY_FAILED” :
    # https://blog.csdn.net/XiaoPANGXia/article/details/49908889
    # context = ssl._create_unverified_context()
    # urllib.urlopen("https://no-valid-cert", context=context
