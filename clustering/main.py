#Roopam Sharma
#Machine Learning (K-means clustering)

from flask import Flask, render_template, request,session
from werkzeug import secure_filename
#import sqlite3 as sql
import MySQLdb as sql
import pandas as pd
import numpy as np
from datetime import datetime,timedelta
from sklearn.cluster import KMeans
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot
import os,math
import time,datetime
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


con = sql.connect(host=hostname,port=dbport,user=username,passwd=passwd,db=db)
cur = con.cursor()
cur.execute("create table if not exists TestTable(pclass int,survived int,name varchar(255),sex varchar(10),age decimal(4,2),sibsp int,parch int,ticket varchar(20),fare decimal(4,2),cabin varchar(10),embarked char(1),boat varchar(5),body varchar(5),home_dest varchar(50))")
con.commit()
port = int(os.getenv('PORT', 8000))

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'arandomstring'

@app.route('/')
def home():
   return render_template('home.html')

@app.route('/clust')
def clust():
   return render_template('clust.html')

@app.route('/clust1')
def clust1():
   return render_template('clust1.html')  

@app.route('/clust2')
def clust2():
   return render_template('clust2.html')     
   
@app.route('/upload')
def upload():
   return render_template('upload.html')
   
@app.route('/search')
def search():
   return render_template('search.html')   

@app.route('/insertdata',methods=['POST','GET'])
def insertdata():
   s = time.time()
   file = request.files["csvfile"]
   filename = secure_filename(file.filename).strip()
   session['upload'] = filename
   #Saving file in uploads folder
   file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename.strip()))
   #con = sql.connect('database.db')
   con = sql.connect(host=hostname,port=dbport,user=username,passwd=passwd,db=db)
   df = pd.read_csv(app.config['UPLOAD_FOLDER']+filename)
   #df = pd.read_excel(app.config['UPLOAD_FOLDER']+filename,sheet_name=0)
   #saving df to sqlite database
   #df.to_sql('TestTable', con, schema=None, if_exists='replace', index=True, index_label=None, chunksize=None, dtype=None)
   #csv_size = os.stat(app.config['UPLOAD_FOLDER']+filename).st_size
   df = df.replace(np.nan,'',regex=True)
   data = [tuple(i) for i in df.values]
   print(data)
   cur = con.cursor()
   cur.executemany(
      """INSERT INTO TestTable (pclass,survived,name,sex,age,sibsp,parch,ticket,fare,cabin,embarked,boat,body,home_dest)
      VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s,%s)""",data)
   app.config['UPLOAD_FOLDER']+filename
   con.commit()
   con.close()
   return render_template('home.html')

@app.route('/csvdata')
def csvdata():
   s = time.time()
   if 'upload' not in session:
	   return render_template('output.html',data = ['Please upload data'])
   #con = sql.connect('database.db')
   con = sql.connect(host=hostname,port=dbport,user=username,passwd=passwd,db=db)
   cur = con.cursor()
   cur.execute('select * from TestTable')
   rows = cur.fetchall()
   con.close()
   if len(rows)==0:
	   return render_template('output.html',data=['No data available'])
   e = time.time()
   print('Time Elapsed:',e-s)  
   return render_template('output.html',data = rows)  
   
@app.route('/clustering',methods=['POST','GET'])
def clustering():
   #con = sql.connect('database.db')
   con = sql.connect(host=hostname,port=dbport,user=username,passwd=passwd,db=db)
   cur = con.cursor()
   cur.execute('select * from TestTable')
   rows = cur.fetchall()
   df = pd.DataFrame(rows)
   X = df.iloc[:,[6,7]].dropna()
   colors = ['r','g','b','c','y','m','k', (0.5,0.3,0.5)]
   X = pd.DataFrame(X)
   c = int(request.form['clusts'])
   #Clustering the data
   kmeans = KMeans(n_clusters=c).fit(X)
   centers = pd.DataFrame(kmeans.cluster_centers_)
   labels = pd.DataFrame(kmeans.labels_)
   no_of_clusters = []
   #Plotting the clusters
   for i in range(c):
       pyplot.scatter([X.iloc[j,0] for j in labels.index[labels[0]==i].tolist()],[X.iloc[j,1] for j in labels.index[labels[0]==i].tolist()], c = colors[i%8])
       no_of_clusters.append(len(labels.index[labels[0]==i].tolist()))
       pyplot.scatter(centers.iloc[i,0],centers.iloc[i,1],label='Centroids'+str(i+1),c=colors[i%8],marker="X",s=80,edgecolors='k')
   pyplot.legend(loc='upper left')
   pyplot.xlabel('Age')
   pyplot.ylabel('Fare')
   pyplot.title('Clustering of the Data')
   ts = time.time()
   fig3 = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M%S')
   pyplot.savefig('static/plots/'+fig3)	
   pyplot.clf()
   #find distance between each centroid
   dist = findDistance(centers)
   return render_template('plot.html',data=[fig3+'.png',kmeans.cluster_centers_,no_of_clusters,dist])

