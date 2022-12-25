from flask import Flask, render_template, request
from firebase_admin import credentials
from firebase_admin import db
import firebase_admin
import random
from datetime import date
import string

app = Flask(__name__)
app.debug = True

cred = credentials.Certificate("./amail-3dd96-firebase-adminsdk-aiuab-854aa11a67.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://amail-3dd96-default-rtdb.asia-southeast1.firebasedatabase.app'
})
data = db.reference()

def create(length=10):
    result = ""
    string_pool = string.ascii_letters + string.digits
    for i in range(length):
        result += random.choice(string_pool)
    return result


def upload(the_key):
    if the_key is None:
        return False
    else:
        data = db.reference('aMail/RandomKeys/')
        data.update({str(the_key): str(the_key)})
        return True

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logincheck', methods=['POST', 'GET'])
def logincheck():
    if request.method == 'POST':
        id = request.form['id']
        id = str(id)
        pw = request.form['password']
        pw = str(pw)
        data = db.reference().get()
        if id in data['aMail']['ID'] and data['aMail']['ID'][id].split('/')[1] == pw:
            return render_template('index2.html')
        else:
            return render_template("tryagain.html")

@app.route('/send', methods=['POST', 'GET'])
def send_mail():
    if request.method == 'POST':
        title = str(request.form['title']) #제목     
        poster = str(request.form['poster']) #메일아이디
        receiver = str(request.form['receiver']) #메일아이디 
        content = str(request.form['content']) #내용
        randomkey = create(10)
        data = db.reference().get()
        if data['aMail']['ID'][receiver] is not None and data['aMail']['ID'][poster]:
            today = date.today()
            today = today.strftime('%Y.%m.%d')
            upload(randomkey)
            ## 주어진 메일 아이디에 맞는 디코 아이디를 찾아야함
            poster_id = data['aMail']['ID'][poster].split('/')[0]
            receiver_id = data['aMail']['ID'][receiver].split('/')[0]
            mails = db.reference('aMail/Mails')
            mails.update({randomkey: {
                "Content": content,
                "From": f"{poster_id}/{poster}",
                "To": f"{receiver}/{receiver_id}",
                "Title": f"{title}",
                "WroteAt": f"{today}"
            }})
            
            return render_template("complete.html")
        else:
            return render_template('tryagain.html')


if __name__ == "__main__":
    app.run(host='127.0.0.1')