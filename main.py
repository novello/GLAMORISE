from GLAMORISE import GLAMORISEMockNLIDB
import csv

def dump(obj):
  for attr in dir(obj):
    if attr in ['aggregate_functions', 'aggregate_fields', 'group_by_fields',
                'candidate_aggregate_functions', 'candidate_aggregate_fields', 'candidate_group_by_fields',
                'having_fields', 'having_conditions', 'having_values', 'having_units',
                'group_by', 'having', 'cut_text', 'substitute_text', 'prepared_query',
                'post_processing_group_by_fields', 'sql'
                ] and getattr(obj, attr):
        print("%s = %r" % (attr, getattr(obj, attr)))

def is_jupyter_notebook():
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter

def printmd(string):
    display(Markdown(string))

with open('./datasets/pfp.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';', quotechar="'")
    next(csv_reader)
    line_count = 0
    for row in csv_reader:
        nl_query = row[0]
        #nl_query = 'What was the average monthly production of oil in state of Rio de Janeiro?'
        jupyter = is_jupyter_notebook()
        if jupyter:
            print("\n\n")
            printmd("**Natural Language Query**: " + nl_query)
        else:
            print("\n\nNatural Language Query: ",nl_query)

        glamorise = GLAMORISEMockNLIDB(nl_query)

        if jupyter:
            printmd("**spaCy Parse Tree**")
            glamorise.customized_displacy()
        if jupyter:
            printmd("**GLAMORISE Internal Variables**")
        else:
            print("GLAMORISE Internal Variables")
        dump(glamorise)
        if jupyter:
            printmd("**GLAMORISE Result**")
            display(glamorise.pd)
        else:
            print("GLAMORISE Result")
            print(glamorise.pd)


