'''import jsonlines
import json

keys = {}
dict_list = []

with jsonlines.open('D:\hackUiowaSqlite\yelp_academic_dataset_tip.json') as reader:
    for obj in reader:
        dict_list.append(obj)

with open('Tips.json', mode = 'w', encoding = 'utf-8') as f:
    json.dump(dict_list, f)'''

import pandas as pd
import json
import sqlite3
#import sqlite
# Open JSON data
with open("D:\hackUiowaSqlite\Business.json", encoding='utf-8') as f:
    data = json.load(f)

'''for element in data:
    for key in element:
        element[key] = str(element[key])'''
# Create A DataFrame From the JSON Data
df = pd.DataFrame(data)

df.to_csv('Business.csv')

'''conn = sqlite3.connect("Yelp.db")
c = conn.cursor()
df.to_sql("Tips",conn)'''