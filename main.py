#
# Developed by Alexandre Novello (PUC-Rio)
#

from glamorise_mock_nlidb import GLAMORISEMockNLIDB
import csv

def dump(obj):
  for attr in dir(obj):
    # only the properties that are important to print
    if attr in ['aggregation_functions', 'aggregation_fields', 'group_by_fields',
                'time_scale_aggregation_functions', 'time_scale_aggregation_fields', 'time_scale_group_by_fields',
                'having_fields', 'having_conditions', 'having_values', 'having_units',
                'group_by', 'cut_text', 'replaced_text', 'prepared_query',
                'post_processing_group_by_fields', 'sql'
                ] and getattr(obj, attr):
        print("%s = %r" % (attr, getattr(obj, attr)))

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

def printmd(string):
    display(Markdown(string))

jupyter = is_jupyter_notebook()
with open('./datasets/pfp.csv', encoding="utf-8") as csv_file:
    # read the file with the NLQ questions
    csv_reader = csv.reader(csv_file, delimiter=';', quotechar="'")
    # jump title line
    next(csv_reader)
    line_count = 0
    # create GLAMORISE object (the child class is instantiated)
    glamorise = GLAMORISEMockNLIDB()
    for row in csv_reader:
        # the NLQ is the first column of the CSV
        nl_query = row[0]        
        if jupyter:
            print("\n\n")
            printmd("**Natural Language Query**: " + nl_query)
        else:
            print("\n\nNatural Language Query: ",nl_query)

        glamorise.execute(nl_query)

        if jupyter:
            printmd("**spaCy Parse Tree**")
            # show spaCy parse tree
            glamorise.customized_displacy()
        if jupyter:
            printmd("**GLAMORISE Internal Properties**")
        else:
            print("GLAMORISE Internal Properties")
        dump(glamorise)

        if jupyter:
            printmd("**GLAMORISE Result**")
            # display the result as a pandas dataframe
            display(glamorise.pd)
        else:
            print("GLAMORISE Result")
            # print the result as a pandas dataframe
            print(glamorise.pd)



