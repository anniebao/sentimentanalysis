from flask import Flask, render_template, request, redirect
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import csv
import pandas as pd
from flaskext.mysql import MySQL
import mysql
from flask_mysqldb import MySQL
import mysql.connector
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '0000'
app.config['MYSQL_DB'] = 'mydatabase'
app.config['MYSQL_PORT'] = 3306

mysql = MySQL(app)
@app.route("/")
def main():
	return render_template('frontpage.html')

@app.route("/ticker")
def watchlist():
	return render_template('ticker.html')
	
@app.route("/manualentry")
def analyzer():
	return render_template('manualentry.html')
	
@app.route("/result", methods = ['POST'])
def ticker():
	text = request.form['ticker']
	ticker = text.upper()
	# db = MySQLdb.connect(host="localhost",user="root",passwd="0000",db="mydatabase",port=3306)
	conn=mysql.connect
	cur = conn.cursor()
	select_query = """ select avgsentiment from mydatabase.sentiments where ticker = %s """
	select_query_count = """ select count from mydatabase.sentiments where ticker = %s """
	cur.execute(select_query, [ticker])
	result = cur.fetchall()
	result = [i[0] for i in result]
	cur.execute(select_query_count, [ticker])
	count = cur.fetchall()
	count = [i[0] for i in count]
	
	cur.close()
	
	return render_template("result.html", result=result[0], ticker=ticker, count = count[0])

@app.route("/analyze", methods = ['POST'])
def result():
	text = request.form['comment']
	result = text.upper()

	stock_lex = pd.read_csv('C:/Users/baoannij/FlaskApp/stock_lex.csv')
	stock_lex['sentiment'] = (stock_lex['Aff_Score'] + stock_lex['Neg_Score'])/2
	stock_lex = dict(zip(stock_lex.Item, stock_lex.sentiment))
	stock_lex = {k:v for k,v in stock_lex.items() if len(k.split(' '))==1}
	stock_lex_scaled = {}
	for k, v in stock_lex.items():
		if v > 0:
			stock_lex_scaled[k] = v / max(stock_lex.values()) * 4
		else:
			stock_lex_scaled[k] = v / min(stock_lex.values()) * -4

	# Loughran and McDonald
	positive = []
	with open('C:/Users/baoannij/FlaskApp/pos.csv', 'r') as f:
		reader = csv.reader(f)
		for row in reader:
			positive.append(row[0].strip())
		
	negative = []
	with open('C:/Users/baoannij/FlaskApp/neg.csv', 'r') as f:
		reader = csv.reader(f)
		for row in reader:
			entry = row[0].strip().split(" ")
			if len(entry) > 1:
				negative.extend(entry)
			else:
				negative.append(entry[0])
				
				
	sia = SentimentIntensityAnalyzer()

	final_lex = {}
	final_lex.update({word:2.0 for word in positive})
	final_lex.update({word:-2.0 for word in negative})
	final_lex.update(stock_lex_scaled)
	final_lex.update(sia.lexicon)
	sia.lexicon = final_lex


	
	score = sia.polarity_scores(result)
	
	neg = score['neg']
	neu = score['neu']
	pos = score['pos']
	compound = score['compound']
		
	print(score)
	print("{:-<40} {}".format(result, str(score)))
	
	
	return render_template("analyze.html", result=result, neg=neg, neu=neu, pos=pos, compound=compound)

	
if __name__ == "__main__":
	app.run()
	