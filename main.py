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
		cur.execute("SELECT * FROM home_matches")
		matches = cur.fetchall()
		
	except Exception as e:
		db.rollback();print(str(e))
		pass
	finally:
		db.close()
	return render_template("home.html", **locals())

@app.route("/topnav")
def getNav():
	return render_template("topnav.html", **locals())

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
				#print(matches[0][5])
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
		print(x)
		mt = "%"+x[0]+"-"+x[1]+"%"
		md = mt.replace("-", " - ")
		print(mt)
		try:
			db = DBO()
			cur = db.cursor(buffered=True)
			cur.execute("SELECT * FROM bookmark_matches WHERE xeid=%s or match_teams like %s or match_teams like %s", (xeid,mt,md,))
			matches = cur.fetchone()
			if matches:
				bookmark = matches[12] 
				bookmark = bookmark.split("-")
				matchteams = matches[5]
			
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
	bookmark = request.args.get("bookmark")
	if match != None and league == None and bookmark == None:
		if "vs" in match:
			match = match.replace("vs", "-")
		match = "%"+match+"%"
		try:
			db = DBO()
			cur = db.cursor(buffered=True)
			cur.execute("SELECT * FROM home_matches where match_teams LIKE %s", (match, ))
			home_matches = cur.fetchall()
			cur.execute("SELECT * FROM bookmark_matches where match_teams LIKE %s", (match, ))
			matches = cur.fetchall()
			
		except Exception as e:
			db.rollback();print(str(e))
			pass
		finally:
			db.close()
	elif league != None and match == None:
		league = "%"+league+" %"
		ll = league.replace(" ", "-")
		try:
			db = DBO()
			cur = db.cursor(buffered=True)
			cur.execute("SELECT * FROM home_matches where league LIKE %s or league like %s", (league, ll, ))
			home_matches = cur.fetchall()
			cur.execute("SELECT * FROM bookmark_matches where league LIKE %s", (league, ))
			matches = cur.fetchall()
			
		except Exception as e:
			db.rollback();print(str(e))
			pass
		finally:
			db.close()
	elif bookmark != None and match != None:
		if "vs" in match:
			match = match.replace("vs", "-")
		match = "%"+match+"%"
		try:
			db = DBO()
			cur = db.cursor(buffered=True)
			cur.execute("SELECT * FROM bookmakers where bookmark=%s and match_teams LIKE %s", (bookmark, match, ))
			book_matches = cur.fetchall()
			cur.execute("SELECT * FROM bookmakers where id is null")
			home_matches = cur.fetchall()
			matches = home_matches
		except Exception as e:
			db.rollback();print(str(e))
			pass
		finally:
			db.close()
	else:
		if book != None:
			old_book = book+"-football"
			book = "%"+book+"%"
			query = request.args.get("type")
			if query != None and query != "":
				query = "%"+query+"%"
				try:
					db = DBO()
					cur = db.cursor(buffered=True)
					cur.execute("SELECT * FROM home_matches where bookmark=%s and match_teams like %s or league like %s", (old_book, query, query,))
					home_matches = cur.fetchall()
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
					cur.execute("SELECT * FROM home_matches WHERE bookmark like %s", (book, ))
					home_matches = cur.fetchall()
					cur.execute("SELECT * FROM bookmark_matches WHERE bookmark like %s", (book, ))
					matches = cur.fetchall()
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

