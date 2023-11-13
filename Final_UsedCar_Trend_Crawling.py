from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import matplotlib.pyplot as plt
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs


from matplotlib import rc
import platform
if platform.system() == 'Darwin': #맥
    rc('font', family='AppleGothic')
elif platform.system() == 'Windows': #윈도우
    rc('font', family='Malgun Gothic')    


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# kb차차차---------------------------------------
url = 'https://www.kbchachacha.com/public/search/main.kbc#!?_menu=buy'
driver.get(url)



# 차종 - 준중형, 중형, SUV --------------------------
chajong = driver.find_element(By.XPATH,'//*[@id="content"]/div[2]/div/div[2]/div[1]/div[2]/div/div[3]/div[1]')

#준중형
subcompact = driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div/div[2]/div[1]/div[2]/div/div[3]/div[1]/div/div[3]/span[1]')

#중형
midsize = driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div/div[2]/div[1]/div[2]/div/div[3]/div[1]/div/div[4]/span[1]')

#SUV
suv = driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div/div[2]/div[1]/div[2]/div/div[3]/div[1]/div/div[8]/span[1]')



# crawling-----------------------------------------

htmllist=[]

def crawling():
    body = driver.find_element(By.TAG_NAME,'body')
    
    for i in range(5):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)

    html = driver.page_source
    htmllist.append(html)



# extract - 차이름, 출고날짜, 주행거리, 가격------------

title = []
when = []
km = []
price = []

def extract() :
    title_raw = soup.find_all('strong', attrs = {'class': 'tit'})

    for i in title_raw :
        t =i.get_text().strip()
        title.append(t)            

    when_raw = soup.find_all('div', attrs = {'class': 'first'})
    for i in when_raw :
        w = i.get_text().strip()
        when.append(w)
    
    km_raw = soup.find_all('div', attrs = {'class': 'data-in'})
    for i in km_raw :
        k = i.get_text().strip()
        km.append(k)

    price_raw = soup.find_all('strong', attrs = {'class': 'pay'})
    for i in price_raw :
        p = i.get_text().strip()
        price.append(p)



# 국산 -------------------------------------------
korea = driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div/div[2]/div[1]/div[1]/ul/li[2]')
korea.click()


# ========================================== A. 준중형차 ==========================================

chajong.click()
subcompact.click()


# 전기
food = driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div/div[2]/div[1]/div[2]/div/div[3]/div[6]')
food.click()
elec = driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div/div[2]/div[1]/div[2]/div/div[3]/div[6]/div/div[9]/span[1]')
elec.click()

# 헛걸음보상
service = driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div/div[2]/div[1]/div[2]/div/div[3]/div[9]')
service.click()
driver.execute_script("window.scrollTo(0, 1000)")
hut_walk = driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div/div[2]/div[1]/div[2]/div/div[3]/div[9]/div/div[1]/span[1]')
hut_walk.click()

# 진단
seller = driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div/div[2]/div[1]/div[2]/div/div[3]/div[10]')
seller.click()
diagnose = driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div/div[2]/div[1]/div[2]/div/div[3]/div[10]/div/div[6]/span[1]')
diagnose.click()
 

driver.execute_script("window.scrollTo(0,0)")

time.sleep(1)

    
crawling()


# 다음페이지 있을 경우 
for i in range(2,10) :
    try :
        url = '//*[@id="content"]/div[2]/div/div[2]/div[2]/div[3]/div[5]/a[{}]'.format(i)
        ee = driver.find_element(By.XPATH, url)
        ee.click()
        crawling()
    except :
        pass



# html로 텍스트 추출
no = len(htmllist)

for i in range(no):
    soup = bs(htmllist[i], 'html.parser')

    with open("subcompact.txt", 'w', encoding='utf-8') as g:
        g.write(soup.prettify())
    
    extract()



# 데이터 프레임 만들기
df1 = pd.DataFrame({'Title' : title,
                   'When' : when,
                   'kmplace' : km,
                   'Price' : price})


# 차종 정리
df1['Title'] = df1['Title'].str.replace('	','').str.replace('\n','').str.replace('실차주','')


# 연도 날짜 정리
name_split = df1["When"].str.split(" ")
df1["Year"] = name_split.str.get(0)
df1["Month"] = name_split.str.get(1)


# km랑 거래위치 나누기
df1['kmplace'] =df1['kmplace'].str.replace('km','').str.replace(',','')
name_split = df1["kmplace"].str.split("\n")
df1["KM"] = name_split.str.get(0)
df1["Place"] = name_split.str.get(1)
df1['KM'] = pd.to_numeric(df1['KM'])


