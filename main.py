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
import json
import sqlite3
app = Flask(__name__)
app.secret_key = 'app@Betting'

is_prod = os.getenv('IS_HEROKU')
complete = 0
print(is_prod)
try:
	conn = sqlite3.connect('sure-bet.sqlite3')
	#conn.execute('CREATE TABLE IF NOT EXISTS user_combination("id" INTEGER PRIMARY KEY AUTOINCREMENT,user VARCHAR(500), odd_one VARCHAR(100) , odd_two VARCHAR(100)  ,odd_three VARCHAR(100) , result VARCHAR(100) , time TIMESTAMP default current_timestamp,book_one VARCHAR(100) ,book_two VARCHAR(100),book_three VARCHAR(100)')
	conn.execute("""CREATE TABLE IF NOT EXISTS user_combination (id INTEGER PRIMARY KEY, user VARCHAR(500),match TEXT, odd_one VARCHAR(100) , odd_two VARCHAR(100)  ,odd_three VARCHAR(100) , result VARCHAR(100) , time TIMESTAMP default current_timestamp,book_one VARCHAR(100) NULL,book_two VARCHAR(100) NULL,book_three VARCHAR(100) NULL)""")
	conn.close()
except Exception as e:
	print(str(e))
	


def get_code():
	pass

def DBO():
	"""
	try:
		db = mysql.connector.connect(host="localhost",    # your host, usually localhost
		     user="root",         # your username
		     passwd="root",  # your password
		     db="askabcry_betting")
		return db
	except Exception as e:
		print(str(e))
		pass
	
	"""
	for i in range(1,7):
		try:
			db = mysql.connector.connect(host="192.185.81.65",    # your host, usually localhost
			     user="askabcry_root",         # your username
			     passwd="tryhackmeanddie",  # your password
			     db="askabcry_bets")
			break
		except Exception as e:
			print(str(e))
			pass



	return db
	#"""
def getRand(vals):
	return random.choice(vals)

def getPower(n):
	
	return n*n*n

def calc(a, b, c):
	
	return (1/a)+(1/b)+(1/c)


class Combine:
	def __init__(self, markets, booklist,match):
		self.user  = session.get("user")
		self.match = match
		self.combination = []
		self.combination_p= []
		self.combination_above = []
		self.combination_above_p = []
		self.book_list = booklist
		self.markets = []
		for m in markets:
			if m not in self.markets:
				self.markets.append(m)
		#print(markets)
		#print(self.book_list)
		self.min_odds = []
		self.min_percent = 1000
		self.markets = markets
		self.cnt = 0
		#print(match)
		self.getCombinations(self.markets)	
		
		if len(self.max_odds) > 0:
			
			self.add_database([self.max_percent,self.max_odds], "one")
		else:
			self.add_database([self.max_percent,[0,0,0]], "")

	def add_database(self,vals,m):
		if m == "":
			try:
				db = sqlite3.connect('sure-bet.sqlite3')
				cur = db.cursor()
				cur.execute("insert into user_combination(user,match,odd_one,odd_two,odd_three,result) values(?,?,?,?,?,?)",[self.user,self.match,str(vals[1][0]),str(vals[1][1]),str(vals[1][2]),str(vals[0])])
				
			except Exception as e:
				db.rollback()
				print(str(e))
				pass
			finally:
				db.commit()
				db.close()
		if m == "one":
			try:
				db = sqlite3.connect('sure-bet.sqlite3')
				cur = db.cursor()
				cur.execute("select * from user_combination where user=? and match=?",[self.user,self.match])
				exs = cur.fetchone()
				if exs:
					pass
				else:
					cur.execute("insert into user_combination(user,match,odd_one,odd_two,odd_three,result) values(?,?,?,?,?,?)", [self.user,self.match,str(vals[1][0]),str(vals[1][1]),str(vals[1][2]),str(vals[0])])
				
			except Exception as e:
				db.rollback()
				print(str(e))
				pass
			finally:
				db.commit()
				db.close()
			used = []
			db = sqlite3.connect('sure-bet.sqlite3')
			cur = db.cursor()
			for book_list in self.book_list: 
				#print(book_list)
				try:
					if db == None:
						db = sqlite3.connect('sure-bet.sqlite3')
						cur = db.cursor()
					book = book_list[3]
					try:
						book = book_list[3].split("-")[0]
					except:
						pass
					if book:
						#if 'sportybet.com' in book or 'dafabet.com' in book or 'betsafe.com' in book or 'betking.com' in book:
						cur.execute("select * from user_combination where result != 0 and result != '0' and book_one is null or book_two is null or book_three is null")
						cnt = cur.fetchone()
						if cnt:
							pass
						else:
							break
						cur.execute("update user_combination set book_one = ? where odd_one like ? and match=? and user=?", [book, "%"+book_list[0]+"%",self.match,self.user])
						
						cur.execute("update user_combination set book_two = ? where odd_two like ? and match=? and user=?", [book, "%"+book_list[1]+"%",self.match,self.user])
						
						cur.execute("update user_combination set book_three = ? where odd_three like ? and match=? and user=?", [book, "%"+book_list[2]+"%",self.match,self.user])
						used.append(book)
					
				except Exception as e:
					db.rollback()
					print(str(e))
					pass
				finally:
					db.commit()
					#db.close()
			#db.close()
			#print(used)	
	def getCombinations(self,ms):
		count = 0
		self.max_percent = 0
		self.max_odds = []
		ls = ms
		l = ls
		ls = []
		cn = getPower(len(l))
		sz = 0
		while sz <= 3000:
			#print(sz)
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
				sz = sz+1
				try:
					
					res = []
					a = x
					b = y
					c = z
					val = calc(float(a[0:3]),float(b[0:3]),float(c[0:3]))
					#print(val)
					if val <= 1:
						
						#print(100-(val*100))
						
						p = val*100
						if 100-p >= self.max_percent:
							print("here = "+str(val))
							self.max_percent = 100-p
							self.max_odds = m
						#print(self.markets)
						#print(self.max_percent)
						#print(self.max_odds)
					
					
				except Exception as e:
					print(str(e))
					pass
		#print(ls)
			
		
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
	
	def get_max(self):
		return [self.max_odds,self.max_percent]
	def get_min(self):
		return [self.min_odds,self.min_percent]	
	
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

