import flask
from flask import request, jsonify, render_template, url_for
from flaskext.markdown import Markdown

from os import path
import sys
sys.path.append(path.abspath('/home/novello/nalir-glamorise'))
sys.path.append(path.abspath('/home/novello/GLAMORISE'))
from glamorise_nlidb import GlamoriseNlidb
import main_common as mc

app = flask.Flask(__name__)
Markdown(app)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/answer_nlqs', methods=['POST'])
def answer_nlqs():
    with open('./config/glamorise_mock_anp.json') as json_file:
        patterns_json_txt = json_file.read()   
    
    # create GLAMORISE object (the child class is instantiated)
    glamorise = GlamoriseNlidb(patterns = patterns_json_txt)
    nlqs = []
    if request.method == 'POST':		
        nlqs = request.form['nlqs']
        nlqs = nlqs.split('\n')

    if nlqs: 
        for nlq in nlqs:

            html = mc.print_results(glamorise, nlq)      

            html += mc.print_total_timers()         
            return render_template('results.html',  rawtext = html, tables=[glamorise.pd.to_html(classes='data')], titles=glamorise.pd.columns.values)    

if __name__ == '__main__':
    app.run()    