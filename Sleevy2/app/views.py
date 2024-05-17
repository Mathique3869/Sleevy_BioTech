
from app import app, db
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app.models import Coach, Player, Charts
from threading import Thread
import base64
from sqlalchemy import desc
from PIL import Image
from io import BytesIO
import os

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/add', methods=['POST'])
def add_data():
    type = request.json['type']
    charts64 = request.json['charts64']
    new_data = Charts(type=type, charts64=charts64)
    db.session.add(new_data)
    db.session.commit()
    
    
@app.route('/graph/<username>')
def create_charts(username):
    emg=Charts.query.order_by(desc(Charts.id)).first()
    emgb64=emg.charts64
    cat=emg.type
    img = base64.b64decode(emgb64)
    image = Image.open(BytesIO(img))
    image.save("C:/Users/achil/Desktop/Entrainement/"+username+"_"+cat+".png")
    flash("Les graphiques d'entrainement de "+username+" ont été créés ")
    return redirect(url_for('players'))


@app.route('/register_coaches', methods=['POST'])
def register_coaches():
    form= request.form
    new_coach= Coach(
        username=form['name'],
        game=form['game']
        
    )
    new_coach.set_password(form['password'])
    db.session.add(new_coach)
    db.session.commit()
    coach=Coach.query.filter_by(username=form['name']).first()
    if coach:
        coach_id=str(coach.id)
        return 'Bravo vous êtes enregistrez il est important de notez votre ID vous en aurez besoin pour vous connecter : ' + coach_id
    else:
        return "ERREUR"
    

@app.route('/login_coaches', methods=['POST'])
def login_coaches():
    form = request.form
    coach = Coach.query.filter_by(username=form['name']).first()
    if not coach:
        flash("Ce coach n'existe pas")
        return redirect(url_for('index'))
    if coach.check_password(form['password']):
        session['coach'] = coach.id
        return redirect(url_for('players'))
    else:
        flash('Le mot de passe est faux')
        return redirect(url_for('index'))


@app.route('/players', methods=['POST', 'GET'])
def players():
    coach_id=None
    if session['coach']:
        coach_id=session['coach']
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
    username= form['name']
    new_player =  Player.query.filter_by(username=username).first()
    if not new_player:
        new_player = Player(
            username = form['name'],
            game = form['game'],
            coach_id = session['coach'],
        )
        db.session.add(new_player)
        db.session.commit()
        flash('Le joueur à été ajouté avec succès')
        return redirect(url_for('players'))
    else:
        flash("Joueur déjà existant")
        return redirect(url_for('players'))


