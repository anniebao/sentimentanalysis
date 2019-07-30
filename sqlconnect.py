import mysql.connector
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import csv
import pandas as pd

# stock market lexicon
stock_lex = pd.read_csv('C:/Users/baoannij/Downloads/stock_lex.csv')
stock_lex['sentiment'] = (stock_lex['Aff_Score'] + stock_lex['Neg_Score']) / 2
stock_lex = dict(zip(stock_lex.Item, stock_lex.sentiment))
stock_lex = {k: v for k, v in stock_lex.items() if len(k.split(' ')) == 1}
stock_lex_scaled = {}
for k, v in stock_lex.items():
    if v > 0:
        stock_lex_scaled[k] = v / max(stock_lex.values()) * 4
    else:
        stock_lex_scaled[k] = v / min(stock_lex.values()) * -4

# Loughran and McDonald
positive = []
with open('C:/Users/baoannij/Downloads/pos.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        positive.append(row[0].strip())

negative = []
with open('C:/Users/baoannij/Downloads/neg.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        entry = row[0].strip().split(" ")
        if len(entry) > 1:
            negative.extend(entry)
        else:
            negative.append(entry[0])

sia = SentimentIntensityAnalyzer()

final_lex = {}
final_lex.update({word: 2.0 for word in positive})
final_lex.update({word: -2.0 for word in negative})
final_lex.update(stock_lex_scaled)
final_lex.update(sia.lexicon)
sia.lexicon = final_lex


def sentiment_analyzer_scores(sentence):
    return sia.polarity_scores(sentence)

    print(score)
    print("{:-<40} {}".format(sentence, str(score)))


myfeed = feedparser.parse(r'c:\Users\baoannij\Downloads\tsla1.xml')

count = 0
totalSentiment = 0

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0000",
);

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE IF NOT EXISTS mydatabase")
mycursor.execute(
    "CREATE TABLE IF NOT EXISTS mydatabase.articles (ticker VARCHAR(45), title VARCHAR(255), description LONGTEXT, date VARCHAR(45), neg FLOAT(4), neu FLOAT(4), pos FLOAT(4), compound FLOAT(4))")
mycursor.execute(
    "CREATE TABLE IF NOT EXISTS mydatabase.sentiments (ticker VARCHAR(45), date VARCHAR(45), avgsentiment FLOAT(4), count FLOAT(4))")

for item in myfeed['items']:
    ticker = 'tsla'
    title = item.title
    description = item.description
    date = item.date
    sentiment = sentiment_analyzer_scores(item.description)
    neg = sentiment['neg']
    neu = sentiment['neu']
    pos = sentiment['pos']
    compound = sentiment['compound']
    count += 1
    totalSentiment += compound
    print(ticker)
    print(title)
    print(description)
    print(date)
    print(sentiment)

    sql = """INSERT INTO mydatabase.articles (ticker,title,description,date,neg,neu,pos,compound)
			 VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
    val = (ticker, title, description, date, neg, neu, pos, compound)

    mycursor.execute(sql, val)
    mydb.commit()
    print("added to db")

mycursor.close()

mydb.close()
avgSentiment = totalSentiment / count
print(avgSentiment)

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0000",
    database="mydatabase"
);

mycursor = mydb.cursor()
sql2 = """INSERT INTO sentiments (ticker, date, avgsentiment,count)
		  VALUES (%s,%s,%s,%s)"""
val2 = (ticker, date, avgSentiment, count)
mycursor.execute(sql2, val2)
mydb.commit()
mycursor.close()
mydb.close()