def get_list(user):
	try:
		db = sqlite3.connect('sure-bet.sqlite3')
		cur = db.cursor()
		cur.execute("select odd_one,odd_two,odd_three,result,book_one,book_two,book_three,match from user_combination where user=? and result != '0' and result != 0 ",[user])#and book_one is not null and book_two is not null and book_three is not null
		odds = cur.fetchall()
		#"""
		if len(odds) == 0:
			#cur.execute("select odd_one,odd_two,odd_three,result,book_one,book_two,book_three,match from user_combination where user=?",[user])
			#odds = cur.fetchall()
			odds = 0
		#"""
		return odds
	except Exception as e:
		db.rollback()
		print(str(e))
		pass
	finally:
		db.close()

def best_today():
	pass
def get_odds():
	try:
		db = DBO()
		cur = db.cursor(buffered=True)
		#cur.execute("select home_odd,draw_odd,away_odd,result,home_odd,draw_odd,away_odd from home_matches")
		
		cur.execute("select home_odd,draw_odd,away_odd,result,home_odd,draw_odd,away_odd,xeid from home_matches")
		odds = cur.fetchall()
		return odds
	except Exception as e:
		db.rollback()
		print(str(e))
		pass
	finally:
		db.close()

def workMatch():
	pass
def get():
	url = 'http://ipinfo.io/json'
	response =  requests.request("GET", url)
	r = response.text
	data = json.loads(r)

	IP=data['ip']
	org=data['org']
	city = data['city']
	country=data['country']
	region=data['region']

	return country

@app.route("/api/request/<mode>")
def api(mode):
	if mode == "nextPage":
		if request.method == "POST":
			pass

@app.route("/")
def home():
	#country = get()
	country = "KE"
	if country != "KE" or country != "NG" or country != "AL":
		country = "KE"
	session["country"] = country
	return redirect("/home/"+str(country)+"/?page=1")

