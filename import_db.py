#
# Developed by Alexandre Novello (PUC-Rio)
#

import os
import pandas as pd
import sqlite3

all_files = list(filter(lambda x: '.csv' in x, os.listdir('datasets/anp/')))

full_dataset = []

for elem in all_files:
    print(elem)
    data = pd.read_csv('datasets/anp/' + elem)
    full_dataset.append(data)

con = sqlite3.connect('datasets/anp_complete.db')

file_names = [os.path.splitext(elem)[0] for elem in all_files]

table_fields = []


columnNames = 'year,month_year,state,basin,field,well,environment,installation,oil_production,' \
                  'condensed_production,associated_gas_production,non_associated_gas_production,' \
                  'water_production,gas_injection,water_injection_for_secundary_recuperation,' \
                  'water_injection_to_discard,co2_injection,nitrogen_injection,water_steam_injection,' \
                  'polymers_injection,other_fluids_injection,file'


cur = con.cursor()
#cur.execute("DROP TABLE IF EXISTS NLIDB_result_set")
#cur.execute("CREATE TABLE NLIDB_result_set (" + columnNames + ")")


for ind in range(0, len(file_names)):

    query = """INSERT INTO NLIDB_result_set (""" + columnNames + """) VALUES (""" +\
            ','.join(map(str,'?'*len(full_dataset[ind].columns))) + ", '"  +  file_names[ind]+ """')"""
    full_dataset[ind] = full_dataset[ind].astype(str)

    for i in range(0, len(full_dataset[ind])):
        insert_register = tuple(full_dataset[ind].iloc[i])
        cur.execute(query, insert_register)
    con.commit()
    print(file_names[ind])
