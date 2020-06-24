import GLAMORISE
import csv

def dump(obj):
  for attr in dir(obj):
    if attr in ['aggregate_functions', 'aggregate_fields', 'group_by_fields',
                'candidate_aggregate_functions', 'candidate_aggregate_fields', 'candidate_group_by_fields',
                'having_fields', 'having_conditions', 'having_value',
                'group_by', 'having', 'cut_text', 'substitute_text', 'prepared_query', 'sql'
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

with open('./datasets/test.csv') as csv_file:
#with open('/content/sample_data/test.csv') as csv_file:
    #csv_reader = csv.reader(csv_file, delimiter=',', quotechar="'")
    #line_count = 0
    #for row in csv_reader:
        #nl_query = row[0]
        nl_query = 'Which field produces the most oil per month?'
        jupyter = is_jupyter_notebook()
        if jupyter:
            print("\n\n")
            printmd("**Natural Language Query**: " + nl_query)
        else:
            print("\n\nNatural Language Query: ",nl_query)
        if jupyter:
            glamorise = GLAMORISEMockNLIDB(nl_query)
        else:
            glamorise = GLAMORISE.GLAMORISEMockNLIDB(nl_query)
        glamorise.pattern_scan()
        if jupyter:
            printmd("**spaCy Parse Tree**")
        else:
            print("spaCy Parse Tree")
        glamorise.customized_displacy()
        if jupyter:
            printmd("**GLAMORISE Preprocessor**")
        else:
            print("GLAMORISE Preprocessor")
        glamorise.prepare_query_to_NLIDB()
        glamorise.prepare_aggregate_SQL()
        dump(glamorise)
