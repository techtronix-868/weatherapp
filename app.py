from flask import Flask,request,render_template,session,redirect,Response
import sqlite3
import json
import requests
app= Flask(__name__)
app.secret_key="my secret key"
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/insertCity", methods=["GET","POST"])
def insertCity():
    if "username" in session:
        if request.method == "GET":
            param = request.args.to_dict()
        else:
            param = request.form.to_dict()
        y = param["city"]
        x = "/get/weather/"+y
        return redirect(x)
    else:
        return redirect('login')
@app.route("/logout")
def logout():
    session.pop("username",None)
    return redirect('login')
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="GET":
        return render_template("login.html")
    else:
        data = request.form.to_dict()
        conn = sqlite3.connect("weather.db")
        cur = conn.cursor()
        cur.execute("select * from user where email like '%s' and password like '%s'" % (data['username'],data['password']))
        if cur.fetchone() is None:
            return("username password doesn't match")
        session['username']=data['username']
        return "Logged In "+data['username']

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="GET":
        return render_template("register.html")
    else:
        data = request.form.to_dict()
        conn = sqlite3.connect("weather.db")
        cur = conn.cursor()
        # try:
        cur.execute('''
        CREATE TABLE IF NOT EXISTS user(name text, password text, email text PRIMARY KEY)
        ''')
        conn.commit()
        cur.execute("SELECT * FROM user WHERE email like '"+data['email']+"'")
        if cur.fetchone() is None:
            cur.execute("INSERT INTO user VALUES('%s','%s','%s')" % (data['name'],data['password'],data['email']))
            conn.commit()

        return str(data)

@app.route('/api/users',methods=["GET","POST"])
def userapi():
    conn = sqlite3.connect("weather.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM USER")
    user_data = cur.fetchall()
    user_dict = {"records":[]}
    for user in user_data:
        user_dict['records'].append(
            {"name":user[0],
            "password":user[1],
            "email":user[2]}
        )
    resp = json.dumps(user_dict,indent=2)
    return Response(response=resp,mimetype="application/json")

@app.route("/api/get/weather/<cityname>")
def apigetweather(cityname):
    params = {"q":cityname,"appid":"d95abc296b4b6a4e4c981a4b83bfa1de"}
    #print(params)
    response =  requests.get("https://api.openweathermap.org/data/2.5/weather",params=params)
    resp = response.json()
    #print(resp);
    resp = {"name":resp.get("name"),"condition":resp.get("weather")[0].get("description"),
    "temprature":resp.get("main").get("temp")}
    print(resp)
    resp['temprature'] = round(resp['temprature'] - 272.14,2)
    return Response(response=json.dumps(resp,indent=2),mimetype="application/json")  
@app.route("/get/weather/<cityname>")

def getweather(cityname):
    return render_template("getweather.html")

if __name__ == "__main__":
	app.run(host="0.0.0.0",debug=True)