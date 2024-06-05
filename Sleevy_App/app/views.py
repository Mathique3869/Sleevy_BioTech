
from app import app, db
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app.models import Coach, Player, Charts
from threading import Thread
import base64
from datetime import datetime
from sqlalchemy import desc
from PIL import Image
from io import BytesIO
import os
import requests


@app.route('/')
def index():
    return render_template('main.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/add', methods=['POST'])
def add_data():
    type = request.json['type']
    charts64 = request.json['charts64']
    new_data = Charts(type=type, charts64=charts64)
    db.session.add(new_data)
    db.session.commit()


@app.route('/graph/<username>')
def create_charts(username):
    # Gestion des charts de type EMG
    emg = Charts.query.filter_by(type="EMG").order_by(desc(Charts.id)).first()
    if emg:
        emgb64 = emg.charts64
        catemg = emg.type
        imgemg = base64.b64decode(emgb64)
        imageemg = Image.open(BytesIO(imgemg))
        date = datetime.now().strftime("%d_%m_%Y_%Hh%M")
        imageemg.save("C:/Users/achil/Desktop/Entrainement/" +
                      username + "_" + catemg + "_" + date + ".png")
    else:
        print("Aucun enregistrement de type 'EMG' trouvé")

    # Gestion des charts de type PPG
    ppg = Charts.query.filter_by(type="PPG").order_by(desc(Charts.id)).first()
    if ppg:
        ppgb64 = ppg.charts64
        catppg = ppg.type
        imgppg = base64.b64decode(ppgb64)
        imageppg = Image.open(BytesIO(imgppg))
        date = datetime.now().strftime("%d_%m_%Y_%Hh%M")
        imageppg.save("C:/Users/achil/Desktop/Entrainement/" +
                      username + "_" + catppg + "_" + date + ".png")
    else:
        print("Aucun enregistrement de type 'PPG' trouvé")
    
    return redirect(url_for('players'))


@app.route('/register_coaches', methods=['POST'])
def register_coaches():
    form = request.form
    new_coach = Coach(
        username=form['username'],
        game=form['game']
    )
    new_coach.set_password(form['password'])
    db.session.add(new_coach)
    db.session.commit()

    coach = Coach.query.filter_by(username=form['username']).first()
    if coach:
        session['coach'] = coach.id
        return redirect(url_for('players'))
    else:
        return redirect(url_for('register'))


@app.route('/login_coaches', methods=['POST'])
def login_coaches():
    form = request.form
    coach = Coach.query.filter_by(username=form['username']).first()
    if not coach:
        return redirect(url_for('login'))
    if coach.check_password(form['password']):
        session['coach'] = coach.id
        return redirect(url_for('players'))
    else:
        return redirect(url_for('login'))


@app.route('/players', methods=['POST', 'GET'])
def players():
    coach_id = None
    if session['coach']:
        coach_id = session['coach']
        players = Player.query.filter_by(coach_id=coach_id)
        return render_template('players.html', players=players)
    return render_template('players.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('coach', None)
    return redirect(url_for('index'))


@app.route('/register_player', methods=['POST'])
def register_player():
    form = request.form
    username = form['username']
    new_player = Player.query.filter_by(username=username).first()
    if not new_player:
        new_player = Player(
            username=form['username'],
            game=form['game'],
            coach_id=session['coach'],
        )
        db.session.add(new_player)
        db.session.commit()
        return redirect(url_for('players'))
    else:
        return redirect(url_for('players'))


@app.route('/rec_start')
def rec_start():
    try:
        response = requests.get('http://192.168.190.172:5000/startrec')
        if response.status_code == 200:
            print(response.text)
            return redirect(url_for('players'))
        else:
            return "Erreur lors de la requête au serveur Raspberry Pi"
    except requests.exceptions.RequestException as e:
        return f"Erreur lors de la requête au serveur Raspberry Pi : {e}"
    

@app.route('/rec_stop')
def rec_stop():
    try:
        response = requests.get('http://192.168.190.172:5000/stoprec')
        if response.status_code == 200:
            print(response.text)
            return redirect(url_for('players'))
        else:
            return "Erreur lors de la requête au serveur Raspberry Pi"
    except requests.exceptions.RequestException as e:
        return f"Erreur lors de la requête au serveur Raspberry Pi : {e}"

