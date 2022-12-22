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
import itertools
import time

app = Flask(__name__)
app.secret_key = 'app@Betting'

is_prod = os.getenv('IS_HEROKU')
print(is_prod)



def DBO():
	if is_prod != None:
		try:
			db = mysql.connector.connect(host=os.getenv("DB_SERVER"),    
			     user=os.getenv("DB_USER"),         
			     passwd=os.getenv("DB_PASS"),  
			     db=os.getenv("DB_NAME"))
		except Exception as e:
			print(str(e))
			time.sleep(1)
			DBO()
			pass
		
	else:
		try:
			db = mysql.connector.connect(host="127.0.0.1",    # your host, usually localhost
			     user="root",         # your username
			     passwd="root",  # your password
			     db="askabcry_betting")
		except Exception as e:
			print(str(e))
			DBO()
			pass



	return db

def calc(a, b, c):
	v1 = 1/a
	v2 = 1/b
	v3 = 1/b
	return v1+v2+v3

class Combine:
	def __init__(self, markets, user):
		self.user  = user
		self.combination = []
		self.combination_p= []
		try:
			db = DBO()
			cur = db.cursor(buffered=True)
			cur.execute("delete from user_combination where user=%s", (self.user,))
		except Exception as e:
			db.rollback()
			print(str(e))
			pass
		finally:
			db.commit()
			db.close()
		print(markets)
		allcombinations = list(itertools.product(markets))
		print(allcombinations)
		count = 0
		self.max_percent = 0
		self.max_odds = []
		for c in allcombinations:
			for y in c:
				try:
					res = []
					a = y[0]
					b = y[1]
					c = y[2]
					val = calc(float(a),float(b),float(c))
					if val < 1:
						if val*100 > self.max_percent:
							self.max_percent = val*100
							self.max_odds = y
						per = [y, val*100]
						res = [y, float(val)]
						self.add_list(res, "~")
						self.add_list(per, "%")
					break
				except Exception as e:
					print(str(e))
					pass
		
	def add_list(self,res,md):
		if md == "~":
			self.combination.append(res)
		if md == "%":
			self.combination_p.append(res)
	def get_list(self,md):
		if md == "~":
			return self.combination
		if md == "%":
			return self.combination_p
	def get_max(self):
		return [self.max_odds,self.max_percent]
	def add_database(self, res):
		try:
			db = DBO()
			cur = db.cursor(buffered=True)
			cur.execute("insert into user_combination(user, odd_one, odd_two, odd_three, result) values(%s,%s,%s,%s,%s) ", (self.user, res[0][0],res[0][1], res[0][2],res[1], ))
			
		except Exception as e:
			db.rollback();print(str(e))
			pass
		finally:
			db.commit()
			db.close()

@app.route("/request/<mode>", methods=['POST'])
def apiRequest(mode):
	if mode == "login":
		msg =  "not finished"
		if request.method == "POST" and "username" in request.form:
			username = request.form["username"]
			if username != "":
				session["user"] = username
				return "success"
			msg = "Invalid login credentials"
		return msg

@app.route("/login", methods=['GET'])
def login():

	return render_template("login.html",**locals())

@app.route("/logout")
def logout():
	session.clear()
	return redirect("/")

@app.route("/", methods=['GET'])
def home():
	#print(session.get("user"))
	#"""
	league = request.args.get("league")

	try:
		db = DBO()
		cur = db.cursor(buffered=True)
		if league != None:
			ll = "%"+league+"%"
			cur.execute("SELECT * FROM home_matches where league =%s or league like %s", (league,ll, ))
			matches = cur.fetchall()
		else:		
			cur.execute("SELECT * FROM home_matches")
			matches = cur.fetchall()
		
	except Exception as e:
		db.rollback();print(str(e))
		pass
	finally:
		db.close()

	
	#matches = []
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
				db.rollback()
				print(str(e))
				pass
			finally:
				db.close()
		return render_template("bookmarks.html", **locals())
"""
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
"""
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
				db.rollback()
				print(str(e))
				pass
			finally:
				db.close()
	return render_template("search.html", **locals())

@app.route("/home/match/<match>")
def gethomeMatch(match):
	if match:
		market_odds = []
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
			if " "not in match_bd[1]:
				match_bdd = " "+match_bd[1]
			else:
				match_bdd = match_d[1]
			match_bb = match_bdd.split(" ")
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
			for mk in markets:
				r = [mk[6], mk[7],mk[8]]
				market_odds.append(r)
			for mk in other_markets:
				r = [mk[3],mk[4],mk[5]]
				market_odds.append(r)
		except Exception as e:
			db.rollback();print(str(e))
			pass
		finally:
			db.close()
		
		if session.get("user") is not None:
			n = len(market_odds)
			ck = Combine(market_odds, session["user"])			
			combinations = ck.get_list("~")
			combinations_p = ck.get_list("%")
			cm = ""
			for combination in combinations:
				cm = cm+"<div class='bets'><button>"+str(combination[0][0])+"</button><button>"+str(combination[0][1])+"</button><button>"+str(combination[0][2])+"</button><div class='res'>"+"{:.2f}".format(combination[1])+"</div></div>"
			cm_p = ""
			for combination in combinations_p:
				cm_p = cm_p + "<div class='bets'><button>"+str(combination[0][0])+"</button><button>"+str(combination[0][1])+"</button><button>"+str(combination[0][2])+"</button><div class='res'>"+"{:.2f}".format(combination[1])+"</div></div>"
			max_percent = ck.get_max()
		return render_template("homematch.html", **locals())

@app.route("/bookmaker/match/<match>")
def getBookMarkets(match):
	if match:
		market_odds = []
		x = match.split("-")
		xeid = x[-1]
		#print(xeid)
		try:
			db = DBO()
			cur = db.cursor(buffered=True)
			cur.execute("SELECT * FROM bookmark_matches WHERE xeid=%s", (xeid,))
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
			if " "not in match_bd[1]:
				match_bdd = " "+match_bd[1]
			else:
				match_bdd = match_d[1]
			match_bb = match_bdd.split(" ")
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
			for mk in markets:
				r = [mk[6], mk[7],mk[8]]
				market_odds.append(r)
			for mk in other_markets:
				r = [mk[3],mk[4],mk[5]]
				market_odds.append(r)
		except Exception as e:
			db.rollback();print(str(e))
			pass
		finally:
			db.close()
		
		if session.get("user") is not None:
			n = len(market_odds)
			ck = Combine(market_odds, session["user"])			
			combinations = ck.get_list("~")
			combinations_p = ck.get_list("%")
			cm = ""
			for combination in combinations:
				cm = cm+"<div class='bets'><button>"+str(combination[0][0])+"</button><button>"+str(combination[0][1])+"</button><button>"+str(combination[0][2])+"</button><div class='res'>"+"{:.2f}".format(combination[1])+"</div></div>"
			cm_p = ""
			for combination in combinations_p:
				cm_p = cm_p + "<div class='bets'><button>"+str(combination[0][0])+"</button><button>"+str(combination[0][1])+"</button><button>"+str(combination[0][2])+"</button><div class='res'>"+"{:.2f}".format(combination[1])+"</div></div>"
			max_percent = ck.get_max()
		return render_template("bookmatch.html", **locals())

@app.route("/user/combination")
def getCombination():
	req = request.args.get("inverse")
	reqp = request.args.get("percent")
	if req != None:
		return render_template("combinations.html")
	if reqp != None:
		return render_template("combinations_p.html")

if __name__ == "__main__":
	app.run(host="0.0.0.0", debug=True)