@app.route("/home/match/<match>")
def gethomeMatch(match):
	if match:
		x = match.split("-")
		xeid = x[-1]
		#print(xeid)
		try:
			db = DBO()
			cur = db.cursor(buffered=True)
			cur.execute("SELECT * FROM home_matches WHERE xeid=%s", (xeid,))
			matches = cur.fetchone()
			match = matches[5]
			matchteams = match
			
			match = match.lower()
			prev_match = match
			match_check = match.split("-")
			if "city" in match_check[0]:
				match = match.replace("city", "")
			if "wolverhampton" in match:
				match = match.replace("wolverhampton", "wolves")
			if "utd" in match:
				match = match.replace("utd", "united")
			if "wanderers" in match:
				match = match.replace("wanderers", "")
			if "hotspur" in match:
				match = match.replace("hotspur", "")
			if "lfc" in match:
				match = match.replace("lfc", "")
			
			#print(match)
			prev_match = prev_match.split("-")
			match_bd = prev_match
			prev_match_t = "%"+prev_match[0].replace(" ", "")+"-"+prev_match[-1][0:2]+"%"
			prev_match = "%"+prev_match[0].replace(" ", "")+"-"+prev_match[-1][1:3]+"%"
			prev_match_d = prev_match.replace("-", " - ")
			match_teams = match.replace(" - ", "-")
			match_teams = "%" + match_teams + "%"
			match_d = match+" "
			match_d = match_d.split("-")
			match_bb = match_bd[1].split(" ")
			match_bb = match_bb[1]
			match_b = "%"+match_bd[0][-4:-1] +" - " + match_bb +"%"
			match_bb = match_b.replace(" - ", "-")
			matchl = match_d[1].split(" ")
			match_t = "%"+match_d[0] + " - "+ matchl[1]+"%"
			match_d = match_t.replace(" ", "")
			match = "%"+match+"%"
			match_t = match_d.replace("-", " - ")
			#print(match_b)
			#print(match_bb)
			#print(match_t)
			#print(prev_match_t)
			best_home = None
			best_away = None
			best_draw = None
			db = DBO()
			cur = db.cursor(buffered=True)
			cur.execute("SELECT * FROM bookmark_matches WHERE match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s", (match, match_teams, match_d,match_t,prev_match,prev_match_d,prev_match_t,match_b,match_bb, ))
			markets = cur.fetchall()
			cur.execute("SELECT * FROM bookmakers WHERE match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s", (match, match_teams,match_d,match_t,prev_match,prev_match_d,prev_match_t,match_b,match_bb, ))
			other_markets = cur.fetchall()
			cur.execute("select max(cast(home_odd as decimal(10,2))), max(cast(draw_odd as decimal(10,2))), max(cast(away_odd as decimal(10,2))) from bookmark_matches WHERE match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s", (match, match_teams, match_d,match_t,prev_match,prev_match_d,prev_match_t,match_b, match_bb,))
			match_odds = cur.fetchone()
			cur.execute("select max(cast(home_odd as decimal(10,2))), max(cast(draw_odd as decimal(10,2))), max(cast(away_odd as decimal(10,2))) from bookmakers WHERE match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s", (match, match_teams, match_d,match_t,prev_match,prev_match_d,prev_match_t,match_b, match_bb,))
			book_odds = cur.fetchone()
			#print(match_odds)
			#print(book_odds)
			#if match_odds and book_odds:
			#print("here")
			if match_odds[0] is not None and book_odds[0] is None:
				best_home = match_odds[0]
				best_draw = match_odds[1]
				best_away = match_odds[2]
			if book_odds[0] is not None and match_odds[0] is None:	
				best_home = book_odds[0]
				best_draw = book_odds[1]
				best_away = book_odds[2]
			if book_odds[0] is not None and match_odds[0] is not None:
				best_home = max(float(match_odds[0]), float(book_odds[0]))
				best_draw = max(float(match_odds[1]), float(book_odds[1]))
				best_away = max(float(match_odds[2]), float(book_odds[2]))
			
			#print(best_away)
		except Exception as e:
			db.rollback();print(str(e))
			pass
		finally:
			db.close()
		return render_template("homematch.html", **locals())

