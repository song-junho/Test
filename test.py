
import pandas as pd
import FinanceDataReader as fdr
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import requests

krx_df = fdr.StockListing("KRX")


def MakeAlarmData(stock_code):
    
    url = 'https://finance.daum.net/api/trader/histories?page=1&perPage=30&symbolCode=A{}&pagination=true'
    real_url = url.format(stock_code)

    headers = {
                'Referer': 'http://finance.daum.net',
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 OPR/58.0.3135.127'
    }
    response = requests.get(real_url, headers=headers)
    jsonObjs = response.json()
    dataList = jsonObjs['data']

    foreignTrader  = dataList[0]["foreignTrader"]["netSales"]
    domesticTrader = dataList[0]["domesticTrader"]["netSales"]  
    
    return foreignTrader, domesticTrader
    



API_TOKEN = '1139815049:AAHZTGRbViIkADeagV-KTvX7wX91T2O4zf4'

NameList_df = pd.read_excel(r"C:\Users\송준호\Desktop\SendTradeAlarm\NameList.xlsx", sheet_name = 'Sheet1')

name_list = list(NameList_df["Name"])
id_list   = list(NameList_df["ChatId"])

today_date = date.today()

for num in range(0, len(NameList_df)):
    
    name    = name_list[num]
    chat_id = id_list[num]
    print(name)
    print(chat_id)

    stock_list = []
    make_df = pd.DataFrame(index = [0], columns = ["StockCode", "ForeignTrader", "DomesticTrader", "AlarmDate"])
    
    file_name = "StockList_" + name + ".xlsx"
    stock_list_df = pd.read_excel(r"C:\Users\송준호\Desktop\SendTradeAlarm\\" + file_name, sheet_name = 'Sheet1') 
    
    for stock_code in stock_list_df["StockCode"]:
        stock_list.append(stock_code[1:])
        
    print(stock_list)
    
    for n in range(0, len(stock_list)):
        stock_code = stock_list[n]
        foreignTrader, domesticTrader = MakeAlarmData(stock_code)
        make_df.loc[n] = [stock_code, foreignTrader, domesticTrader, 0]
        
    ##비교(알람)
    file_name = "StockPrice_" + name + ".xlsx"
    stock_price_df = pd.read_excel(r"C:\Users\송준호\Desktop\SendTradeAlarm\\" + file_name, sheet_name = 'Sheet1') 

    
    for i in range(0 , len(stock_price_df)):
        
        StockName = krx_df[krx_df["Symbol"] == make_df["StockCode"][i]]["Name"].values[0]
        send_text = StockName + ", 외국인 순매수량: " + " " + str(make_df["ForeignTrader"][i]) + ", 기관 순매수량: " + str(make_df["DomesticTrader"][i])
        send_text = "%s" % send_text

        url_tmpl = "https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={send_text}"
        url =  url_tmpl.format(token=API_TOKEN, chat_id=chat_id, send_text=send_text)
        r = requests.get(url)

        print(send_text)

        make_df["AlarmDate"][i] = today_date
            
        make_df.to_excel(r"C:\Users\송준호\Desktop\SendTradeAlarm\\" + file_name)


make_df
