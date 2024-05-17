#!/usr/bin/env python3
# -*- coding: cp1251 -*-
import sys
import requests

url = 'https://yandexform.ru/amo/recognize/note_rec.php'
foo = sys.argv[1]
result = sys.argv[2]

files = {
    'number': (None, foo),
    'text': (None, result)
}

response = requests.post(url_amo, files=files)

