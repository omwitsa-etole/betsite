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


def get_code():
	pass

def DBO():
	try:
		db = mysql.connector.connect(host="localhost",    # your host, usually localhost
		     user="root",         # your username
		     passwd="root",  # your password
		     db="askabcry_betting")
		return db
	except Exception as e:
		print(str(e))
		pass
		
	
	while True:
		try:
			db = mysql.connector.connect(host="192.185.81.65",    # your host, usually localhost
			     user="askabcry_root",         # your username
			     passwd="tryhackmeanddie",  # your password
			     db="askabcry_betting")
			break
		except Exception as e:
			print(str(e))
			pass



	return db

def getRand(vals):
	return random.choice(vals)

def getPower(n):
	
	return n*n*n

def calc(a, b, c):
	
	return (1/a)+(1/b)+(1/c)


class Combine:
	def __init__(self, markets, user):
		self.user  = user
		self.combination = []
		self.combination_p= []
		self.combination_above = []
		self.combination_above_p = []
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
		self.max_percent = 0
		self.max_odds = []
		self.markets = markets
		self.cnt = 0
		self.getCombinations(markets[0:5])
		
	def getCombinations(self,ms):
		count = 0

		ls = ms
		l = ls
		cn = getPower(len(l))
		while True:

			if len(ls) >= cn:
				break
			for i in range(0,len(l)):
				x = l[i][0]
				cnt = 0
				l1 = []
				l2 = []
				while True:
					try:
						l1.append(l[i-cnt][1])
						l2.append(l[i-cnt][2])
						cnt = cnt+1
					except:
						break

				
				y = getRand(l1)
				z = getRand(l2)
				m = [x,y,z]
				ls.append(m)
				try:
					res = []
					a = x
					b = y
					c = z
					val = calc(float(a),float(b),float(c))
					
					if val < 1:
						
						if val*100 > self.max_percent:
							self.max_percent = val*100
							self.max_odds = m
						per = [m, val*100]
						res = [m, float(val)]
						self.add_list(res, "~")
						self.add_list(per, "%")
					else:
						per = [m, val*100]
						res = [m, float(val)]
						self.add_list(res, ">~")
						self.add_list(per, ">%")
					self.cnt = self.cnt + 1
				except Exception as e:
					print(str(e))
					pass
		
	def add_list(self,res,md):
		if md == "~":
			if res not in self.combination:
				self.combination.append(res)
		if md == "%":
			if res not in self.combination_p:
				self.combination_p.append(res)
		if md == ">~":
			if res not in self.combination_above:
				self.combination_above.append(res)
		if md == ">%":
			if res not in self.combination_above_p:
				self.combination_above_p.append(res)
	def get_list(self,md):
		if md == "~":
			return self.combination
		if md == "%":
			return self.combination_p
		if md == ">~":
			return self.combination_above
		if md == ">%":
			return self.combination_above_p
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
	country = 'home'
	league = request.args.get("league")
	count = request.args.get("filter")
	if count != None:
		country = count
	time_filter = request.args.get("time")
	print(time_filter)

	db = DBO()
	cur = db.cursor(buffered=True)
	if league != None and country != None and time_filter == None:
		ll = "%"+league+"%"
		
		cur.execute("SELECT * FROM home_matches where league=%s and country=%s", (league,country, ))
		matches = cur.fetchall()
		return render_template("home.html", **locals())
	elif league != None and country == None:
		ll = "%"+league+"%"
		cur.execute("SELECT * FROM home_matches WHERE country='home' AND league =%s or league like %s", (league,ll, ))
		matches = cur.fetchall()
		return render_template("home.html", **locals())
	elif country != None and league == None:
		cur.execute("SELECT * FROM home_matches where country=%s", (country, ))
		matches = cur.fetchall()
		return render_template("home.html", **locals())
	elif time_filter != None and league == None:
		cur.execute("SELECT * FROM home_matches where country='home' ORDER BY match_time asc")
		matches = cur.fetchall()
		return render_template("home.html", **locals())
	elif time_filter != None and league != None:
		ll = "%"+league+"%"
		cur.execute("SELECT * FROM home_matches where country='home' and league =%s or league like %s ORDER BY match_time asc", (league,ll, ) )
		matches = cur.fetchall()
		return render_template("home.html", **locals())
	elif league != None and country != None and time_filter != None:
		ll = "%"+league+"%"
		
		cur.execute("SELECT * FROM home_matches where league=%s or league like %s and country=%s ORDER BY match_time asc", (league, ll,country, ))
		matches = cur.fetchall()
		return render_template("home.html", **locals())
	else:		
		cur.execute("SELECT * FROM home_matches where country='home'")
		matches = cur.fetchall()
		return render_template("home.html", **locals())
	
	#matches = []
	#return render_template("home.html", **locals())

