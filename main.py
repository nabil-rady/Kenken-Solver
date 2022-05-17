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
    BT = {'solution': assignment}
    print('BT: ')
    print(assignment)
    return BT

@app.route('/fc', methods=['GET'])
def fc():
    global size, cages
    ken = kenken.Kenken(size, cages)
    
    assignment = solution.backtracking_search(ken, inference_method=solution.forward_checking)
    assignment = list(assignment.items())
    FC = {'solution': assignment}
    print('FC: ')
    print(assignment)
    return FC

@app.route('/ac3', methods=['GET'])
def ac3():
    global size, cages
    ken = kenken.Kenken(size, cages)
    
    assignment = solution.backtracking_search(ken, inference_method=solution.forward_checking_and_ac3)
    assignment = list(assignment.items())
    AC3 = {'solution': assignment}
    print('AC3: ')
    print(assignment)
    return AC3

@app.get('/')
def index():
    return render_template('index.html')

app.run(debug=True)