@app.route("/bookmaker/match/markets/<match>")
def getBookMarkets(match):
	if match:
		try:
			match = match.replace("vs", "-")
		except:
			pass
		try:
			match = match.lower()
			match_check = match.split("-")
			prev_match = match
			if "city" in match_check[0]:
				match = match.replace("city", "")
			if "wolverhampton" in match:
				match = match.replace("wolverhampton", "wolves")
			if "utd" in match:
				match = match.replace("utd", "united")
			if "wanderers" in match:
				match = match.replace("wanderers", "")
			if "hotspur" in match:
				match = match.replace("hotspur", "")
			if "town" in match:
				match = match.replace("town", "")
			if "lfc" in match:
				match = match.replace("lfc", "")
			if "fc" in match:
				match = match.replace("fc", "")
			
			#print(match)
			prev_match = prev_match.split("-")
			match_bd = prev_match
			prev_match_t = "%"+prev_match[0].replace(" ", "")+"-"+prev_match[-1][0:2]+"%"
			prev_match = "%"+prev_match[0].replace(" ", "")+"-"+prev_match[-1][1:3]+"%"
			prev_match_d = prev_match.replace("-", " - ")
			#print(prev_match)
			#print(prev_match_d)
			match_teams = match.replace(" - ", "-")
			match_teams = "%" + match_teams + "%"
			match_d = match+" "
			match_d = match_d.split("-") 
			match_bb = match_bd[1].split(" ")
			match_bb = match_bb[1]
			match_b = "%"+match_bd[0][-4:-1] +" - " + match_bb +"%"
			match_bb = match_b.replace(" - ", "-")
			matchl = match_d[1].split(" ")
			match_t = "%"+match_d[0] + " - "+ matchl[1]+"%"
			match_d = match_t.replace(" ", "")
			match = "%"+match+"%"
			match_t = match_d.replace("-", " - ")
			#print(match_b)
			#print(match_bb)
			#print(match_t)
			#print(prev_match_t)
			best_home = None
			best_away = None
			best_draw = None
			db = DBO()
			cur = db.cursor(buffered=True)
			cur.execute("SELECT * FROM bookmark_matches WHERE match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s", (match, match_teams, match_d,match_t,prev_match,prev_match_d,prev_match_t,match_b,match_bb, ))
			markets = cur.fetchall()
			cur.execute("SELECT * FROM bookmakers WHERE match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s", (match, match_teams,match_d,match_t,prev_match,prev_match_d,prev_match_t,match_b,match_bb, ))
			other_markets = cur.fetchall()
			cur.execute("select max(cast(home_odd as decimal(10,2))), max(cast(draw_odd as decimal(10,2))), max(cast(away_odd as decimal(10,2))) from bookmark_matches WHERE match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s", (match, match_teams, match_d,match_t,prev_match,prev_match_d,prev_match_t,match_b, match_bb,))
			match_odds = cur.fetchone()
			cur.execute("select max(cast(home_odd as decimal(10,2))), max(cast(draw_odd as decimal(10,2))), max(cast(away_odd as decimal(10,2))) from bookmakers WHERE match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s", (match, match_teams, match_d,match_t,prev_match,prev_match_d,prev_match_t,match_b, match_bb,))
			book_odds = cur.fetchone()
			matchl = match_d[1].split(" ")
			match_t = "%"+match_d[0] + " - "+ matchl[1]+"%"
			match_d = match_t.replace(" ", "")
			match = "%"+match+"%"
			match_t = match_d.replace("-", " - ")
			print(match_b)
			#print(match_t)
			best_home = None
			best_away = None
			best_draw = None
			db = DBO()
			cur = db.cursor(buffered=True)
			cur.execute("SELECT * FROM bookmark_matches WHERE match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s", (match, match_teams, match_d,match_t,prev_match,prev_match_d,prev_match_t,match_b ))
			markets = cur.fetchall()
			cur.execute("SELECT * FROM bookmakers WHERE match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s", (match, match_teams,match_d,match_t,prev_match,prev_match_d,prev_match_t,match_b, ))
			other_markets = cur.fetchall()
			cur.execute("select max(cast(home_odd as decimal(10,2))), max(cast(draw_odd as decimal(10,2))), max(cast(away_odd as decimal(10,2))) from bookmark_matches WHERE match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s", (match, match_teams, match_d,match_t,prev_match,prev_match_d,prev_match_t,match_b, ))
			match_odds = cur.fetchone()
			cur.execute("select max(cast(home_odd as decimal(10,2))), max(cast(draw_odd as decimal(10,2))), max(cast(away_odd as decimal(10,2))) from bookmakers WHERE match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s", (match, match_teams, match_d,match_t,prev_match,prev_match_d,prev_match_t,match_b, ))
			book_odds = cur.fetchone()
			#print(match_odds)
			#print(book_odds[0])
			if match_odds[0] is not None and book_odds[0] is None:
				best_home = match_odds[0]
				best_draw = match_odds[1]
				best_away = match_odds[2]
			if book_odds[0] is not None and match_odds[0] is None:	
				best_home = book_odds[0]
				best_draw = book_odds[1]
				best_away = book_odds[2]
			if book_odds[0] is not None and match_odds[0] is not None:
				best_home = max(float(match_odds[0]), float(book_odds[0]))
				best_draw = max(float(match_odds[1]), float(book_odds[1]))
				best_away = max(float(match_odds[2]), float(book_odds[2]))
			#print(best_away)
		except Exception as e:
			db.rollback();print(str(e))
			pass
		finally:
			db.close()
		return render_template("bookmarkets.html", **locals())

if __name__ == "__main__":
	app.run(host="0.0.0.0", debug=True)
