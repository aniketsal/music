from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from flask import flash
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.externals import joblib
from sklearn.metrics import pairwise_distances
from scipy.spatial.distance import cosine
import numpy as np


app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'andya'

# Intialize MySQL
mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def pas():
    return render_template('index.html')


@app.route('/log', methods=['GET', 'POST'])
def past():
    return render_template('index.html')
# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        if account:
            user_id=account[0]
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM rating')
            kj=cursor.fetchall()
            a=[list(x) for x in kj]
            rating=np.zeros((200,200))
            for i in range(len(a)):
                rating[int(a[i][0])-1][int(a[i][1])-1]=a[i][2]
            n,m=rating.shape
            centeredcosine=np.zeros((n,m))
            uid=int(user_id)-1
            mean=(np.mean(rating,axis=1))
            for i in range(n):
                for j in range(m):
                    centeredcosine[i][j]=rating[i][j]-mean[i]
            dist_out = 1-pairwise_distances(centeredcosine, metric="cosine")
            np.fill_diagonal(dist_out,0)
            similarusers=np.argmax(dist_out[uid], axis=0)
            fsimilar=similarusers+1;
            sim_user_songid=[]
            cur_user_songid=[]
            final=[]
            #print(type(similarusers))
            for i in a:
                if int(i[0])==int(fsimilar):
                    sim_user_songid.append(i[1])
                if int(i[0])==user_id:
                    cur_user_songid.append(i[1])
            sim_user_songid = list(dict.fromkeys(sim_user_songid))
            cur_user_songid = list(dict.fromkeys(cur_user_songid))
            for i in sim_user_songid:
                if i not in cur_user_songid:
                    final.append(i)
            if final:
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT song_id,song_name FROM info WHERE song_id IN  %s',[final])
                j=cursor.fetchall()
                po="Recommendations for you"
                return render_template('playlist.html',li=j,id=user_id,po=po)
            else:
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT song_id,song_name FROM info WHERE song_id IN %s',[43,8,71,26,54,22,66,88,99,23,105,35,4])
                s=cursor.fetchall()
                return render_template('playlist.html',li=s,id=user_id,po="Recommendations for you")

        else:
            msg="Please provide valid credentials"
            return render_template('index.html',msg=msg)

   



# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', [username])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'This username already exists!'
            return render_template('register.html',msg=msg)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
            return render_template('register.html',msg=msg)
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
            return render_template('register.html',msg=msg)

        elif not username or not password or not email:
            msg = 'Please fill out the form!'
            return render_template('register.html',msg=msg)
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            t=(username, password, email)
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)',t)
            mysql.connection.commit()


            cursor.execute('SELECT id FROM accounts WHERE username = %s', [username])
            account = cursor.fetchone()
            if account:
                id=account['id']
            msg = 'You have successfully registered!'
            return render_template("check.html",id=id)#ye syntax yaad rakh bass abhi changes karke dekta mai
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html')


@app.route("/check", methods=['GET', 'POST'])
def check():
    #id=request.args.get('id')
    #return str(id)
    id = request.form["id"]
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #return str(id)
    if request.method=='POST' :
        
        msg=request.form.getlist('mycheckbox')
        #return str(msg)
        for m in msg:
            t=(id,m)
            #return str(id)
            cursor.execute('INSERT INTO user_genre VALUES (%s, %s)',t)
            mysql.connection.commit()
    #id=request.form["id"]
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT song_genre FROM user_genre WHERE user_id= %s',[id])
    a=cursor.fetchall()
    n=[list(k) for k in a]
    #return str(len(n))
    f=[]
    #return str(n[1][0])

    for i in range(len(n)):
        l=n[i][0].replace(" ","")
        f.append(l)
    #return str(f)
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT song_id,song_name FROM info WHERE song_genre IN  %s',[f])
    j=cursor.fetchall()
    l=[list(k) for k in j]
    #return str(l)



    return render_template('playlist.html',li=l,id=id)
    #return render_template('playlist.html',id=id)

@app.route("/player",methods=['GET','POST'])
def player():
    songid=request.form["songid"]
    user_id=request.form["id"]
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT song_name,song_artist,song_path FROM info WHERE song_id =  %s',[songid])
    m=cursor.fetchall()


    return render_template('player.html',name=m[0][0],artist=m[0][1],path=m[0][2],songid=songid,id=user_id)

@app.route("/dummy",methods=['GET','POST'])
def dummy():
    gs=request.form['id']
    return str(gs)
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT song_genre FROM user_genre WHERE user_id= %s',[gs])
    a=cursor.fetchall()
    n=[list(k) for k in a]
    #return str(len(n))
    f=[]
    #return str(n[1][0])

    for i in range(len(n)):
        l=n[i][0].replace(" ","")
        f.append(l)
    #return str(f)
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT song_id,song_name FROM info WHERE song_genre IN  %s',[f])
    j=cursor.fetchall()
    l=[list(k) for k in j]
    return render_template('playlist.html',li=l,id=gs)

