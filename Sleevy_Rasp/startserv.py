import RecPPGEMG
from flask import Flask
from globals import stop_event
app = Flask(__name__)

@app.route('/')
def index():
    return 'Où était le Gondor lorsque le Westfold est tombé ?'

@app.route('/startrec')
def startrec():
    stop_event.clear()
    RecPPGEMG.all()
    return '1'

@app.route('/stoprec')
def stoprec():
    stop_event.set()
    return '1'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
