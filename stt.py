#!/usr/bin/env python3
# -*- coding: cp1251 -*-
import urllib.request
import json
import sys
import os
import psycopg2
from datetime import datetime
import requests

url_amo = 'https://yandexform.ru/amo/recognize/note_rec.php'


file=sys.argv[1]
lid = sys.argv[2]


FOLDER_ID = "default"
API = "AQVNzkfa052DgfDgk7isPgb_JMMYF2MMcxsaPJrK"
params = "&".join([
	"topic=general",
	"format=lpcm",
	"sampleRateHertz=8000",
	"lang=ru-RU"
])
try:
	with open(file, "rb") as f:
		data = f.read()
	url = urllib.request.Request("https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?%s" % params, data=data)
	url.add_header("Authorization", "Api-Key %s" % API)
	responseData = urllib.request.urlopen(url).read().decode('UTF-8')
	decodedData = json.loads(responseData)
	os.remove(file)
except FileNotFoundError:
	print("none",end="")
	sys.exit()

conn = psycopg2.connect(
    dbname="maksimsima",
    user="maksimsima",
    password="Maks1999",
    host="pg3.sweb.ru",
    port="5432"
)

cur = conn.cursor()

# ���������� lid
lid = str(lid)

# ���������� �������
cur.execute("SELECT data FROM telephone WHERE lid = %s", (lid,))
rows = cur.fetchall()
respVac = ""
# ����� �����������
for row in rows:
    respVac = row[0]

cur.close()
conn.close()

