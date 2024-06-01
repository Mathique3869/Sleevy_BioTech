import RecPPGEMG
from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'Où était le Gondor lorsque le Westfold est tombé ?'

@app.route('/startrec')
def startrec():
    RecPPGEMG.all()
    return 

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
