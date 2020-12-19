#
# Developed by Alexandre Novello (PUC-Rio)
#

from glamorise_nlidb import GlamoriseNlidb
import main_common as mc
import csv
from codetiming import Timer

token_path = '../nalir-glamorise/zfiles/tokens.anp.xml'

config_db = '''{
    "connection":{
            "host": "localhost",
            "password":"desenvolvimento123",
            "user":"nalir",
            "database":"anp"
        },
        "loggingMode": "ERROR",
        "zfiles_path":"/home/novello/nalir-glamorise/zfiles",
        "jars_path":"/home/novello/nalir-glamorise/jars/new_jars"
    }
    '''

patterns_json_txt = """{
  "units_of_measurement" : [],
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
            "pre_cut_text" : false
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
            "pre_cut_text" : false
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
            "pre_time_scale_replace_text" : {"most" : "for each", "most number of" : "for each", "biggest" : "for each", "longest" : "for each", "furthest" : "for each", "highest" : "for each", "tallest" : "for each", "greatest" : "for each", "best" : "for each", "oldest" : "for each", "max" : "for each", "maximum" : "for each"},
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

   
# create GLAMORISE object (the child class is instantiated)
glamorise = GlamoriseNlidb(NLIDB = 'NaLIR', patterns = patterns_json_txt, config_db = config_db, token_path = token_path)
with open('./nlqs/nalir_anp_modified.nlqs.txt', encoding="utf-8") as file:            
    # read the file with the NLQ questions
    lines = file.readlines()     
    line_count = 0
    # create GLAMORISE object (the child class is instantiated)#     
    for nlq in lines:    
        line_count += 1                                             
        mc.print_results(glamorise, nlq)

    mc.print_total_timers()
    del glamorise  

