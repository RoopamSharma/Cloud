from flask import Flask, render_template, request
import sqlite3 as sql
app = Flask(__name__)

import sqlite3
import base64
conn = sqlite3.connect('database.db')
#conn.execute('drop table people')
#conn.execute('CREATE TABLE people(name TEXT, grade integer ,room text, telnum TEXT, picture TEXT,keywords text)')
#conn.execute('drop table images')
#conn.execute('create table images(picture text, img blob)')					
# print("Opened database successfully")
# print("Table created successfully")
# conn.close()


@app.route('/')
def home():
   return render_template('home.html')

@app.route('/upload')
def new_student():
   return render_template('upload.html')
   
@app.route('/functions')
def func():
   return render_template('functions.html')

@app.route('/namesearch')
def search_by_name():
   return render_template('namesearch.html') 

@app.route('/gradesearch')
def search_by_grade():
   return render_template('gradesearch.html')
   
@app.route('/addpic')
def addpic():
   con = sql.connect("database.db") 	
   cur = con.cursor()
   cur.execute("select name from people")
   rows = cur.fetchall()   
   return render_template('addpic.html',msg = rows) 

@app.route('/deletepage')
def delpage():
   con = sql.connect("database.db") 	
   cur = con.cursor()
   cur.execute("select name from people")
   rows = cur.fetchall()   
   return render_template('deletepage.html',msg = rows)    

@app.route('/editpage')
def edtpage():
   con = sql.connect("database.db") 	
   cur = con.cursor()
   cur.execute("select name from people")
   rows = cur.fetchall()   
   return render_template('editpage.html',msg = rows)      
		
@app.route('/addcsv',methods = ['POST', 'GET'])
def addcsv():	
	if request.method == 'POST':
		try:
			fname = request.files.getlist("images")
			for i in range(len(fname)):
			    print(fname[i].filename)
			    readimg = fname[i]
			    img = readimg.read()
			    img = base64.b64encode(img)
			    con = sql.connect("database.db")
			    cur = con.cursor()
			    cur.execute("INSERT INTO images(picture,img) values(?,?)",(fname[i].filename.lower(),img))
			    con.commit()
			con.close()
			readfile = request.files["csvfile"]
			print(readfile)
			f_data = readfile.read().decode("utf-8")
			print(f_data)
			lines = f_data.split("\n")
			i = 0
			for line in lines:
				#Skipping the csv headers
				if i==0:
					i=1
					continue
				fields = line.split(",")
				if len(fields)<6:
					break
				with sql.connect("database.db") as con:
					cur = con.cursor()
					cur.execute("INSERT INTO people(name,grade,room,telnum,picture,keywords) VALUES (?,?,?,?,?,?)",(fields[0],int(fields[1].strip()),fields[2],fields[3],fields[4].lower(),fields[5].strip()))
					con.commit()
					msg = "Record successfully added"					
		except:
		    con.rollback()
		    msg =  "error in insert operation"
		finally:	
			return render_template("result.html",msg = msg)	
			con.close()
			
@app.route('/list')
def list():
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("select * from people")
   
   rows = cur.fetchall();
   return render_template("list.html",rows = rows)
   
@app.route('/display')
def display():
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("select * from images")
   
   rows = cur.fetchall()
   images = []
   for r in rows:
        r1 = {}
        r1['picture'] = r['picture']
        r1['img'] = r['img'].decode('utf-8')
        images.append(r1)
        print(r1['picture'])
   print(len(images))	
   return render_template("display.html",rows = images)

@app.route('/nsearch',methods = ['POST','GET'])   
def nsearch():
   con = sql.connect("database.db") 	
   cur = con.cursor()
   print(request.form['query'])
   cur.execute("select picture from people where name = ? ",(request.form['query'],))
   rows = cur.fetchall()
   if len(rows)==0:
       return render_template("searchresults.html",res = [request.form['query'],''])
   #print(rows[0])
   #print(rows[0][0])
   #print(str(rows[0][0]).lower())
   cur.execute("select img from images where picture = ? ",(str(rows[0][0]).lower(),))
   rows = cur.fetchall()
   if len(rows)==0:
       images = ''   
   else:
       print("Type")
       print(type(rows[0][0]))
       images = rows[0][0].decode('utf-8')
   print(len(images))
   return render_template("searchresults.html",res = [request.form['query'],images])

@app.route('/gsearch',methods = ['POST','GET'])   
def gsearch():
   con = sql.connect("database.db") 	
   cur = con.cursor()
   op = request.form['op']
   print(op)
   if op == 'lt':
       print("Started")
       cur.execute("select i.img from people p,images i where p.picture=i.picture and grade < ? ",(request.form['query'],))
   elif op== 'gt':
       cur.execute("select i.img from people p,images i where p.picture=i.picture and grade > ? ",(request.form['query'],))
   else:
       cur.execute("select i.img from people p,images i where p.picture=i.picture and grade = ? ",(request.form['query'],))
   rows = cur.fetchall()
   if len(rows)==0:
       return render_template("searchresults.html",res = [op,request.form['query'],''])
   images = []
   for row in rows:   
       images.append(row[0].decode('utf-8'))
   print(len(images))
   return render_template("gradeimages.html",res = [op,request.form['query'],images])

@app.route('/addimg',methods=['POST','GET'])
def addimg():
   con = sql.connect("database.db") 	
   cur = con.cursor()
   op = request.form['selName']
   readimg = request.files.get("images")
   fname = readimg.filename
   img = readimg.read()
   img = base64.b64encode(img)
   cur.execute("update people set picture = ? where name = ?",(fname.lower(),op))
   con.commit()
   cur.execute("select img from images where picture = ? ",(fname.lower(),))
   rows = cur.fetchall()
   print(rows)
   if len(rows)==0:
       cur.execute("insert into images(picture,img) values(?,?)",(fname.lower(),img))
       con.commit() 
   else:
       cur.execute("update images set img = ? where picture = ?",(img,fname.lower()))
       con.commit()
   con.close()
   return render_template("result.html",msg = "Data Updated successfully")	
   

@app.route('/delperson',methods=['POST','GET'])
def delperson():
   con = sql.connect("database.db") 	
   cur = con.cursor()
   cur.execute("select picture from people where name=?",(request.form['selName'],))
   rows = cur.fetchall()
   cur.execute("delete from people where name = ?",(request.form['selName'],))		    
   #con.commit()
   print(rows)
   cur.execute("delete from images where picture = ?",rows[0])		    
   con.commit()
   con.close()
   return render_template("result.html",msg = "Data Updated successfully")	
   
   
@app.route('/editfunc',methods=['POST','GET'])
def editfunc():
   con = sql.connect("database.db") 	
   cur = con.cursor()
   cur.execute("select * from people where name=?",(request.form['selName'],))
   rows = cur.fetchall()
   con.close()
   print(rows)
   return render_template("editperson.html",msg = rows)	
   
@app.route('/updatedata',methods=['POST','GET'])
def updatedata():
   con = sql.connect("database.db") 	
   cur = con.cursor()
   print("sh")
   print(request.form['name'])
   cur.execute("update people set grade = ?,room=?,telnum=?,keywords=? where name = ?",(request.form['grade'],request.form['room'],request.form['telnum'],request.form['keywords']),request.form['name'])
   con.commit()
   con.close()
   return render_template("result.html",msg = "Data Updated successfully")	
   
if __name__ == '__main__':
   app.run(debug = True)