# 가격 정리
df1['Price'] = df1['Price'].str.replace('만원','').str.replace(',','')
name_split = df1["Price"].str.split(" ")
df1["Real Price"] = name_split.str.get(0)
df1['Real Price'] = pd.to_numeric(df1['Real Price'])


# 필요없는 column 제거
df1 = df1.drop(['When'], axis = 1)
df1 = df1.drop(['kmplace'], axis = 1)
df1 = df1.drop(['Price'], axis =1)


# 중복 매물 제거
df1 = df1.drop_duplicates(subset=None, keep='first', inplace=False, ignore_index=False)


# excel 저장
df1.to_excel('./subcompact.xlsx')


# 시각화

# 모델 매물 수 순위
pop1 = df1['Title'].value_counts().sort_values(ascending = True)
pop1.plot.barh(x='index', y='Title', fontsize=7, color = "#A7F58B")
plt.title('Subcompact car Model')
plt.show()


# 주행거리와 가격 간 Scatter plot
plt.scatter(df1['KM'], df1['Real Price'], alpha = 0.5, c ='#A7F58B', label ="Subcompact")
 
plt.legend(loc = "best")
plt.xlabel('KM')
plt.ylabel('Real Price')
plt.show()

'''
# Subcompact Car 가격 boxplot
df1['Real Price'].plot.box( color = "lightsalmon")
plt.title('Price of Subcompact Car')
plt.show()


# Subcompact Car 주행거리 boxplot
df1['KM'].plot.box()
plt.title('Milage of Subcompact car')
plt.show()

'''



# ========================================== B. 중형차 ==========================================
driver.execute_script("window.scrollTo(0,0)")

chajong.click()
subcompact.click()
midsize.click()

driver.execute_script("window.scrollTo(0,0)")

time.sleep(1)
   
htmllist=[]

crawling()


# 다음페이지 있을 경우
for i in range(2,10) :
    try :
        url = '//*[@id="content"]/div[2]/div/div[2]/div[2]/div[3]/div[5]/a[{}]'.format(i)
        ee = driver.find_element(By.XPATH, url)
        ee.click()
        crawling()
    except :
        pass


# html로 텍스트 추출
no = len(htmllist)
title = []
when = []
km = []
price = []

for i in range(no):
    soup = bs(htmllist[i], 'html.parser')

    with open("midsize.txt", 'w', encoding='utf-8') as g:
        g.write(soup.prettify())
    
    extract()


#데이터 프레임 만들기
df2 = pd.DataFrame({'Title' : title,
                   'When' : when,
                   'kmplace' : km,
                   'Price' : price})


# 차종 정리
df2['Title'] = df2['Title'].str.replace('	','').str.replace('\n','').str.replace('실차주','')


# 연도 날짜 정리
name_split = df2["When"].str.split(" ")
df2["Year"] = name_split.str.get(0)
df2["Month"] = name_split.str.get(1)


# km랑 거래위치 나누기
df2['kmplace'] =df2['kmplace'].str.replace('km','').str.replace(',','')
name_split = df2["kmplace"].str.split("\n")
df2["KM"] = name_split.str.get(0)
df2["Place"] = name_split.str.get(1)
df2['KM'] = pd.to_numeric(df2['KM'])


# 가격 정리
df2['Price'] = df2['Price'].str.replace('만원','').str.replace(',','')
name_split = df2["Price"].str.split(" ")
df2["Real Price"] = name_split.str.get(0)
df2['Real Price'] = pd.to_numeric(df2['Real Price'])


# 필요없는 column 제거
df2 = df2.drop(['When'], axis = 1)
df2 = df2.drop(['kmplace'], axis = 1)
df2 = df2.drop(['Price'], axis =1)


# 중복 매물 제거
df2 = df2.drop_duplicates(subset=None, keep='first', inplace=False, ignore_index=False)


# excel 저장
df2.to_excel('./midsize.xlsx')



# 시각화

# 모델 매물 수 순위
pop2 = df2['Title'].value_counts().sort_values(ascending = True)
pop2.plot.barh(x='index', y='Title', fontsize=7, color = "#9BEEF7")
plt.title('Midsize car Model')
plt.show()

#  주행거리와 가격 간 scatter plot 
plt.scatter(df2['KM'], df2['Real Price'], alpha = 0.5, c ='#9BEEF7', label ="Midsize")
 
plt.legend(loc = "best")
plt.xlabel('KM')
plt.ylabel('Real Price')
plt.show()

