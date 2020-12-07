#
# Developed by Alexandre Novello (PUC-Rio)
#

from glamorise_nlidb import GlamoriseNlidb
import csv

patterns_json_txt = """{
  "units_of_measurement" : ["cubic meters"],
    "default_pattern" : [{"POS": "ADV", "OP": "*"}, {"POS": "ADJ", "OP": "*"}, {"POS": "NOUN", "LOWER":{"NOT_IN": ["number"]}}],
    "patterns" : {
        "than options" : {
            "reserved_words" : ["more than", "greater than", "less than", "equal to", "greater than or equal to", "less than or equal to"],
            "having_conditions" : [">", ">", "<", "=", ">=", "<="],
            "specific_pattern" : [{"LIKE_NUM": true}, {"POS": "ADV", "OP": "*"}, {"POS": "ADJ", "OP": "*"}, {"POS": "NOUN", "OP": "*"}, {"POS": "NOUN"}],
            "cut_text" : false
        },
        "group by" : {
            "reserved_words" : ["by", "per", "for each", "of each"],
            "group_by" : true,            
            "cut_text" : false
        },
        "group by and" : {
            "reserved_words" : ["by", "per", "for each", "of each"],
            "group_by" : true,
            "specific_pattern" : [{"POS": "ADV", "OP": "*"}, {"POS": "ADJ", "OP": "*"}, {"POS": "NOUN", "LOWER":{"NOT_IN": ["number"]}}, {"LOWER" : "and"}, {"POS": "NOUN", "LOWER":{"NOT_IN": ["number"]}}],
            "cut_text" : false            
        },
        "how options" : {
            "reserved_words" : ["how many", "how much"],
            "aggregation_functions" : ["count", "sum"],
            "cut_text" : true
        },
        "other count" : {
            "reserved_words" : ["number of", "number of the"],
            "aggregation_functions" : "count",
            "cut_text" : true
        },
        "other sum" : {
            "reserved_words" : ["total"],
            "aggregation_functions" : "sum",
            "cut_text" : true
        },      
        "average options" : {
            "reserved_words" : ["average", "avg", "mean"],
            "aggregation_functions" : "avg",
            "cut_text" : true
        },
        "superlative min" : {
            "reserved_words" : ["least", "smallest", "tiniest", "shortest", "cheapest", "nearest", "lowest", "worst", "newest", "min", "minimum"],
            "aggregation_functions" : "min",
            "cut_text" : true
        },
        "superlative max" : {
            "reserved_words" : ["most", "most number of", "biggest", "longest", "furthest", "highest", "tallest", "greatest", "best", "oldest", "max", "maximum"],
            "aggregation_functions" : "max",
            "cut_text" : true
        },
        "time scale options" : {
            "reserved_words" : ["daily", "monthly", "yearly"],
            "time_scale_replace_text" : {"daily" : "day", "monthly" : "month", "yearly" : "year"},
            "time_scale_aggregation_functions" : "sum",
            "cut_text" : false
        }
    }
}"""

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
# with open('./datasets/pfp.csv', encoding="utf-8") as csv_file:
#     # read the file with the NLQ questions
#     csv_reader = csv.reader(csv_file, delimiter=';', quotechar="'")
#     # jump title line
#     next(csv_reader)
#     line_count = 0
#     # create GLAMORISE object (the child class is instantiated)
#     glamorise = GlamoriseNlidb(NLIDB = 'NaLIR')
#     for row in csv_reader:

        
# the NLQ is the first column of the CSV
#nl_query = row[0]        
glamorise = GlamoriseNlidb(NLIDB = 'NaLIR', patterns = patterns_json_txt)
nl_query = 'return me the number of authors for each conference where author name contains Alex'
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

del glamorise

