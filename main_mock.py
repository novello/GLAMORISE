#
# Developed by Alexandre Novello (PUC-Rio)
#

from glamorise_nlidb import GlamoriseNlidb
import main_common as mc
import csv
from codetiming import Timer

patterns_json_txt = """{
  "units_of_measurement" : ["cubic meters"],
    "default_pattern" : [{"POS": "ADV", "OP": "*"}, {"POS": "ADJ", "OP": "*"}, {"POS": "NOUN", "LOWER":{"NOT_IN": ["number"]}}],
    "patterns" : {
        "than options" : {
            "reserved_words" : ["more than", "greater than", "less than", "equal to", "greater than or equal to", "less than or equal to"],
            "pre_having_conditions" : [">", ">", "<", "=", ">=", "<="],
            "specific_pattern" : [{"LIKE_NUM": true}, {"POS": "ADV", "OP": "*"}, {"POS": "ADJ", "OP": "*"}, {"POS": "NOUN", "OP": "*"}, {"POS": "NOUN"}],
            "pre_cut_text" : false
        },
        "group by" : {
            "reserved_words" : ["by", "per", "for each", "of each"],
            "pre_group_by" : true,            
            "pre_cut_text" : true
        },
        "group by and" : {
            "reserved_words" : ["by", "per", "for each", "of each"],
            "pre_group_by" : true,
            "specific_pattern" : [{"POS": "ADV", "OP": "*"}, {"POS": "ADJ", "OP": "*"}, {"POS": "NOUN", "LOWER":{"NOT_IN": ["number"]}}, {"LOWER" : "and"}, {"POS": "NOUN", "LOWER":{"NOT_IN": ["number"]}}],
            "pre_cut_text" : false            
        },
        "how options" : {
            "reserved_words" : ["how many", "how much"],
            "pre_aggregation_functions" : ["count", "sum"],
            "pre_cut_text" : true
        },
        "other count" : {
            "reserved_words" : ["number of", "number of the"],
            "pre_aggregation_functions" : "count",
            "pre_cut_text" : true
        },
        "other sum" : {
            "reserved_words" : ["total"],
            "pre_aggregation_functions" : "sum",
            "pre_cut_text" : true
        },      
        "average options" : {
            "reserved_words" : ["average", "avg", "mean"],
            "pre_aggregation_functions" : "avg",
            "pre_cut_text" : true
        },
        "superlative min" : {
            "reserved_words" : ["least", "smallest", "tiniest", "shortest", "cheapest", "nearest", "lowest", "worst", "newest", "min", "minimum"],
            "pre_aggregation_functions" : "min",
            "pre_cut_text" : true
        },
        "superlative max" : {
            "reserved_words" : ["most", "most number of", "biggest", "longest", "furthest", "highest", "tallest", "greatest", "best", "oldest", "max", "maximum"],
            "pre_aggregation_functions" : "max",
            "pre_cut_text" : true
        },
        "time scale options" : {
            "reserved_words" : ["daily", "monthly", "yearly"],
            "pre_time_scale_replace_text" : {"daily" : "day", "monthly" : "month", "yearly" : "year"},
            "pre_time_scale_aggregation_functions" : "sum",
            "pre_cut_text" : false
        }
    }
}"""



jupyter = mc.is_jupyter_notebook()
with open('./datasets/pfp.csv', encoding="utf-8") as csv_file:
    # read the file with the NLQ questions
    csv_reader = csv.reader(csv_file, delimiter=';', quotechar="'")
    # jump title line
    next(csv_reader)
    line_count = 0
    # create GLAMORISE object (the child class is instantiated)
    glamorise = GlamoriseNlidb(patterns = patterns_json_txt)
    for row in csv_reader:
        # the NLQ is the first column of the CSV
        nl_query = row[0]        
        if jupyter:
            print("\n\n")
            mc.printmd("**Natural Language Query**: " + nl_query)
        else:
            print("\n\nNatural Language Query: ",nl_query)

        glamorise.execute(nl_query)

        if jupyter:
            mc.printmd("**spaCy Parse Tree**")
            # show spaCy parse tree
            glamorise.customized_displacy()
        if jupyter:
            mc.printmd("**GLAMORISE Internal Properties**")
        else:
            print("GLAMORISE Internal Properties")
        mc.dump(glamorise)

        if jupyter:
            mc.printmd("**GLAMORISE Result**")
            # display the result as a pandas dataframe
            display(glamorise.pd)
        else:
            print("GLAMORISE Result")
            # print the result as a pandas dataframe
            print(glamorise.pd)

        
        print("timer_pre : {:.2f} sec".format(glamorise._timer_pre.last))
        print("timer_nlidb_execution : {:.2f} sec".format(glamorise._timer_nlidb_execution.last))
        print("timer_nlidb_json_result_set : {:.2f} sec".format(glamorise._timer_nlidb_json_result_set.last))
        print("timer_pos : {:.2f} sec".format(glamorise._timer_pos.last))
        print("timer_exibition : {:.2f} sec".format(glamorise._timer_exibition.last))

    for (key, value) in Timer.timers.items():
        print("total {} : {:.2f} sec".format(key, value))
    del glamorise

