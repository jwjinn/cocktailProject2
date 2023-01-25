import json
# https://gem1n1.tistory.com/2

with open('/home/joo/hadoopLocation/test.json', 'r') as f:
    k = json.load(f)

print(k)
# [{'email': 'email1', 'hadoop': 'location1'}, {'email': 'email2', 'hadoop': 'location2'}]

print(k[0]['email'])
# 0번째의 email키