
# coding: utf-8

# In[13]:

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import csv
import pandas as pd

# stock market lexicon
stock_lex = pd.read_csv('C:/Users/baoannij/Downloads/stock_lex.csv')
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
final_lex.update({word:2.0 for word in positive})
final_lex.update({word:-2.0 for word in negative})
final_lex.update(stock_lex_scaled)
final_lex.update(sia.lexicon)
sia.lexicon = final_lex



def sentiment_analyzer_scores(sentence):
    score = sia.polarity_scores(sentence)
    print(str(score))
    print("{:-<40} {}".format(sentence, str(score)))
    
    
sentiment_analyzer_scores("today is a great day")