@app.route("/calculator")
def getCalc():
	match = request.args.get("match")
	if match == None:
		return """
			<div class="t-ody" style="position: relative;background: black;height: 60px;">
				<h2 style="position: absolute;left: 2%;color: yellow;" onclick="location.href='/'">SureBet</h2><br>

				<div style="float: right;color: white;"><a href='/?login' style="margin-left: 10px;">Login</a><a style="margin-left: 20px;">Signup</a></div>
				
				</div><br><center>Select A <a href='/'>match</a> to perfom calculations</center>
				"""
	if session.get("user") != None:
		return render_template("calculator.html", **locals())
	else:
		return """
			<div class="t-ody" style="position: relative;background: black;height: 60px;">
				<h2 style="position: absolute;left: 2%;color: yellow;" onclick="location.href='/'">SureBet</h2><br>

				<div style="float: right;color: white;"><a href='/?login' style="margin-left: 10px;">Login</a><a style="margin-left: 20px;">Signup</a></div>
				
				</div><br><center>Login to Perfom calculations <a href='/?login'>Login</a></center>
				"""

@app.route("/topnav")
def getNav():
	all_links = ['Nigeria', 'Kenya', 'Ghana', 'Gambia', 'Jamaica', 'Morocco', 'Niger', 'Mali', 'Mauritius', 'Rwanda', 'Senegal','Uganda', 'South Africa', 'Zambia', 'Zimbabwe']
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
		time_filter = request.args.get("time")
		bk = "%"+book+"%"
		#print(bk)
		if league == None and time_filter == None:
			try:
				db = DBO()
				cur = db.cursor(buffered=True)
				cur.execute("SELECT * FROM bookmark_matches WHERE bookmark=%s or bookmark like %s", (book,bk,))
				matches = cur.fetchall()
				#print(matches[0][5])
			except Exception as e:
				db.rollback();print(str(e))
				pass
			finally:
				db.close()
		elif league == None and time_filter != None:
			try:
				db = DBO()
				cur = db.cursor(buffered=True)
				cur.execute("SELECT * FROM bookmark_matches WHERE bookmark=%s or bookmark like %s ORDER BY match_time asc", (book,bk,))
				matches = cur.fetchall()
				#print(matches[0][5])
			except Exception as e:
				db.rollback();print(str(e))
				pass
			finally:
				db.close()
		elif league != None and time_filter != None:
			try:
				db = DBO()
				cur = db.cursor(buffered=True)
				cur.execute("SELECT * FROM bookmark_matches WHERE bookmark=%s or bookmark like %s and league=%s ORDER BY match_time asc", (book, bk,league,))
				matches = cur.fetchall()
				
			except Exception as e:
				db.rollback()
				print(str(e))
				pass
			finally:
				db.close()
		else:
			try:
				db = DBO()
				cur = db.cursor(buffered=True)
				cur.execute("SELECT * FROM bookmark_matches WHERE bookmark=%s or bookmark like %s and league=%s", (book, bk,league,))
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
		bk = "%"+bookmark+"%"
		try:
			db = DBO()
			cur = db.cursor(buffered=True)
			cur.execute("SELECT * FROM bookmakers where bookmark=%s or bookmark like %s and match_teams LIKE %s", (bookmark,bk, match, ))
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
			bk = "%"+book+"%"
			query = request.args.get("type")
			if query != None and query != "":
				query = "%"+query+"%"
				try:
					db = DBO()
					cur = db.cursor(buffered=True)
					cur.execute("SELECT * FROM home_matches where bookmark=%s or bookmark like %s and match_teams like %s or league like %s", (old_book,bk, query, query,))
					home_matches = cur.fetchall()
					cur.execute("SELECT * FROM bookmark_matches WHERE bookmark=%s or bookmark like %s and match_teams like %s or league like %s", (old_book,bk, query, query, ))
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
		country = request.args.get("filter")
		
		max_percent = [[], 0]
		market_odds = []
		x = match.split("-")
		xeid = x[-1]
		#print(xeid)
		try:
			db = DBO()
			cur = db.cursor(buffered=True)
			cur.execute("SELECT * FROM home_matches WHERE xeid=%s", (xeid,))
			matches = cur.fetchone()
			session["match"] = matches[1]
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
			if "paris saint germain" in match:
				match = match.replace("paris saint germain", "psg")
			
			#print(match)
			prev_match = prev_match.split("-")
			match_bd = prev_match
			hb = "%"+prev_match[0]+"%"
			ab = "%"+prev_match[1]+"%"
			home_prev = prev_match[0][0:3]
			home_prev = "%"+home_prev+"%"
			away_prev = prev_match[1][1:4]
			away_prev = "%"+away_prev+"%"
			home_match = match.split("-")[0][0:3]
			away_match = match.split("-")[1][1:4]
			hm = "%"+match.split("-")[0]+"%"
			am = "%"+match.split("-")[1]+"%"
			if " " in hm:
				hm = hm.replace(" ", "")
			if " " in am:
				am = am.replace(" ", "")
			if "psg" in hm:
				hm = hm.replace("psg", "paris")
			if "psg" in am:
				am = am.replace("psg", "paris")
			
			#print("select * from bookmark matches where home_team like "+home_match+" or home_team like "+hm+" or home_team like "+home_prev+"")
			home_match = "%"+home_match+"%"
			away_match = "%"+away_match+"%"
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
			try:
				prev_match_t = prev_match_t.replace(" ", "")
			except:
				pass
			
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
			cur.execute("select * from bookmark_matches where home_team like %s and away_team like %s or home_team like %s and away_team like %s or home_team like %s and away_team like %s or home_team like %s and away_team like %s",(home_prev,away_prev,home_match,away_match,hb,ab,hm,am,))
			#cur.execute("SELECT * FROM bookmark_matches WHERE match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or home_team like %s or home_team like %s and away_team like %s or away_team like %s", (match, match_teams, match_d,match_t,prev_match,prev_match_d,prev_match_t,match_b,match_bb,home_prev,home_match,away_prev,away_match, ))
			markets = cur.fetchall()
			cur.execute("select * from bookmark_matches where match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s", (match, match_teams,match_d,match_t,prev_match,prev_match_d,prev_match_t,match_b,match_bb, ))
			marketss = cur.fetchall()
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
				if r not in market_odds:
					market_odds.append(r)
			for mk in other_markets:
				r = [mk[3],mk[4],mk[5]]
				if r not in market_odds:
					market_odds.append(r)
			for mk in marketss:
				if mk not in markets:
					markets.append(mk)
		except Exception as e:
			db.rollback();print(str(e))
			pass
		finally:
			db.close()
		
		if session.get("user") is not None:
			n = len(market_odds[0:5])
			ck = Combine(market_odds, session["user"])		
			#session["obj"] = ck		
			combinations = ck.get_list("~")
			combinations_p = ck.get_list("%")
			combinations_above = ck.get_list(">~")
			combinations_above_p = ck.get_list(">%")
			cm = ""
			for combination in combinations:
				cm = cm+"<div class='bets'><button>"+str(combination[0][0])+"</button><button>"+str(combination[0][1])+"</button><button>"+str(combination[0][2])+"</button><div class='res'>"+"{:.2f}".format(combination[1])+"</div></div>"
			cm_p = ""
			for combination in combinations_p:
				cm_p = cm_p + "<div class='bets'><button>"+str(combination[0][0])+"</button><button>"+str(combination[0][1])+"</button><button>"+str(combination[0][2])+"</button><div class='res'>"+"{:.2f}".format(combination[1])+"</div></div>"
			cma = ""
			for combination in combinations_above:
				cma = cma+"<div class='bets'><button>"+str(combination[0][0])+"</button><button>"+str(combination[0][1])+"</button><button>"+str(combination[0][2])+"</button><div class='res'>"+"{:.2f}".format(combination[1])+"</div></div>"
			cma_p = ""
			for combination in combinations_above_p:
				cma_p = cma_p+"<div class='bets'><button>"+str(combination[0][0])+"</button><button>"+str(combination[0][1])+"</button><button>"+str(combination[0][2])+"</button><div class='res'>"+"{:.2f}".format(combination[1])+"</div></div>"
			max_percent = ck.get_max()
			session["obj"] = max_percent
			lcm = len(combinations)
			lmm = len(combinations_above)
		return render_template("homematch.html", **locals())

