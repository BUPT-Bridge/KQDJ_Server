from bs4 import BeautifulSoup  # pip install beautifulsoup4
import requests
import datetime  
import math
import re

# 假设response.text是从网页获取的HTML内容
url = "https://jtgl.beijing.gov.cn/"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'

soup = BeautifulSoup(response.text, 'html.parser')
scripts = soup.find_all('script', attrs={'type': 'text/javascript'})

# 用于存储Holiday数组的字符串
holiday_script = ""

# 查找包含Holiday数组定义的<script>标签
for script in scripts:
    if script.string and "var Holiday=new Array" in script.string:
        holiday_script = script.string
        break

# 使用正则表达式从JavaScript代码中提取日期
Holiday = re.findall(r'"(\d{4}-\d{1,2}-\d{1,2})"', holiday_script)

# 打印提取的日期列表
print(Holiday)


def getXHNumber(tDate:datetime.datetime, sDate:datetime.datetime):  
    nDayNum = tDate.weekday() + 1 
    print(nDayNum)
    if nDayNum > 5:
        return nDayNum
    nDiff = (tDate - sDate).days / (7 * 13)
    nDiff = math.floor(nDiff) % 5
    print(nDiff)
    nDayNum = 5 - nDiff + nDayNum
    if nDayNum > 5:
        nDayNum -= 5
    return nDayNum
  
def xianxing():  
    # 限行节假日数组（除去周六日）  
    # Holiday = ["2024-9-15", "2024-9-16", "2024-9-17", "2024-10-1", "2024-10-2", "2024-10-3", "2024-10-4", "2024-10-5", "2024-10-6", "2024-10-7"]  
    sStartDate = '2014-04-14'  # 开始星期，周一的日期  
    x = [None,'5和0', '1和6', '2和7', '3和8', '4和9', '不限行', '不限行']  

    vStartDate = datetime.datetime.strptime(sStartDate, "%Y-%m-%d")  
    vToday = datetime.datetime.now()  # 客户端当天时间  

    nDayNum1 = getXHNumber(vToday, vStartDate)  # 限行尾号数组值  
    vToday += datetime.timedelta(days=1)  
    nDayNum2 = getXHNumber(vToday, vStartDate)  

    # 判断今天和明天是否为节假日  
    for holiday in Holiday:  
        tddate = datetime.datetime.strptime(holiday, "%Y-%m-%d")  
        if vToday.strftime("%Y-%m-%d") == tddate.strftime("%Y-%m-%d"):  
            nDayNum1 = 6  
        if (vToday + datetime.timedelta(days=1)).strftime("%Y-%m-%d") == tddate.strftime("%Y-%m-%d"):  
            nDayNum2 = 6  
    return x[nDayNum1], x[nDayNum2]


def apple():
    today_limit, tomorrow_limit = xianxing()
    print(111)
    print("今天限行尾号:", today_limit)  # 显示当天限行尾号
    print("明天限行尾号:", tomorrow_limit)  # 显示明天限行尾号
    print(111)

apple()