'''
# Midsize 가격 boxplot
df2['Real Price'].plot.box()
plt.title('Price of Midsize Car')
plt.show()

# Midsize 주행거리 boxplot
df2['KM'].plot.box()
plt.title('Milage of Midsize Car')
plt.show()

'''



# ========================================== C. SUV ==========================================
driver.execute_script("window.scrollTo(0,0)")

chajong.click()
midsize.click()
suv.click()
 
driver.execute_script("window.scrollTo(0,0)")

time.sleep(1)
    
htmllist=[]

crawling()


# 다음페이지 있을 경우
for i in range(2,10) :
    try :
        url = '//*[@id="content"]/div[2]/div/div[2]/div[2]/div[3]/div[5]/a[{}]'.format(i)
        ee = driver.find_element(By.XPATH, url)
        ee.click()
        crawling()
    except :
        pass


# html로 텍스트 추출
no = len(htmllist)
title = []
when = []
km = []
price = []

for i in range(no):
    soup = bs(htmllist[i], 'html.parser')

    with open("suv.txt", 'w', encoding='utf-8') as g:
        g.write(soup.prettify())
    
    extract()


# 데이터 프레임 만들기
df3 = pd.DataFrame({'Title' : title,
                   'When' : when,
                   'kmplace' : km,
                   'Price' : price})


# 차종 정리
df3['Title'] = df3['Title'].str.replace('	','').str.replace('\n','').str.replace('실차주','')


# 연도 날짜 정리
name_split = df3["When"].str.split(" ")
df3["Year"] = name_split.str.get(0)
df3["Month"] = name_split.str.get(1)


# km랑 거래위치 나누기
df3['kmplace'] = df3['kmplace'].str.replace('km','').str.replace(',','')
name_split = df3["kmplace"].str.split("\n")
df3["KM"] = name_split.str.get(0)
df3["Place"] = name_split.str.get(1)
df3['KM'] = pd.to_numeric(df3['KM'])


# 가격 정리
df3['Price'] = df3['Price'].str.replace('만원','').str.replace(',','')
name_split = df3["Price"].str.split(" ")
df3["Real Price"] = name_split.str.get(0)
df3['Real Price'] = pd.to_numeric(df3['Real Price'])


# 필요없는 column 제거
df3 = df3.drop(['When'], axis = 1)
df3 = df3.drop(['kmplace'], axis = 1)
df3 = df3.drop(['Price'], axis =1)


# 중복 매물 제거
df3 = df3.drop_duplicates(subset=None, keep='first', inplace=False, ignore_index=False)


# excel 저장
df3.to_excel('./SUV.xlsx')


# 시각화

# 모델 매물 수 순위
pop3 = df3['Title'].value_counts().sort_values(ascending = True)
pop3.plot.barh(x='index', y='Title', fontsize=7, color = "#CE93FF")
plt.title('SUV car Model')
plt.show()

# 주행거리와 가격 간 Scatter plot
plt.scatter(df3['KM'], df3['Real Price'], alpha = 0.5, c ='#CE93FF', label ="SUV")
 
plt.legend(loc = "best")
plt.xlabel('KM')
plt.ylabel('Real Price')
plt.show()

'''
# SUV 가격 boxplot
df3['Real Price'].plot.box()
plt.title('Price of SUV Car')
plt.show()

# SUV 주행거리 boxplot
df3['KM'].plot.box()
plt.title('Milage of SUV car')
plt.show()
'''



# ======================== 가격, 주행거리 별 boxplot ===========================

# 가격 boxplot
data1 = df1['Real Price']
data2 = df2['Real Price']
data3 = df3['Real Price']
data = [data1, data2, data3]

fig = plt.figure(figsize =(7, 10))
ax = fig.add_subplot(111)
ax = ax.boxplot(data, patch_artist = True, vert =1)
plt.xticks([1,2,3], ['Subcompact', 'Midsize', 'SUV'])
plt.title('Price')

colors = ['#A7F58B', '#9BEEF7', '#CE93FF']
for patch, color in zip( ax['boxes'], colors):
    patch.set_facecolor(color)

plt.show()


# 주행거리 boxplot
data1 = df1['KM']
data2 = df2['KM']
data3 = df3['KM']
data = [data1, data2, data3]

fig = plt.figure(figsize =(7, 10))
ax = fig.add_subplot(111)
ax = ax.boxplot(data, patch_artist = True, vert =1)
plt.xticks([1,2,3], ['Subcompact', 'Midsize', 'SUV'])
plt.title('Milage(km)')

colors = ['#A7F58B', '#9BEEF7', '#CE93FF']
for patch, color in zip( ax['boxes'], colors):
    patch.set_facecolor(color)

plt.show()