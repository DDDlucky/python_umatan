from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import requests
import datetime
from flask import Flask,request,render_template,jsonify

options = Options()
driver = webdriver.Chrome(options=options)

url = "https://search.rakuten.co.jp/search/mall/ANKER/?f=0"


def scr(url):
    driver.get(url)
    time.sleep(2)

    item_name = []
    url_list = []
    stock_flg = []

    items = driver.find_elements_by_class_name("searchresultitem")

    for item in items:
        title = item.find_element_by_class_name("title")
        item_name.append(title.text)

        url = item.find_element_by_tag_name("a").get_attribute("href")
        url_list.append(url)

        item = item.text
        item = item.split("\n")

        if "売り切れ" in item:
          stock_flg.append(1)
        else:
          stock_flg.append(0)

    df = pd.DataFrame([item_name, url_list, stock_flg]).T
    df.columns = ["item_name", "url", "stock_flg"]

    driver.quit()

    return df

def slack_Send(df):
  df = df.sort_values(by="stock_flg", ascending=False)
  df.to_csv("test.csv")

  TOKEN = "{xoxb-2175746339216-2175777305248-Rtu2ejkTJptNPvtPzhr4pG8i}"
  CHANNEL = "{C024950NXUN}"

  files = {
    "file": open("test.csv")
  }

  today = datetime.date.today()
  

  params = {
    "token": TOKEN,
    "channel": CHANNEL,
    "filename": f"rakuten_stock_{today}.csv",
    "initial_comment": f"楽天の在庫情報です。欠品率{out_of_stock_rate*100:.1f}%です。",
    "title": f"rakuten_stock_{today}.csv"
  }
  requests.post(url="https://slack.com/api/files.upload", params=params, files=files)


# def main():
#   url = "https://search.rakuten.co.jp/search/mall/ANKER/?f=0"
#   df = scr(url)
#   print(df)
#   slack_Send(df)

app = Flask(__name__)
@app.route("/")
def check():
  return render_template("index.html")

@app.route("/output", methods=["POST"])
def output():
  url = request.json["url"]
  df = scr(url)
  print(df)
  out_of_stock_rate = df.stock_flg.sum()/len(df)
  print(out_of_stock_rate)
  return_data = {
    "result": round(out_of_stock_rate*100, 1 )
  }
  return jsonify(ResultSet=return_data)

if __name__ == "__main__":
  app.run()
