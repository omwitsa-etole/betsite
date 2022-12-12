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
app.secret_key = 'app@Betting'

is_prod = os.getenv('IS_HEROKU')


def DBO():
	if is_prod != None:
		db = mysql.connector.connect(host=os.getenv("DB_SERVER"),    
                     user=os.getenv("DB_USER"),         
                     passwd=os.getenv("DB_PASS"),  
                     db=os.getenv("DB_NAME"))
	else:
		db = mysql.connector.connect(host="localhost",    
                     user="root",         
                     passwd="root",  
                     db="betting")

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
		print(matches_date)
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

@app.route("/bookmaker/<book>")
def getBookmaker(book):
	if book:
		book_league = book.replace("-", " / ")
		book_league = book_league.upper()
		league = request.args.get("league")
		if league == None:
			try:
				db = DBO()
				cur = db.cursor(buffered=True)
				cur.execute("SELECT * FROM bookmark_matches WHERE bookmark=%s", (book,))
				matches = cur.fetchall()
				print(matches[0][5])
			except Exception as e:
				db.rollback();print(str(e))
				pass
			finally:
				db.close()
		else:
			try:
				db = DBO()
				cur = db.cursor(buffered=True)
				cur.execute("SELECT * FROM bookmark_matches WHERE bookmark=%s and league=%s", (book, league,))
				matches = cur.fetchall()
				
			except Exception as e:
				db.rollback();print(str(e))
				pass
			finally:
				db.close()
		return render_template("bookmarks.html", **locals())

@app.route("/bookmaker/match/<bookmatch>")
def BookMatch(bookmatch):
	if bookmatch:
		bookmark = "N/A"
		x = bookmatch.split("-")
		xeid = x[-1]
		try:
			db = DBO()
			cur = db.cursor(buffered=True)
			cur.execute("SELECT * FROM bookmark_matches WHERE xeid=%s", (xeid,))
			matches = cur.fetchone()
			if matches:
				bookmark = matches[12] 
				bookmark = bookmark.split("-")
		except Exception as e:
			db.rollback();print(str(e))
			pass
		finally:
			db.close()
		return render_template("bookmatch.html", **locals())
if __name__ == "__main__":
	app.run(host="0.0.0.0", debug=True)
