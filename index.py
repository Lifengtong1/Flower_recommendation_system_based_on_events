#!/Users/bin/python
# -*- coding: utf-8 -*-

html = '''Content-type: text/html;


<html>
<head>
  <meta http-equiv="Content-Type" content="text/html" charset="UTF-8" />
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" crossorigin="anonymous">
  <title>花レコメンド</title>
</head>
<body>
<nav class="navbar navbar-light bg-light">
  <div class="container-fluid">
    <a class="navbar-brand" href="#">
      出来事による花レコメンド
    </a>
  </div>
</nav>

<form action="test.py" method="post" enctype="multipart/form-data">
<div class="container-sm">
  <p class="p1">出来事を選択してください</p>
  <select class="form-select" name="event">
    <option value="お見舞い">お見舞い</option>
    <option value="母の日">母の日</option>
    <option value="父の日">父の日</option>
    <option value="敬老の日">敬老の日</option>
  </select>
  <div class="bt">
  <input class="btn btn-outline-primary" type="submit"　value="Submit"/>
  </div>
  <p>お勧め花ランキング</p>
  <p>%s</p>
</div>
</form>

</body>
<style>
  form {
    padding-top: 20px;
  }
  .bt {
    padding-top: 10px;
    padding-bottom: 10px;
  }
</style>
</html>
'''

import cgi
import os, sys
import numpy as np
import pandas as pd
from PIL import Image
# ライブラリのインポート
import psycopg2

try:
    import msvcrt
    msvcrt.setmode(0, os.O_BINARY)
    msvcrt.setmode(1, os.O_BINARY)
except ImportError:
    pass

f = cgi.FieldStorage()
x = f.getfirst('event', '')
# データベースとの接続
conn = psycopg2.connect("host=localhost port=5432 dbname=### user=### postgres=### password=###")
key=conn.cursor()
key.execute("select red, yellow, pink, white, purple, spring, summer, autumn, winter, fragrance, moms_love, love, thanks, respect, dedication, friendly, hope, longevity from keyword where words = '{}'".format(x))
keys = key.fetchall()

flower=conn.cursor()
flower.execute("select name, red, yellow, pink, white, purple, spring, summer, autumn, winter, fragrance, moms_love, love, thanks, respect, dedication, friendly, hope, longevity from flower")
flowers = flower.fetchall()

key.close()
flower.close()
conn.close()

qvec = np.array([])
fs = np.array([])
# 類似度計算
def comp_sim(qvec,tvec):
    return np.dot(qvec, tvec) / (np.linalg.norm(qvec) * np.linalg.norm(tvec))

# 花の読み込み
for i in range(int(len(flowers))):
  fs=np.append(fs,flowers[i])
fs=fs.reshape([11,19])
fs=pd.DataFrame(fs)
   

# keyword
if 'event' in f:
  for i in range(int(len(keys[0]))):
    qvec=np.append(qvec, float(keys[0][i]))
else:
  print(html % '')

names = fs[0]
key_s = fs.iloc[:, 1:]
key_s = key_s.loc[:, 1:].astype('float')

result=np.array([])
for i in range(key_s.index.shape[0]):
    result = np.append(result, comp_sim(qvec, key_s.iloc[i,:].to_numpy()))
rank = np.argsort(result)
arr = []
for index in rank[:-rank.shape[0]-1:-1]:
    arr.append([names[index], result[index]])
content = pd.DataFrame(arr)
content.columns=['花','類似度']

print(html % content.to_html(classes=["table", "table-bordered", "table-hover"], escape=False))