@app.route('/clustering1',methods=['POST','GET'])
def clustering1():
   #con = sql.connect('database.db')
   con = sql.connect(host=hostname,port=dbport,user=username,passwd=passwd,db=db)
   cur = con.cursor()
   cur.execute('select * from TestTable')
   rows = cur.fetchall()
   df = pd.DataFrame(rows)
   print(request.form['par1'])
   print(request.form['par2'])
   X = df.iloc[:,[int(request.form['par1']),int(request.form['par2'])]].dropna()
   X.columns= ['0','1']
   colors = ['r','g','b','c','y','m','k', (0.5,0.3,0.5)]
   
   if request.form['par1']=='1':
       X.iloc[:,0] = X.iloc[:,0]/100
   if request.form['par2']=='1':
       X.iloc[:,1] = X.iloc[:,1]/100	   
   print(X) 	   
   
   c = int(request.form['clusts'])
   #Clustering the data
   kmeans = KMeans(n_clusters=c).fit(X)
   centers = pd.DataFrame(kmeans.cluster_centers_)
   labels = pd.DataFrame(kmeans.labels_)
   no_of_clusters = []
   #Plotting the clusters
   d = []
   for i in range(c):
       pyplot.scatter([X.iloc[j,0] for j in labels.index[labels[0]==i].tolist()],[X.iloc[j,1] for j in labels.index[labels[0]==i].tolist()], c = colors[i%8])
	   
       no_of_clusters.append(len(labels.index[labels[0]==i].tolist()))
       pyplot.scatter(centers.iloc[i,0],centers.iloc[i,1],label='Centroids'+str(i+1),c=colors[i%8],marker="X",s=80,edgecolors='k')
   pyplot.legend(loc='upper left')
   
   pyplot.title('Clustering of the Data')
   ts = time.time()
   fig3 = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M%S')
   pyplot.savefig('static/plots/'+fig3)	
   pyplot.clf()
   #find distance between each centroid
   dist = findDistance(centers)
   return render_template('plot.html',data=[fig3+'.png',kmeans.cluster_centers_,no_of_clusters,dist,d])

@app.route('/clustering3',methods=['POST','GET'])
def clustering3():
   #con = sql.connect('database.db')
   con = sql.connect(host=hostname,port=dbport,user=username,passwd=passwd,db=db)
   cur = con.cursor()
   cur.execute('select * from TestTable where Fare>=? and Fare<= ?',(request.form['r1'],request.form['r2']))
   rows = cur.fetchall()
   cur.execute('delete from TestTable where Fare>=? and Fare<= ?',(request.form['r1'],request.form['r2']))
   con.commit()
   con.close()
   return render_template('output.html',data=[rows[0:5],len(rows)])

@app.route('/searching',methods=['POST','GET'])
def searching():
   #con = sql.connect('database.db')
   con = sql.connect(host=hostname,port=dbport,user=username,passwd=passwd,db=db)
   cur = con.cursor()
   cur.execute('select * from TestTable where CabinNum=? or Lname = ?',(request.form['cabin'],request.form['lname']))
   rows = cur.fetchall()
   con.close()
   return render_template('output1.html',data=rows)
 
def findDistance(X):
   dist = []
   m,n = X.shape
   for i in range(m):
       for j in range(i+1,m):
           dist.append([(i,j),math.sqrt(sum((X.iloc[i,:]-X.iloc[j,:])**2))])
   return dist		   
         
if __name__ == '__main__':
   app.run(host='0.0.0.0', port=port,debug = True)
   #app.run(debug=True)	