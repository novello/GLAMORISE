import flask
from flask import request, jsonify, render_template, url_for
from flaskext.markdown import Markdown
from flaskext.markdown import Markup
from flask import escape

from os import path
import sys
import json
from xml.etree.ElementTree import fromstring

#to open GLAMORISE and NaLIR files
with open('./config/environment/path.json') as json_file:
    json_path = json_file.read()
json_path = json.loads(json_path)
sys.path.append(path.abspath(json_path['nalir_relative_path']))
sys.path.append(path.abspath(json_path['glamorise_relative_path']))
import main_common as mc
from glamorise_nlidb import GlamoriseNlidb


app = flask.Flask(__name__)
Markdown(app)
app.config["DEBUG"] = False


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logo_history')
def logo_history():
    return render_template('logo_history.html')    


@app.route('/glamorise_mock_anp')
def glamorise_mock_anp():
    with open('./config/environment/glamorise_mock.json') as json_file:
        config_glamorise = json_file.read()
    with open('./config/environment/glamorise_interface_mock_danke_anp.json') as json_file:
        config_glamorise_interface = json_file.read()                

    return render_template('form.html', type='glamorise_mock_anp', config_glamorise=config_glamorise, config_glamorise_interface=config_glamorise_interface)

@app.route('/glamorise_danke_anp')
def glamorise_danke_anp():
    with open('./config/environment/glamorise_danke.json') as json_file:
          config_glamorise = json_file.read()
    with open('./config/environment/glamorise_interface_mock_danke_anp.json') as json_file:
        config_glamorise_interface = json_file.read() 
    
    return render_template('form.html', type='glamorise_danke_anp', config_glamorise=config_glamorise, config_glamorise_interface=config_glamorise_interface)

@app.route('/glamorise_nalir_anp')
def glamorise_nalir_anp():
    with open('./config/environment/glamorise_nalir.json') as json_file:
        config_glamorise = json_file.read()
    with open('./config/environment/glamorise_interface_nalir_anp.json') as json_file:
        config_glamorise_interface = json_file.read()        
    with open('./config/environment/nalir_tokens.xml') as xml_file:
        nalir_tokens = xml_file.read()

    return render_template('form.html', type='glamorise_nalir_anp', config_glamorise=config_glamorise, config_glamorise_interface=config_glamorise_interface, nalir_tokens=nalir_tokens)


@app.route('/glamorise_nalir_mas')
def glamorise_nalir_mas():
    with open('./config/environment/glamorise_nalir.json') as json_file:
        config_glamorise = json_file.read()
    with open('./config/environment/glamorise_interface_nalir_mas.json') as json_file:
        config_glamorise_interface = json_file.read()                
    with open('./config/environment/nalir_tokens.xml') as xml_file:
        nalir_tokens = xml_file.read()

    return render_template('form.html', type='glamorise_nalir_mas', config_glamorise=config_glamorise, config_glamorise_interface=config_glamorise_interface, nalir_tokens=nalir_tokens)


@app.route('/backend', methods=['GET', 'POST'])
def backend():    
    try:
        type = 'glamorise_mock_anp'
        nlq = []
        if request.method == 'POST':
            nlq = request.form.get('nlq').replace('<', '').replace('>', '')
            type = request.form.get('type')
            config_glamorise = request.form.get('glamoriseJsonConfig')
            config_glamorise_interface = request.form.get('glamoriseJsonConfigInterface')
            nalir_tokens =  request.form.get('nalirXmlConfig')              
        elif request.method == 'GET':
            nlq = request.args.get('nlq').replace('<', '').replace('>', '')
            type = request.args.get('type')
            config_glamorise = request.args.get('glamoriseJsonConfig')
            config_glamorise_interface = request.args.get('glamoriseJsonConfigInterface')
            nalir_tokens =  request.args.get('nalirXmlConfig')           
            
        if nalir_tokens:
                nalir_tokens = fromstring(nalir_tokens)    
        if nlq:       
            if type == 'glamorise_mock_anp':                        
                glamorise = GlamoriseNlidb(config_glamorise_param = config_glamorise, config_glamorise_interface_param=config_glamorise_interface) 
            elif type == 'glamorise_danke_anp':            
               glamorise = GlamoriseNlidb(NLIDB = 'Danke',config_glamorise_param = config_glamorise, config_glamorise_interface_param=config_glamorise_interface)          
            elif type == 'glamorise_nalir_anp':            
                with open('./config/environment/nalir_anp_db.json') as json_file:
                    config_db = json_file.read()                        
                glamorise = GlamoriseNlidb(NLIDB = 'NaLIR', config_glamorise_param = config_glamorise, config_glamorise_interface_param=config_glamorise_interface, config_db = config_db, tokens = nalir_tokens)
            elif type == 'glamorise_nalir_mas':
                with open('./config/environment/nalir_mas_db.json') as json_file:
                    config_db = json_file.read()                        
                glamorise = GlamoriseNlidb(NLIDB = 'NaLIR', config_glamorise_param = config_glamorise, config_glamorise_interface_param=config_glamorise_interface, config_db = config_db, tokens = nalir_tokens)
            nlq, html, dep, ent = mc.print_results(glamorise, nlq)
            
            return render_template('results.html',  nlq=nlq, rawtext=html, tables=[glamorise.pd.to_html(classes='data')], titles=glamorise.pd.columns.values, dep = Markup(dep), ent = Markup(ent))        
        else:
            return ''
    except Exception as e:
        print('Exception: ', e)            
        return ''
            
            
if __name__ == '__main__':
    app.run(host='0.0.0.0')
