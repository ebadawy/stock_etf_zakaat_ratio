import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import json
import yfinance as yf

def fetch_etf_holdings_with_weights(etf: str):
    url = "https://www.zacks.com/funds/etf/{}/holding"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0"
    }
    response = requests.get(url, headers=headers)
    rslt = []
    with requests.Session() as req:
        req.headers.update(headers)
        r = req.get(url.format(etf))
        print(f"Extracting: {r.url}")
        goal = re.findall(r'etf\\\/(.*?)\\/.*?\\/.*?', r.text)
        holdings = json.loads(r.text.split("etf_holdings.formatted_data")[1].split("</script>")[0].split(";")[0][3:])
        holdings[0]
        for holding in holdings:
            ticker_symbol = re.findall(r'rel="([A-Z]+)"', holding[1])
            if not ticker_symbol: continue
            ticker_symbol = ticker_symbol[0]
            weight = float(holding[3])
            rslt.append([ticker_symbol,weight])
    return rslt
    
def is_etf(ticker):
    return yf.Ticker(ticker).info["quoteType"] == "ETF"
  
def zakaatable_ratio_stock(ticker_symbol, cache):
    if ticker_symbol in cache: return cache[ticker_symbol]
    ticker = yf.Ticker(ticker_symbol)
    last_date = str(ticker.balance_sheet.keys()[0]).split(" ")[0]
    ratio = ticker.balance_sheet[last_date]["Current Assets"]/ticker.balance_sheet[last_date]["Total Assets"]
    cache[ticker_symbol] = ratio
    return ratio

def zakaatable_ratio_etf(ticker_symbol,cache):
    if ticker_symbol in cache: return cache[ticker_symbol]
    holdings = fetch_etf_holdings_with_weights(ticker_symbol)
    total_weighted_ratio = 0
    for symbol, weight in holdings:
        total_weighted_ratio += zakaatable_ratio_stock(symbol,cache) * weight
    cache[ticker_symbol] = total_weighted_ratio / sum(weight for _, weight in holdings)
    return cache[ticker_symbol]
    
def zakaatable_ratio(ticker_symbol: str,cache) -> float:
    if ticker_symbol in cache: return cache[ticker_symbol]
    if is_etf(ticker_symbol):
        return zakaatable_ratio_etf(ticker_symbol,cache)
    return zakaatable_ratio_stock(ticker_symbol,cache)
    
# example
cache = {}
portfolio = ["VGT","AAPL"]
for holding in portfolio:
  print(holding, zakaatable_ratio(holding,cache))