@app.route("/home/<md>/", methods=['GET'])
def land(md):
	#print(session.get("user"))
	#"""
	if md == None:
		return redirect("/")

	country = md
	page = request.args.get("page")
	if page == None:
		page = "1"
		session["page"] = page
	else:
		try:
			page = int(page)
			page = str(page)
			session["page"] = page
		except:
			pass
	if md != session["country"]:
		session["country"] = md
		page = "1"
		session["page"] = page
		#refresh = None
	print(session["country"])
	match_list = []
	league = request.args.get("league")
	if league != session.get("league") and league != None: 
		session["league"] = league
	#league = session.get("league")
	count = request.args.get("filter")
	
	if page != None and session.get("user") != None:
		try:
			db = sqlite3.connect('sure-bet.sqlite3')
			cur = db.cursor()
			cur.execute("delete from user_combination where user=?", [session["user"]])
		except Exception as e:
			db.rollback()
			print(str(e))
			pass
		finally:
			db.commit()
			db.close()
		"""
		if league == None:
			return redirect("/home/"+session["country"])
		else:
			return redirect("/home/"+session["country"]+"/?league="+league)
		
	if league != None:
		try:
			db = sqlite3.connect('sure-bet.sqlite3')
			cur = db.cursor()
			cur.execute("delete from user_combination where user=?", [session["user"]])
		except Exception as e:
			db.rollback()
			print(str(e))
			pass
		finally:
			db.commit()
			db.close()
	"""	
	if count != None:
		country = count
	time_filter = request.args.get("time")
	if session["page"] != None:	
		print(session["page"])
		page = session["page"]
		try:
			db = DBO()
			cur = db.cursor(buffered=True)
			if league != None:
				cur.execute("select xeid,match_teams from home_matches where league like %s",("%"+league+"%",))
				matchs = cur.fetchall()
			else:
				cur.execute("select xeid,match_teams from home_matches")
				matchs = cur.fetchall()

			if page == "1":
				matchs = matchs[0:5]
			elif page == "2":
				matchs = matchs[6:11]
			elif page == "3":
				matchs = matchs[12:18]
			elif page == "4":
				matchs = matchs[19:27]
			elif page == "5":
				matchs = matchs[28:34]
			elif page == "6":
				matchs = matchs[35:41]
			elif page == "7":
				matchs = matchs[42:48]
			elif page == "8":
				matchs = matchs[49:55]
			elif page == "9":
				matchs = matchs[56:62]
			elif page == "10":
				matchs = matchs[63:69]
			elif page == "11":
				matchs = matchs[70:76]
			elif page == "12":
				matchs = matchs[77:83]
			else:
				matchs = matchs[84:90]
			print(len(matchs))
		except Exception as e:
			print(str(e))
			pass
		finally:
			db.close()	
	try:
		db = sqlite3.connect('sure-bet.sqlite3')
		cur = db.cursor()
		if session.get("user") == None:
			cur.execute("select count(id) from user_combination where user=?",["korg"])
		else:
			cur.execute("select count(id) from user_combination where user=?",[session["user"]])
		count = cur.fetchone()[0]
		
		if count == 0 or count == '0':
			#print(matchs)
			lis = MatchData(matchs,session["country"])
			match_list = lis.get_data()[0:6]
			
			book_list = lis.get_books()[0:6]
			#print(book_list)
	except Exception as e:
		print(str(e))
		pass
			
	
	if len(match_list) > 0 and len(book_list) > 0 and session.get("user") != None:
		try:
			db = sqlite3.connect('sure-bet.sqlite3')
			cur = db.cursor()
			cur.execute("delete from user_combination where user=?", [session["user"]])
		except Exception as e:
			db.rollback()
			print(str(e))
			pass
		finally:
			db.commit()
			db.close()
		
		count = 0
		for book in book_list:
			
			count = count +1
			match_l = []
			
			for i in range(0,len(book[0])):

				match_l.append(book[0][i-1][0:3])
			#print(book[0])
			ck = Combine(match_l,book[0],book[1])
		
	if session.get("user") != None:
		combinations = get_list(session["user"])
		if combinations == 0:
			s = session["page"]
			if int(s) >= 14:
				return redirect("/home/"+session["country"]+"/na")
			s = int(s)+1	
			
			if league == None:
				if s > 13:
					s = 14
				return redirect("/home/"+session["country"]+"/?page="+str(s))	
			else:
				if s > 13:
					s = 1
					return redirect("/home/"+session["country"]+"/?page="+str(s))
				return redirect("/home/"+session["country"]+"/?league="+league+"&&page="+str(s))		
			#return redirect()
		#best_today = best_today(session["user"])
	else:
		combinations = get_odds()
	matches = []
	
	
	try:
		db = DBO()
		cur = db.cursor(buffered=True)
		for m in combinations:
			cur.execute("SELECT * FROM home_matches where xeid=%s", (m[7], ))
			matches.append(cur.fetchone())
	except Exception as e:
		print(str(e))
		pass
	finally:
		db.close()
	
	#print(combinations)
	#print(matches)
	"""
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
	"""
	#matches = []
	return render_template("home.html", **locals())

