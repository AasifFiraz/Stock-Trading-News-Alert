import requests
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

STOCK = "NFLX"
COMPANY_NAME = "Facebook"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
MY_EMAIL = os.environ.get('MY_EMAIL')
PASSWORD = os.environ.get('PASSWORD')
STOCK_API_KEY = os.getenv('STOCK_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

bull_bear = ''
diff_price_percentage = 0


def get_stock_data():
    stock_parameters = {
        'apikey': STOCK_API_KEY,
        'function': 'TIME_SERIES_DAILY',
        'symbol': STOCK,
    }

    response = requests.get(STOCK_ENDPOINT, params=stock_parameters)
    response.raise_for_status()
    data = response.json()["Time Series (Daily)"]
    data_list = [value for (item, value) in data.items()]
    yesterdays_closing_price = data_list[0]["4. close"]

    day_before_closing_price = data_list[1]["4. close"]

    difference_price = float(yesterdays_closing_price) - float(day_before_closing_price)
    if difference_price > 0:
        global bull_bear
        bull_bear = 'BULLISH ?'
    else:
        bull_bear = 'BEARISH ?'

    global diff_price_percentage
    diff_price_percentage = abs(difference_price) / float(day_before_closing_price) * 100

    if diff_price_percentage > 5:
        get_news()


def get_news():
    news_parameters = {
        'apiKey': NEWS_API_KEY,
        'q': STOCK
    }

    response = requests.get(NEWS_ENDPOINT, params=news_parameters)
    response.raise_for_status()
    data = response.json()['articles']
    three_articles = data[:3]

    formatted_articles = [f"Headline: {article['title']}. \nDetail: {article['description']}"
                          for article in three_articles]

    for article in formatted_articles:
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.ehlo()
            connection.starttls()
            connection.ehlo()
            connection.login(MY_EMAIL, PASSWORD)
            connection.sendmail(
                from_addr=MY_EMAIL,
                to_addrs="aasiffiraz123@gmail.com",
                msg=f"Subject:Market Update - {STOCK}: {round(diff_price_percentage, 2)}% - {bull_bear}\n\n{article}"
                    .encode("ascii", "ignore").decode("ascii"))


get_stock_data()