@app.route("/now",methods=['GET','POST'])
def now():

    try:
        rat=int(request.form["rating"])
        songid=int(request.form["songid"])
        user_id=int(request.form["id"])
        #return str(user_id)
        name=request.form["songname"]
        path=request.form["path"]
        artist=request.form["artist"]
        t=(user_id,songid,rat)   
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO rating VALUES (%s, %s,%s)',t)

        mysql.connection.commit()

    except:
        pass
       
        
    
    #rat=int(request.form["rating"])
    songid=int(request.form["songid"])
    user_id=int(request.form["id"])
    #return str(user_id)
    name=request.form["songname"]
    path=request.form["path"]
    artist=request.form["artist"]
    '''
    t=(user_id,songid,rat)   
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO rating VALUES (%s, %s,%s)',t)

    mysql.connection.commit()
    '''
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM rating')
    kj=cursor.fetchall()
    a=[list(x) for x in kj]
    rating=np.zeros((200,200))
    for i in range(len(a)):
        rating[int(a[i][0])-1][int(a[i][1])-1]=a[i][2]
    n,m=rating.shape
    centeredcosine=np.zeros((n,m))
    uid=int(user_id)-1
    mean=(np.mean(rating,axis=1))
    for i in range(n):
        for j in range(m):
            centeredcosine[i][j]=rating[i][j]-mean[i]
    dist_out = 1-pairwise_distances(centeredcosine, metric="cosine")
    np.fill_diagonal(dist_out,0)
    similarusers=np.argmax(dist_out[uid], axis=0)
    fsimilar=similarusers+1;

    sim_user_songid=[]
    cur_user_songid=[]
    final=[]
    #print(type(similarusers))
    for i in a:
        if int(i[0])==int(fsimilar):
            sim_user_songid.append(i[1])

        if int(i[0])==user_id:
            cur_user_songid.append(i[1])

    sim_user_songid = list(dict.fromkeys(sim_user_songid))
    cur_user_songid = list(dict.fromkeys(cur_user_songid))
    for i in sim_user_songid:
        if i not in cur_user_songid:
            final.append(i)

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT song_id,song_name FROM info WHERE song_id IN  %s',[final])
    j=cursor.fetchall()
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT song_name,song_artist,song_path FROM info WHERE song_id =  %s',[songid])
    k=cursor.fetchall()
    po="Recommendations for you"
    if j:
        return render_template('player.html',name=k[0][0],artist=k[0][1],path=k[0][2],songid=songid,id=user_id,j=j,po=po)
    else:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT song_name,song_artist,song_path FROM info WHERE song_id IN %s',[1,8,71,26,54,22,66,88,99,23,105,35,4])
        s=cursor.fetchall()
        return render_template('player.html',name=k[0][0],artist=k[0][1],path=k[0][2],songid=songid,id=user_id,j=s,po=po)
    

@app.route("/genre",methods=['GET','POST'])
def genre():
    uid=request.form["id"]
    g=request.form["g"]
    if g=='1':
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT song_id,song_name FROM info')
        j=cursor.fetchall()
        l=[list(k) for k in j]
        po="All Songs"
    elif(g=='2'):
        cursor = mysql.connection.cursor()
        f='BollywoodSad'
        cursor.execute('SELECT song_id,song_name FROM info WHERE song_genre =  %s',[f])
        j=cursor.fetchall()
        l=[list(k) for k in j]
        po="Bollywood Sad"
    elif(g=='3'):
        cursor = mysql.connection.cursor()
        f='BollywoodRomantic'
        cursor.execute('SELECT song_id,song_name FROM info WHERE song_genre = %s',[f])
        j=cursor.fetchall()
        l=[list(k) for k in j]
        po="Bollywood Romantic"
    elif(g=='4'):
        cursor = mysql.connection.cursor()
        f='BollywoodDance'
        cursor.execute('SELECT song_id,song_name FROM info WHERE song_genre =  %s',[f])
        j=cursor.fetchall()
        l=[list(k) for k in j]
        po="Bollywood Dance"
    elif(g=='5'):
        cursor = mysql.connection.cursor()
        f='BollywoodDevotional'
        cursor.execute('SELECT song_id,song_name FROM info WHERE song_genre =  %s',[f])
        j=cursor.fetchall()
        l=[list(k) for k in j]
        po="Bollywood Devotional"
    else:
        cursor = mysql.connection.cursor()
        f='BollywoodMotivational'
        cursor.execute('SELECT song_id,song_name FROM info WHERE song_genre =  %s',[f])
        j=cursor.fetchall()
        l=[list(k) for k in j]
        po="Bollywood Motivational"
    return render_template('playlist.html',li=l,id=uid,po=po)



@app.route('/search', methods=['GET', 'POST'])
def search():
    uid=request.form["id"]
    song=request.form["book"]
    lsong="%" + song + "%"
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT song_id,song_name FROM info WHERE song_name LIKE %s OR song_movie LIKE %s',[lsong,lsong])
    exist = cursor.fetchall()
    if exist:
        q=[list(k) for k in exist]
        msg="Results"
        return render_template('playlist.html',li=q,id=uid,f1=msg)
    else:
        msg="OOPS! NO RESULTS FOUND"
        return render_template('playlist.html',f=msg)
    










if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