def write_to_json(id, text, rec):
    text = text + ' ' + rec
    data = {
        "������": id,
        "����": text,
        "�����": str(datetime.now())
    }

    try:
        with open("/tmp/backup.json", "r") as file:
            file_data = json.load(file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        file_data = []

    found = False
    for item in file_data:
        if item["������"] == id:
            if isinstance(item["����"], str):
                item["����"] = [item["����"]]  # ����������� ������ � ������
            item["����"].append(text)
            found = True

    if not found:
        file_data.insert(0, data)

    with open("/tmp/backup.json", "w") as file:
        json.dump(file_data, file, indent=4, ensure_ascii=False)

def count_matches(sentence, lists,respVac):
	matches = {}

	for list_name, word_list in lists.items():
            matches[list_name] = sum(sentence.lower().count(word.lower()) if idx <= len(sentence.split()) // 1 else 2 * sentence.lower().count(word.lower()) for idx, word in enumerate(word_list))

	max_matches = max(matches.values())
	
	max_list = max(matches, key=matches.get)
	if sentence == "":
		return("void")

	elif max_matches == 0:
		return("none")

	if max_list == "detail" and respVac.lower().find('����') != -1:
		return("gruz")
	elif max_list == "detail" and respVac.lower().find('��') != -1:
		return("eda")
	elif max_list == "detail" and respVac.lower().find('�����') != -1:
		return("taxi")
	elif max_list == "detail" and respVac.lower().find('����') != -1:
		return("avto")

	if max_list == "vacancy" and respVac.lower().find('����') != -1:
		return("gruzv")
	elif max_list == "vacancy" and respVac.lower().find('��') != -1:
		return("edav")
	elif max_list == "vacancy" and respVac.lower().find('�����') != -1:
		return("taxi")
	elif max_list == "vacancy" and respVac.lower().find('����') != -1:
		return("avtov")

	if max_matches != 0:
		return(max_list)

if decodedData.get("error_code") is None:
	resp=decodedData.get("result")
	files = {
    		'number': (None, lid),
    		'text': (None, resp)
	}
	response = requests.post(url_amo, files=files)
else:
	print("none")
lists = {
    
    "autocall": ['������������ ��� ���� ������','������c�','�������','����','��������','���������','����������','����������','�������','������','���������' , '�����','������', '�������������','������������','���������','�������','�� ��������','�� ����� ������' ,'��������','������','��������','��������','���������'],

    "podrabotka": ["��� ����������"," � ��������� �����","���� ��� ���������� �������","��� �������"],
    "fixcar": ["������ ���������", "�����", "������ ���������", "�����","�����"],
    "pogoda": ["������", "�������", "������ ������", "���������", "���� �������"],
    "sick": ["�����", "�������", "����������", "������������", "������","�����","�������","�����"],
    "cheap": ["�����","���������","������ �������"],
    "malo": ["������ �����", "���� ���", '��� �������','���� �������',"��� ������","�����","��� �������"],

    "park": ['��� �� �������', '�������','����','����� ����','��������','���������'],
    "vacancy": ['�� ������ �������','�������', '���������','��� �� �������','����� ��������','��� �� ����������','������ �������'],
    "company": ['��� ���','�������', '����', '���������','����', '������','�����','����� ��������','��� �� ��������','��� �� �������'],
    "late": ['��������� �����','�����','�� ������','�����','�����','�����','� �����','���� ���','�����','���� ����� �����',"��������� ������","�� ��������","�������� �����","�� ����",'���� � �� ����� �����'],
    "cash": ['�����','�����','��������','����','�������','����','������'],
    "taxes": ['����� �������� �����','�����','��������', '����� � ���', '� ������ �����','�������','�������','����� ������','������� ����','�� ���������� ����'],
    "wallet": ['����������', '�������'],
    "app": ['��� �� ����������', '��������','����� ����������'],
    "city": ['�����','����', '�����', '�����','�����','�����','������','�������','����','��������','���� � ������','������','����������'],
    "salary": ['�����','�� ���', '� ���', '����','�� �����','�������','����','�������','�������','�����','�����','�� ������','���������'],
    "gsm": ['�����','���', '��������', '����������','���������','������','������','�������','��'],
    "transport": ['���� ������ ����','�� ����� ����','�����������', '���������', '�����','���','����','�����','������ ���','��������','�� ����� ����','�� ����� ��������'],
    "time": ['����������','������','���������','������', '����', '�����','������','����� ������','�� ��������','�� ������','����������','���','�������� ������','����������'],
    "tomorrow": ['�����������', '������','�������','�����','��� �� �����','����','�����','��������','��� ��������'],
    "office": ['��� ��� ����','����� ���','��� ��� �����','����', '����','���������','����� � ���� ���������','����','�������','������','��� ���������','�������'],
    "hour": ['�� ���� �������������', '�����','�� ���� �������������','��� ���������������','����������', '�����','�����','�����','��������','�������� ��������','�����������','�������� ������','�������','�������','�� �����','�� ����'],
    "autoyear": ['��� ������� ������','��� �������','����','��������','� ���� ������', '���� �������','���� ��������','������ ����','������ ����� ��������','�� ������ ����','����','200','19'],
    "num": ['����','������ �', '������ ��','�� ��������','������','�������','������','�����','����� ��������','������','�������','�����������','������','��������','���� ��������','����� ��������'],
    "uzbek": ['������������ �����','�������','���������', '�����','������','�����','������','�����','���� � ����','�������','�����','���������','������'],
    "small": ['� ��� �������',' �� �������'],
    "work": ['��� �� �����������','��� �� ������', '����� ������', '������','�������','����� ���','����������'],
    "yandex": ['�� ���� �������','������', '��� ������','������ ������'],

    "detail": ['����� ','��������','��� � ��� ���','��������','�������� ����','��������','��������','��� ��� ������','������','������','�������','����������', '���������', '�����������', '��� ������','�����','�����������','����','�����','�������','����'],
    "official": ['���������', '����������','�� ����������','������ ���','��������','����������� ���������������'],
    "order": ['�������', '�����','����','������� ������� � ����','� ����','� �����','��������','�����'],
    "eda": ['���', '���', '���','������ ���','�����','������'],
    "taxi": ['�����', '���������', '�������','�����','�������'],
    "avto": ['����������', '����������', '����������','�����','�������','������','������'],
    "gruz": ['������', '����', '�������� ����', '���������', '�����','���������'],
    "yes_q": ['���','��', '����','��������'],
    "allo": ['���', '����','������� ����','����� ������','���������'],
    "yes": ['���������� � ������','���������','���������','������','��� ������','��� �������','��� �������', '��������','�����','�������','�� ���������','�� ���������','�� ����������','�����������','����������'],
    "no_q": ['������� ������','���������','������','��� ����','�� �� ���','�����','����','�������','���', '��� ��������', '���','��������','���','�������','������','�� ����','�������','�������','�����������'],
    "no": ['�����','�� ���� ������','���������','� �� ����������','������','��������','�� �������','�� ��������','�����','���','�� �� ���','��� �������','�� ���������','��� �� ���������','��� �� ��������','��������','�����','��������','�� ����������'],
    "age": ['���������', '������','�����','�� ������','� ���������','������� � ��������','13 ���','16 ���','14 ���','15 ���','17 ���','�� ������� ���'] 

}
words = resp.split()  # ��������� ������ �� �����
unique_words = []
for word in words:
    if word not in unique_words:
        unique_words.append(word)

resp = ' '.join(unique_words)  # ���������� ����� ������� � ������
result = count_matches(resp, lists,respVac)
write_to_json(lid, resp,result)
print(result,end="")