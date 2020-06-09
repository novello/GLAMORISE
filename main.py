import GLAMORISE
import csv

with open('./datasets/teste.csv') as csv_file:
#with open('/content/sample_data/teste.csv') as csv_file:
  csv_reader = csv.reader(csv_file, delimiter=',', quotechar="'")
  line_count = 0
  for row in csv_reader:
    nl_query = row[0]
    print("\n\nNatural Language Query: ",nl_query )
    glamorise = GLAMORISE.GLAMORISE(nl_query)
    glamorise.pattern_scan()
    glamorise.customized_displacy()
    print("aggregate function: ", glamorise.aggregate_function)
    print("aggregate field: ", glamorise.aggregate_field)
    print("group_by_field: ", glamorise.group_by_field)
    print("having_field: ", glamorise.having_field)
    print("group_by: ", glamorise.group_by)
    print("having: ", glamorise.having)
    print("cut_text: ", glamorise.cut_text)