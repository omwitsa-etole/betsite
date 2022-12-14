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
print(is_prod)

def DBO():
	if is_prod != None:
		db = mysql.connector.connect(host=os.getenv("DB_SERVER"),    
		     user=os.getenv("DB_USER"),         
		     passwd=os.getenv("DB_PASS"),  
		     db=os.getenv("DB_NAME"))
	else:
		while True:
			try:
				db = mysql.connector.connect(host="192.185.81.65",    # your host, usually localhost
				     user="askabcry_root",         # your username
				     passwd="tryhackmeanddie",  # your password
				     db="askabcry_betting")
				break
			except:
				pass



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
	print(time_today)
	try:
		db = DBO()
		cur = db.cursor(buffered=True)
		cur.execute("SELECT max(home_odd) FROM bookmark_matches")
		maxh = cur.fetchone()
		if maxh:
			cur.execute("SELECT * FROM bookmark_matches WHERE home_odd=%s", (maxh ))
			home_matches = cur.fetchone()
		cur.execute("SELECT max(draw_odd) FROM bookmark_matches")
		maxh = cur.fetchone()
		if maxh:
			cur.execute("SELECT * FROM bookmark_matches WHERE draw_odd=%s", (maxh ))
			draw_matches = cur.fetchone()
		cur.execute("SELECT max(away_odd) FROM bookmark_matches")
		maxh = cur.fetchone()
		if maxh:
			cur.execute("SELECT * FROM bookmark_matches WHERE away_odd=%s", (maxh ))
			away_matches = cur.fetchone()
		
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
@app.route("/search")
def search():
	match = request.args.get("matches")
	league = request.args.get("leagues")
	book = request.args.get("book")
	if match != None and league == None:
		print(match)
		if "vs" in match:
			match = match.replace("vs", "-")
		match = "%"+match+"%"
		try:
			db = DBO()
			cur = db.cursor(buffered=True)
			cur.execute("SELECT * FROM bookmark_matches where match_teams LIKE %s", (match, ))
			matches = cur.fetchall()
			
		except Exception as e:
			db.rollback();print(str(e))
			pass
		finally:
			db.close()
	elif league != None and match == None:
		league = "%"+league+"%"
		try:
			db = DBO()
			cur = db.cursor(buffered=True)
			cur.execute("SELECT * FROM bookmark_matches where league LIKE %s", (league, ))
			matches = cur.fetchall()
			
		except Exception as e:
			db.rollback();print(str(e))
			pass
		finally:
			db.close()
	else:
		if book != None:
			old_book = book+"-football"
			book = "%"+book+"%"
			print(book)
			query = request.args.get("type")
			if query != None and query != "":
				query = "%"+query+"%"
				print(query)
				try:
					db = DBO()
					cur = db.cursor(buffered=True)
					cur.execute("SELECT * FROM bookmark_matches WHERE bookmark=%s and match_teams like %s or league like %s", (old_book, query, query, ))
					matches = cur.fetchall()
					print("here")
				except Exception as e:
					db.rollback();print(str(e))
					pass
				finally:
					db.close()
				return render_template("search.html", **locals())
			else:
				try:
					db = DBO()
					cur = db.cursor(buffered=True)
					cur.execute("SELECT * FROM bookmark_matches WHERE bookmark like %s", (book, ))
					matches = cur.fetchall()
					print("here2")
				except Exception as e:
					db.rollback();print(str(e))
					pass
				finally:
					db.close()
				return render_template("search.html", **locals())
		else:
			try:
				db = DBO()
				cur = db.cursor(buffered=True)
				cur.execute("SELECT * FROM bookmark_matches")
				matches = cur.fetchall()
				
			except Exception as e:
				db.rollback();print(str(e))
				pass
			finally:
				db.close()
	return render_template("search.html", **locals())

@app.route("/markets/bookmaker/<match>")
def getBookMarkets(match):
	if match:
		match_teams = match.replace(" - ", "-")
		
		match_teams = "%" + match_teams + "%"
		match = "%"+match+"%"
		
		try:
			db = DBO()
			cur = db.cursor(buffered=True)
			cur.execute("SELECT * FROM bookmark_matches WHERE match_teams like %s or match_teams like %s", (match, match_teams, ))
			markets = cur.fetchall()
		except:
			print(str(e))
			pass
		finally:
			db.close()
		return render_template("bookmarkets.html", **locals())

if __name__ == "__main__":
	app.run(host="0.0.0.0", debug=True)