@app.route("/home/<md>/na")
def noMatch(md):
	if md:
		page = request.args.get("page")
		if page != None:
			return redirect("/home/"+session["country"]+"/?page=1")	
		return render_template("nomatch.html")
@app.route("/calculator")
def getCalc():
	match = request.args.get("match")
	cal = request.args.get("cal")
	if match == None:
		return """
			<div class="t-ody" style="position: relative;background: black;height: 60px;">
				<h2 style="position: absolute;left: 2%;color: yellow;" onclick="location.href='/'">SureBet</h2><br>

				<div style="float: right;color: white;"><a href='/?login' style="margin-left: 10px;">Login</a><a style="margin-left: 20px;">Signup</a></div>
				
				</div><br><center>Select A <a href='/'>match</a> to perfom calculations</center>
				"""
	if session.get("user") != None:
		if cal != None:
			odds = session["odds1"]
		else:
			odds = session["odds"]
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
	bookmarks = []
	if session.get("country") != None:
	
		try:
			db = DBO()
			cur = db.cursor(buffered=True)
		
			cur.execute("select bookmark from bookmark_matches where {0}=1".format(session["country"]))
			books = cur.fetchall()
			for book in books:
				book = book[0].split("-")[0]
				if book not in bookmarks:
					bookmarks.append(book)
		except Exception as e:
			print(str(e))
			pass
		finally:
			db.close()
	try:
		db = DBO()
		cur = db.cursor(buffered=True)
		cur.execute("select * from top_leagues where is_active=1")
		leagues = cur.fetchall()
		cur.execute("select * from bookmarks where is_active=1")
		bookmakers = cur.fetchall()
	except Exception as e:
		print(str(e))
		pass
	finally:
		db.close()
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
			cur.execute("SELECT * FROM bookmark_matches where bookmark like %s and match_teams LIKE %s", (bk, match, ))
			home_matches = cur.fetchall()
			
			matches = home_matches
		except Exception as e:
			db.rollback();print(str(e))
			pass
		finally:
			db.close()
	elif book != None:
		old_book = book+"-football"
		book = "%"+book+"%"
		bk = "%"+book+"%"
		query = request.args.get("type")
		query = "%"+query+"%"
		if query != None and query != "%%":
			query = "%"+query+"%"
			try:
				db = DBO()
				cur = db.cursor(buffered=True)
				
				home_matches = []
				cur.execute("SELECT * FROM bookmark_matches WHERE bookmark like %s and match_teams like %s or  bookmark like %s and home_team like %s or  bookmark like %s and away_team like %s", (bk, query,bk, query,bk,query, ))
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
				
				home_matches = []
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
			if matches:
				#session["match"] = matches[1]
				match = matches[5]
			else:
				match = "NOT - FOUND"
				#session-match["match"]
			matchteams = match
			
			match = match.lower()
			prev_match = match
			match_check = match.split("-")
			if "atl" in match:
				match = match.replace("atl", "atletico")
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
			if "fc" in match:
				match = match.replace("fc", "")
			if "psg" in match:
				match = match.replace("psg", "paris ")
			if "man" in match:
				match = match.replace("man", "manchester")
			if "mun" in match:
				match = match.replace("mun", "manchester")
			if "mnc" in match:
				match = match.replace("mnc", "manchester")
			
			#print(match)
			prev_match = prev_match.split("-")
			match_bd = prev_match
			hb = "%"+prev_match[0]+"%"
			ab = "%"+prev_match[1]+"%"
			home_prev = prev_match[0][0:6]
			home_prev = "%"+home_prev+"%"
			away_prev = prev_match[1][1:4]
			away_prev = "%"+away_prev+"%"
			home_match = match.split("-")[0][0:6]
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
			prev_match_t = "%"+prev_match[0].replace(" ", "")+"-"+prev_match[-1][0:3]+"%"
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
			
		except Exception as e:
			db.rollback();print(str(e))
			pass
		finally:
			db.close()
		
		
		return render_template("homematch.html", **locals())

