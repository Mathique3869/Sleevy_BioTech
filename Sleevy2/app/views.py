from app import app, db
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app.models import Coach, Player
from threading import Thread
from pynput import keyboard
import os

@app.route('/')
def index():
    return render_template('main.html')


count = 0
stopped = True  
keyboard_listener = None

def start_keyboard_listener():
    global count, stopped
    count = 0  
    with open('count.txt', 'w') as file:
        file.write(str(count))

    def on_press(key):
        global count
        count += 1

    def on_release(key):
        pass  

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

   
    while stopped:
        pass

    print("Arrêt de l'écoute du clavier.")
    with open('count.txt', 'w') as file:
        file.write(str(count))

@app.route("/start_listen", methods=["POST"])
def start_listen():
    global stopped, keyboard_listener
    if keyboard_listener and keyboard_listener.is_alive():
        return jsonify({"message": "L'écoute du clavier est déjà en cours."})
    else:
        stopped = False
        keyboard_listener = Thread(target=start_keyboard_listener)
        keyboard_listener.start()
        return jsonify({"message": "L'écoute du clavier a démarré."})

@app.route("/stop_listen", methods=["POST"])
def stop_listen():
    global stopped
    stopped = True
    return jsonify({"message": "L'écoute du clavier a été arrêtée."})

@app.route("/get_count", methods=["GET"])
def get_count():
    global count
    return jsonify({"count": count})


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


def toggle_listen():
    global stopped, count
    if request.method == "POST":
        stopped = not stopped
        if stopped:
            print("Arrêt de l'écoute du clavier.")
        else:
            print("Reprise de l'écoute du clavier.")
        return jsonify({"message": "L'écoute du clavier a été arrêtée ou reprise."})
    else:
        with open('count.txt', 'r') as file:
            count = int(file.read())
        return jsonify({"count": count})

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



@app.route('/coach', methods=['POST', 'GET'])
def individual_coach():
    pseudo = request.form['name']
    game = request.form['game']
    prez="Bonjour " + pseudo + " vous jouez à " + game
    return prez


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