@app.route("/bookmaker/match/<match>")
def getBookMarkets(match):
	if match:
		country = request.args.get("filter")
		max_percent = [[], 0]
		market_odds = []
		x = match.split("-")
		xeid = x[-1]
		#print(xeid)
		try:
			db = DBO()
			cur = db.cursor(buffered=True)
			cur.execute("SELECT * FROM bookmark_matches WHERE xeid=%s", (xeid,))
			matches = cur.fetchone()
			session["match"] = matches[1]
			match = matches[5]
			matchteams = match
			
			match = match.lower()
			prev_match = match
			mm = match
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
			if "paris saint germain" in match:
				match = match.replace("paris saint germain", "psg")
			
			
		
			#print(match)
			prev_match = prev_match.split("-")
			match_bd = prev_match
			hb = "%"+prev_match[0]+"%"
			ab = "%"+prev_match[1]+"%"
			home_prev = prev_match[0][0:3]
			home_prev = "%"+home_prev+"%"
			away_prev = prev_match[1][1:4]
			away_prev = "%"+away_prev+"%"
			home_match = match.split("-")[0][0:3]
			away_match = match.split("-")[1][1:4]
			hm = "%"+match.split("-")[0]+"%"
			am = "%"+match.split("-")[1]+"%"
			if " " in hm:
				hm = hm.replace(" ", "")
			if " " in am:
				am = am.replace(" ", "")
			if "psg" in hm:
				hm = hm.replace("psg", "paris")
			if "psg" in am:
				am = am.replace("psg", "paris")
			
			#print("select * from bookmark matches where home_team like "+home_match+" or home_team like "+hm+" or home_team like "+home_prev+"")
			home_match = "%"+home_match+"%"
			away_match = "%"+away_match+"%"
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
			try:
				prev_match_t = prev_match_t.replace(" ", "")
			except:
				pass
			
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
			cur.execute("select * from bookmark_matches where home_team like %s and away_team like %s or home_team like %s and away_team like %s or home_team like %s and away_team like %s or home_team like %s and away_team like %s",(home_prev,away_prev,home_match,away_match,hb,ab,hm,am,))
			#cur.execute("SELECT * FROM bookmark_matches WHERE match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or home_team like %s or home_team like %s and away_team like %s or away_team like %s", (match, match_teams, match_d,match_t,prev_match,prev_match_d,prev_match_t,match_b,match_bb,home_prev,home_match,away_prev,away_match, ))
			markets = cur.fetchall()
			cur.execute("select * from bookmark_matches where match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s or match_teams like %s", (match, match_teams,match_d,match_t,prev_match,prev_match_d,prev_match_t,match_b,match_bb, ))
			marketss = cur.fetchall()
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
				if r not in market_odds:
					market_odds.append(r)
			for mk in other_markets:
				r = [mk[3],mk[4],mk[5]]
				if r not in market_odds:
					market_odds.append(r)
			for mk in marketss:
				if mk not in markets:
					markets.append(mk)
		except Exception as e:
			db.rollback();print(str(e))
			pass
		finally:
			db.close()
		
		if session.get("user") is not None:
			n = len(market_odds[0:5])
			ck = Combine(market_odds, session["user"])	
			#session["obj"] = ck			
			combinations = ck.get_list("~")
			combinations_p = ck.get_list("%")
			combinations_above = ck.get_list(">~")
			combinations_above_p = ck.get_list(">%")
			cm = ""
			for combination in combinations:
				cm = cm+"<div class='bets'><button>"+str(combination[0][0])+"</button><button>"+str(combination[0][1])+"</button><button>"+str(combination[0][2])+"</button><div class='res'>"+"{:.2f}".format(combination[1])+"</div></div>"
			cm_p = ""
			for combination in combinations_p:
				cm_p = cm_p + "<div class='bets'><button>"+str(combination[0][0])+"</button><button>"+str(combination[0][1])+"</button><button>"+str(combination[0][2])+"</button><div class='res'>"+"{:.2f}".format(combination[1])+"</div></div>"
			cma = ""
			for combination in combinations_above:
				cma = cma+"<div class='bets'><button>"+str(combination[0][0])+"</button><button>"+str(combination[0][1])+"</button><button>"+str(combination[0][2])+"</button><div class='res'>"+"{:.2f}".format(combination[1])+"</div></div>"
			cma_p = ""
			for combination in combinations_above_p:
				cma_p = cma_p+"<div class='bets'><button>"+str(combination[0][0])+"</button><button>"+str(combination[0][1])+"</button><button>"+str(combination[0][2])+"</button><div class='res'>"+"{:.2f}".format(combination[1])+"</div></div>"
			max_percent = ck.get_max()
			session["obj"] = max_percent
			lcm = len(combinations)
			lmm = len(combinations_above)
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
