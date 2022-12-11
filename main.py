from flask import Flask, render_template, request, redirect, url_for, session, Response
import re
from IPython.display import HTML
from bs4 import BeautifulSoup 
import requests
import random
import os
import mysql.connector
import datetime
from datetime import timedelta

app = Flask(__name__)
app.debug = True
app.secret_key = 'app@Betting'

def DBO():
	db = mysql.connector.connect(host="192.185.81.65",    
                     user="askabcry_root",         
                     passwd="tryhackmeanddie",  
                     db="askabcry_betting")

	return db


@app.route("/", methods=['GET'])
def home():
	try:
		db = DBO()
		cur = db.cursor(buffered=True)
		cur.execute("SELECT * FROM matches")
		matches = cur.fetchall()
		cur.execute("SELECT * FROM matches_date")
		matches_date = cur.fetchall()
	except Exception as e:
		db.rollback();print(str(e))
		pass
	finally:
		db.close()
	return render_template("home.html", **locals())

@app.route("/best-today", methods=['GET'])
def bestToday():
	time_today = datetime.datetime.now() - timedelta(days=1)
	#print(last_online)
	try:
		db = DBO()
		cur = db.cursor(buffered=True)
		cur.execute("SELECT max(home_odd) FROM matches WHERE time >= %s",(time_today, ))
		maxh = cur.fetchone()
		if maxh:
			cur.execute("SELECT * FROM matches WHERE home_odd=%s", (maxh ))
			home_matches = cur.fetchone()
		cur.execute("SELECT max(draw_odd) FROM matches WHERE time >= %s",(time_today, ))
		maxh = cur.fetchone()
		if maxh:
			cur.execute("SELECT * FROM matches WHERE draw_odd=%s", (maxh ))
			draw_matches = cur.fetchone()
		cur.execute("SELECT max(away_odd) FROM matches WHERE time >= %s",(time_today, ))
		maxh = cur.fetchone()
		if maxh:
			cur.execute("SELECT * FROM matches WHERE away_odd=%s", (maxh ))
			away_matches = cur.fetchone()
		cur.execute("SELECT * FROM matches_date")
		matches_date = cur.fetchall()

	except Exception as e:
		db.rollback();print(str(e))
		pass
	finally:
		db.close()

	return render_template("best.html", **locals())

@app.route("/match/<match>")
def getMatch(match):
	if match:
		x = match.split("-")
		xeid = x[-1]
		try:
			db = DBO()
			cur = db.cursor(buffered=True)
			cur.execute("SELECT * FROM matches WHERE xeid=%s", (xeid,))
			matches = cur.fetchone()
			cur.execute("SELECT * FROM matches_date WHERE xeid=%s", (xeid,))
			match_date = cur.fetchone()
		except Exception as e:
			db.rollback();print(str(e))
			pass
		finally:
			db.close()
		return render_template("match.html", **locals())


	return render_template("match.html", **locals())
@app.route("/markets/<mat>")
def getMarkets(mat):
	print(mat)
	if mat:
		try:
			db = DBO()
			cur = db.cursor(buffered=True)
			cur.execute("SELECT * FROM matches WHERE xeid=%s", (mat,))
			matches = cur.fetchone()
			cur.execute("SELECT * FROM bookmakers WHERE xeid=%s", (mat,))
			markets = cur.fetchall()
			n = len(markets)
		except Exception as e:
			db.rollback();print(str(e))
			pass
		finally:
			db.close()
		return render_template("markets.html", **locals())

app.run(host="0.0.0.0", port=8080)
