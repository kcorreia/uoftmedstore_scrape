
import numpy as np
import matplotlib.pyplot as plt
import datetime
import time
import re
import urllib
import pandas as pd

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.alert import Alert




def test():
    try:
        WebDriverWait(browser, 6).until(EC.alert_is_present(),'Timed out waiting for PA creation confirmation popup to appear.')
        alert = browser.switch_to_alert()
        alert.accept()
        print "\t\talert accepted"
    except TimeoutException:
        print "\t\tno alert"



browser = webdriver.Chrome('/Users/kcorreia/Downloads/chromedriver_2018_mac')
browser.get('https://www.uoftmedstore.com/login.sz')
browser.find_element_by_name("_name").clear()
browser.find_element_by_name('_name').send_keys('USERNAME')
browser.find_element_by_name("_passwd").clear()
browser.find_element_by_name('_passwd').send_keys('PASSWORD')
browser.find_element_by_xpath("//button[@class='ui fluid primary large submit button']").click()
#browser.find_element_by_xpath("//input[@type='submit']").click()


# get all the order numbers
browser.get('https://www.uoftmedstore.com/orders.sz?filter=all')
html_source = browser.page_source
order_list=[]
num=0
while html_source.count('show_detail2')>1:
	url='https://www.uoftmedstore.com/orders.sz?offset='+str(num)
	browser.get(url)
	html_source = browser.page_source
	orders=[x.split(')">')[0] for x in html_source.split('show_detail2(')[2:]]
	order_list=order_list+orders
	num=num+20


df=pd.read_csv('medstore_details.txt',sep='\t').fillna('')

#remove already processed orders
order_list=[order for order in order_list if int(order) not in df[0].tolist()]


# get the order details
fix=[]
for order in order_list:
	print order
	browser.get('https://www.uoftmedstore.com/receipt.sz?_id='+order)
	html_source = browser.page_source
	date=html_source.split('<div style="float: right">Order Date: ')[1].split('</div>')[0]
	soup = BeautifulSoup(html_source, 'html.parser')
	header=soup.find('thead')
	header_cells=[cell.text for cell in header.find_all('th')]
	body=soup.find('tbody')
	skus=body.find_all('tr')
	for sku in skus[:-1]:
		details=[cell.text for cell in sku.find_all('td')]
		# check if not free, such as pACYC184
		details=[int(order),date]+details
		if 'GST' in header_cells and details[-2]=='0.00':
			details=details[:-2]+details[-1:]
			df.loc[len(df)]=details
		elif details[-1] != '0.00':
			df.loc[len(df)]=details



df=df.sort_values(by=['Datetime'])

df.to_csv('medstore_details.txt',sep='\t',encoding='utf-8',index=False)






##############################

"""

# function to plot frequency of purchases, and 80:20 analysis


df3=df.groupby([2])[10].sum()
df3.sort(ascending=False)

total_cost=sum(df3)

cost=0
SKUs=df3.index.tolist()
while cost<0.8*total_cost:
	SKU=SKUs.pop(0)
	cost=cost+df3[SKU]
	df_temp=df[df[2].str.contains(SKU)]
	product=str(round(df3[SKU],2))+'. '+df_temp[4][0]+', '+df_temp[3][0]
	product=product.replace('/','-per-')
	g = df_temp.groupby(pd.TimeGrouper("M"))
	x = g.sum().index.tolist()
	y = g.sum()[10].tolist()
	ax = plt.subplot(111)
	ax.bar(x, y, width=15)
	ax.xaxis_date()
	ax.set_axisbelow(True)
	ax.xaxis.grid(color='gray', linestyle='dashed')
	ax.yaxis.grid(color='gray', linestyle='dashed')
	ax.set_title(product)
	ax.set_ylabel('CAD')
	plt.savefig(product+'.png')
	plt.clf()





total_cost=sum(df[10].tolist())

SKUs=list(set(df[2].tolist()))
output=[]
for SKU in SKUs:
	output.append((sum(df[df[2].str.contains(SKU)][10].tolist()),SKU))

output.sort(reverse=True)

for o in output:
	total,SKU=o
	print '\n\n'
	print o
	df[df[2].str.contains(SKU)]

portion=[]
portion_SKU=[]
for o in output:
	total,SKU=o
	portion.append(total)
	portion_SKU.append(SKU)
	if sum(portion)/total_cost>0.80:
		break


for SKU in portion_SKU:
	printer='\t'.join([df[df[2].str.contains(SKU)][3].tolist()[0],df[df[2].str.contains(SKU)][4].tolist()[0], str(sum(df[df[2].str.contains(SKU)][6].tolist()    )),   str(sum(df[df[2].str.contains(SKU)][10].tolist()    ))     ])
	f=open('8020-quant.txt','a')
	f.write(printer+'\n')
	f.close()

"""



