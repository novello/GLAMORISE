from codetiming import Timer
import glamorise

def is_jupyter_notebook():
    # check the environment
    try:
        shell = get_ipython().__class__.__name__
        #if shell == 'ZMQInteractiveShell':
        if shell == 'Shell':  # Google Colab
            return True   # Jupyter notebook or qtconsole
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter

def mc_print(string):
    if jupyter:
        display(Markdown(string))
    else:
        print(string)
    return string     

def mc_display(pd):
    if jupyter:
        return display(pd)
    else:                
        print(pd)
      



def print_results(glamorise, nlq):      
    result = ''
    print("\n\n")
    result += '</br></br>'
    nlq_str = mc_print("**Natural Language Query**: " + nlq)

    glamorise.execute(nlq)
    
    
    dep = glamorise.customized_displacy_dependency_parse_tree()    
    ent = glamorise.customized_displacy_entities()

    print("\n\n")
    result += '</br></br></br>'
    result += mc_print("**GLAMORISE Internal Properties**")
    print("\n")
    result += '</br></br>'
    result += mc_print("**GLAMORISE Preprocessor Properties**")
    result += glamorise.dump('pre_')

    print("\n")
    result += '</br></br>'
    result += mc_print("**GLAMORISE NLIDB Interface Properties**")
    result += glamorise.dump('nlidb_interface_')

    print("\n")
    result += '</br></br>'
    result += mc_print("**GLAMORISE Post-processor Properties**")
    result += glamorise.dump('pos_')

    print("\n")
    result += '</br></br>'
    result += mc_print("**GLAMORISE Result**")
    # display the result as a pandas dataframe
    mc_display(glamorise.pd)    

    result += glamorise.print_timers()

    if glamorise.config_glamorise.get('debug') and glamorise.config_glamorise['debug']:        
        return nlq_str, result, dep, ent
    else:
        return nlq_str, '', dep, ent


def print_total_timers():
    result = ''
    for (key, value) in Timer.timers.items():
        print("total {} : {:.2f} sec".format(key, value))
        result += "</br>total {} : {:.2f} sec".format(key, value)
    return result    

jupyter = is_jupyter_notebook()        