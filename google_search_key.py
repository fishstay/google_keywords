import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
from fake_useragent import UserAgent
import time
import networkx as nx
import igviz as ig

def gSuggest(query):
	query.replace(" ", "+")
	hl="zh-TW"
	gl="tw"
	url = "http://suggestqueries.google.com/complete/search?output=firefox&q={}&hl={}&gl={}".format(query,hl,gl)
	ua = UserAgent(verify_ssl=False) 
	headers = {"user-agent": ua.chrome}

	response = requests.get(url, headers=headers, verify=True)
	results = json.loads(response.text)

	return results

def word_group(results):
	data = []
	for word in results[1]:
		k = gSuggest(word)[0]
		deep_words = gSuggest(word)[1]

		for deep_word in deep_words:
			group = [k, deep_word]
	
			data.append(group)

	return data

def get_autocomp_kws(query):
	results = gSuggest(query)
	data = word_group(results)
	return data

st.title('Google預測搜尋字串')
st.subheader('請輸入想查詢的字，並在輸入完成後點擊下方按鈕：')

keyword = st.text_input('')
if st.button('我已輸入完成'):
	data = []

	google_suggest = get_autocomp_kws(keyword)
	data = data + google_suggest

	df = pd.DataFrame(data, columns=['第一層預測字', '第二層預測字'])

	if len(df) > 0:

		G = nx.Graph()

		for i in range(len(df)):
			G.add_edge(df.iloc[i]['第一層預測字'], df.iloc[i]['第二層預測字'])

		for j in df.第一層預測字.unique():
			G.add_edge(keyword, j)

		name_dict = {}

		for node in G.nodes():
			if ((node in df.第一層預測字.tolist()) or (node == keyword)):
				name_dict[node] = node
			else: 
				name_dict[node] = ''

		nx.set_node_attributes(G, name_dict, 'name')

		fig = ig.plot(G,
					  node_label = 'name',
					  layout = 'kamada'
					 )

		st.write(fig)
		st.table(df)

	else:
		st.header('抱歉，沒有資料！')
