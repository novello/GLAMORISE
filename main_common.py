from codetiming import Timer

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

def mc_display(pd):
    if jupyter:
        display(pd)
    else:                
        print(pd)



def print_results(glamorise, nlq):    
    print("\n\n")
    mc_print("**Natural Language Query**: " + nlq)

    glamorise.execute(nlq)
    
    if jupyter:
        mc_print("**spaCy Parse Tree**")
        # show spaCy parse tree
        glamorise.customized_displacy()

    print("\n\n")
    mc_print("GLAMORISE Internal Properties")
    print("\n")
    mc_print("GLAMORISE Preprocessor Properties")
    glamorise.dump('pre_')

    print("\n")
    mc_print("GLAMORISE NLIDB Interface Properties")
    glamorise.dump('nlidb_interface_')

    print("\n")
    mc_print("GLAMORISE Post-processor Properties")
    glamorise.dump('pos_')

    mc_print("**GLAMORISE Result**")
    # display the result as a pandas dataframe
    mc_display(glamorise.pd)    

    glamorise.print_timers()
    


def print_total_timers():
    for (key, value) in Timer.timers.items():
        print("total {} : {:.2f} sec".format(key, value))

jupyter = is_jupyter_notebook()        