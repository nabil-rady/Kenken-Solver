from flask import Flask, render_template, request
import kenken
import solution

app = Flask(__name__)

cages = None
size = None

@app.route('/generate', methods=['POST'])
def generate():
    global cages
    global size

    size = int(request.json['size'])
    cages = kenken.generate(size)
    
    print('cages: ')
    for cage in cages:
        print(cage)
    
    return {'board': cages}

@app.route('/bt', methods=['GET'])
def bt():
    global size, cages
    ken = kenken.Kenken(size, cages)
    
    assignment = solution.backtracking_search(ken)
    assignment = list(assignment.items())
    BT = {'BT': assignment}
    print('BT: ')
    print(assignment)
    return BT

@app.get('/')
def index():
    return render_template('index.html')

app.run(debug=True)
