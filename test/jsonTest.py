import json
from collections import OrderedDict

# 파일 읽기

dict = {'email': 'email1',
        'hadoop': 'location1'}

# with open('/home/joo/hadoopLocation/test.json', 'w') as f:
#     json.dump(dict, f)

# # print(dict)
#
#
# with open('/home/joo/hadoopLocation/test.json') as f:
#     d_update = json.load(f, object_pairs_hook = OrderedDict)
#
# print(d_update)
#
# # dict = {'email': 'email2',
# #         'hadoop': 'location2'}
#
# d_update['email'] = 'email2'
# d_update['hadoop'] = 'location2'
#
#
# print(d_update)

"""
json_dict = { 'category': 'food', 'name': 'mcdonalds', 'price': '1000' }

# add an element to the existing list
row= { 'category': 'food', 'name': 'lotteria', 'price': '1500' }
json_dict = [json_dict, row]

# result
print(json_dict)
"""

json_dict = {'email': 'email2', 'hadoop': 'location2'}

with open('/home/joo/hadoopLocation/test.json', 'r') as f:
     k = json.load(f)

print(k)

json_dict = [k, json_dict]

with open('/home/joo/hadoopLocation/test.json', 'w') as f:
     json.dump(json_dict, f)