class MatchData:
	def __init__(self,matchs,country):
		self.country = country
		self.user = session["user"]
		self.matches = matchs
		self.market_odds = []
		self.book_list = []
		for match in self.matches:
			#print(match[1])		
			if "Home" not in match[1]:
				self.reloadOne(match[0],match[1])
		
			
	def get_books(self):
		return self.book_list
	def get_data(self):
		return self.market_odds
	def Checkmatch(self,match):
		
		if "atl" in match:
				match = match.replace("atl", "atletico")
		if "wolverhampton" in match:
			match = match.replace("wolverhampton", "wolves")
		if "utd" in match:
			match = match.replace("utd", "united")
		if "wanderers" in match:
			match = match.replace("wanderers", "")
		
		if "lfc" in match:
			match = match.replace("lfc", "")	
		if "fc" in match:
			match = match.replace("fc", "")
		if "psg" in match:
			match = match.replace("psg", "paris ")
		if "sg" in match:
			match = match.replace("sg", "saint germain")
		if "manchester" in match:
			match = match.replace("manchester","man")
		if "man." in match:
			match = match.replace("man.", "man")
		if "1." in match:
			match = match.replace("1.","")
		if "mun" in match:
			match = match.replace("mun", "manchester")
		if "mnc" in match:
			match = match.replace("mnc", "manchester")
		return match

	def reloadOne(self,xeid,match):
		#print(match)
		match = match.lower()
		try:
			prevmatch = match.split("-")
			home_t = prevmatch[0]
			away_t = prevmatch[-1]
			match = self.Checkmatch(match)
			match = match.split("-")
			
			home_h = match[0]
			away_h = match[-1]
			home = prevmatch[0][1:6]
			away= prevmatch[-1][1:7]
			home_team = match[0][1:6]
			away_team = match[-1][1:7]
			home = "%"+home+"%"
			away = "%"+away+"%"
			home_team = "%"+home_team+"%"
			away_team = "%"+away_team+"%"
			home_t = "%"+home_t+"%"
			away_t = "%"+away_t+"%"
			home_h = "%"+home_h+"%"
			away_h = "%"+away_h+"%"
			try:
				
				db = DBO()
				cur = db.cursor(buffered=True)
				cur.execute("select home_odd,draw_odd,away_odd,bookmark FROM bookmark_matches where {0}=1 and home_team like %s and away_team like %s and home_odd != '-' and draw_odd !='-' and away_odd !='-' or {0}=1 and home_team like %s and away_team like %s and home_odd != '-' and draw_odd !='-' and away_odd !='-' or {0}=1 and home_team like %s and away_team like %s and home_odd != '-' and draw_odd !='-' and away_odd !='-' or {0}=1 and home_team like %s and away_team like %s and home_odd != '-' and draw_odd !='-' and away_odd !='-'".format(self.country),(home,away,home_team,away_team,home_t,away_t,home_h,away_h,))
				bookmarks = cur.fetchall()
				#cur.execute("SELECT home_odd,draw_odd,away_odd,bookmark FROM bookmark_matches where home_team like %s and away_team like %s or home_team like %s and away_team like %s or home_team like %s and away_team like %s or home_team like %s and away_team like %s ",(home,away,home_team,away_team,home_t,away_t,home_h,away_h,))
				#bookmarks = cur.fetchall()
				
				if bookmarks:
					for book in bookmarks:
						if book[0:3] not in self.market_odds:
							self.market_odds.append([book[0:3],xeid])
						if book not in self.book_list:
							self.book_list.append([bookmarks,xeid])
					
				
				#print(bookmarks)
				#print(self.book_list[0])
			except Exception as e:
				db.rollback();print(str(e))
				pass
			finally:
				db.close()
		except Exception as e:
			print(str(e))
			pass
		
	

@app.route("/bookmaker/reload",methods=['GET','POST'])
def refresh():
	global complete 
	if request.method == "POST" and complete == 0:
		complete = 1
		try:
			db = DBO()
			cur = db.cursor(buffered=True)
			cur.execute("SELECT * FROM home_matches")
			matches = cur.fetchall()
			match = MatchData(matches)
			ck = Combine(market_odds, session["user"])	
			combinations = ck.get_list()	
			#for match in matches:
				
			n = len(markets)
		except Exception as e:
			db.rollback();print(str(e))
			pass
		finally:
			db.close()
		msg = "Refresh Completed"
	return render_template("reload.html",**locals())

@app.route("/markets")
def getMarkets():
	
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
			if "man" in match:
				match = match.replace("man", "manchester")
			
			
		
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
		
		except Exception as e:
			db.rollback();print(str(e))
			pass
		finally:
			db.close()
		
		
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
	app.run(host="0.0.0.0", port=8080, debug=True)
