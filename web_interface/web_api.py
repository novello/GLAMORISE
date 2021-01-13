import flask
from flask import request, jsonify, render_template, url_for
from flaskext.markdown import Markdown

from os import path
import sys
sys.path.append(path.abspath('/home/novello/nalir-glamorise'))
sys.path.append(path.abspath('/home/novello/GLAMORISE'))
import main_common as mc
from glamorise_nlidb import GlamoriseNlidb

app = flask.Flask(__name__)
Markdown(app)
app.config["DEBUG"] = True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/glamorise_mock_anp')
def glamorise_mock_anp():
    with open('./config/glamorise_mock_anp.json') as json_file:
        patterns_json_txt = json_file.read()

    return render_template('form.html', type='glamorise_mock_anp', patterns_json_txt=patterns_json_txt)


@app.route('/glamorise_nalir_anp')
def glamorise_nalir_anp():
    with open('./config/glamorise_nalir_anp.json') as json_file:
        patterns_json_txt = json_file.read()
    with open('./config/nalir_tokens.xml') as xml_file:
        nalir_tokens = xml_file.read()

    return render_template('form.html', type='glamorise_nalir_anp', patterns_json_txt=patterns_json_txt, nalir_tokens=nalir_tokens)


@app.route('/glamorise_nalir_mas')
def glamorise_nalir_mas():
    with open('./config/glamorise_nalir_mas.json') as json_file:
        patterns_json_txt = json_file.read()
    with open('./config/nalir_tokens.xml') as xml_file:
        nalir_tokens = xml_file.read()

    return render_template('form.html', type='glamorise_nalir_mas', patterns_json_txt=patterns_json_txt, nalir_tokens=nalir_tokens)


@app.route('/backend', methods=['GET', 'POST'])
def backend():    
    try:
        type = 'glamorise_mock_anp'
        nlq = []
        if request.method == 'POST':
            nlq = request.form['nlq']
            type = request.form['type']
            patterns_json_txt = request.form['glamoriseJsonConfig']
            nalir_tokens =  request.form['nalirXmlConfig']
        elif request.method == 'GET':
            nlq = request.args.get('nlq')        
            type = request.args.get('type')
            patterns_json_txt = request.args.get('glamoriseJsonConfig')
            nalir_tokens =  request.args.get('nalirXmlConfig')
        if nlq:       
            if type == 'glamorise_mock_anp':        
                with open('./config/glamorise_mock_anp.json') as json_file:
                    patterns_json_txt = json_file.read()                              
                glamorise = GlamoriseNlidb(patterns = patterns_json_txt)
            elif type == 'glamorise_nalir_anp':            
                with open('./config/nalir_anp_local_db.json') as json_file:
                    config_db = json_file.read()        
                #with open('./config/glamorise_nalir_anp.json') as json_file:
                #    patterns_json_txt = json_file.read()                
                glamorise = GlamoriseNlidb(NLIDB = 'NaLIR', patterns = patterns_json_txt, config_db = config_db)
            elif type == 'glamorise_nalir_mas':
                with open('./config/nalir_mas_local_db.json') as json_file:
                    config_db = json_file.read()        
                #with open('./config/glamorise_nalir_mas.json') as json_file:
                #    patterns_json_txt = json_file.read()           
                glamorise = GlamoriseNlidb(NLIDB = 'NaLIR', patterns = patterns_json_txt, config_db = config_db)
            html = mc.print_results(glamorise, nlq)

            html += mc.print_total_timers()
            return render_template('partial_results.html',  rawtext=html, tables=[glamorise.pd.to_html(classes='data')], titles=glamorise.pd.columns.values)        
        else:
            return ''
    except:
        return ''
                


@app.route('/answer_nlqs', methods=['GET', 'POST'])
def answer_nlqs():
    # with open('./config/glamorise_mock_anp.json') as json_file:
    #    patterns_json_txt = json_file.read()
    # create GLAMORISE object (the child class is instantiated)
    #glamorise = GlamoriseNlidb(patterns = patterns_json_txt)

    with open('./config/nalir_mas_local_db.json') as json_file:
        config_db = json_file.read()

    with open('./config/glamorise_nalir_mas.json') as json_file:
        patterns_json_txt = json_file.read()

    glamorise = GlamoriseNlidb(
        NLIDB='NaLIR', patterns=patterns_json_txt, config_db=config_db)

    nlqs = []
    if request.method == 'POST':
        nlqs = request.form['nlqs']
    elif request.method == 'GET':
        nlqs = request.args.get('nlqs')
    nlqs = nlqs.split('\n')

    if nlqs:
        for nlq in nlqs:

            html = mc.print_results(glamorise, nlq)

            html += mc.print_total_timers()
            return render_template('results.html',  rawtext=html, tables=[glamorise.pd.to_html(classes='data')], titles=glamorise.pd.columns.values)


if __name__ == '__main__':
    app.run()
