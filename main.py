from flask import Flask, render_template, request
import kenken

app = Flask(__name__)

cliques = None

@app.route('/generate', methods=['POST'])
def generate():
    global cliques
    size = int(request.json['size'])
    cliques = kenken.generate(size)
    
    print('Cliques: ')
    for clique in cliques:
        print(clique)
    
    return {'board': cliques}

@app.get('/')
def index():
    return render_template('index.html')

app.run(debug=True)