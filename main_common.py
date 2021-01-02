from codetiming import Timer

def dump(obj):
  for attr in dir(obj):
    # only the properties that are important to print
    if attr in ['pre_aggregation_functions', 'pre_aggregation_fields', 'pre_group_by_fields',
                'pre_time_scale_aggregation_functions', 'pre_time_scale_aggregation_fields', 'pre_time_scale_group_by_fields',
                'pre_having_fields', 'pre_having_conditions', 'pre_having_values', 'pre_having_units',
                'pre_group_by', 'pre_cut_text', 'pre_replaced_text', 'original_query', 'pre_before_query', 'pre_prepared_query', 'pre_prepared_query_before_field_translation',
                'nlidb_interface_fields',
                'pos_aggregation_functions', 'pos_aggregation_fields', 'pos_group_by_fields', 'pos_glamorise_sql', 'pos_nlidb_sql', 'pos_nlidb_sql_first_attempt', 'pos_nlidb_sql_second_attempt', 'pos_nlidb_sql_third_attempt'
                ] and getattr(obj, attr):
        print("%s = %r\n" % (attr, getattr(obj, attr)))

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


def print_results(glamorise, nlq):
    if jupyter:
        print("\n\n")
        mc.printmd("**Natural Language Query**: " + nlq)
    else:
        print("\n\nNatural Language Query: ",nlq)

    glamorise.execute(nlq)

    if jupyter:
        mc.printmd("**spaCy Parse Tree**")
        # show spaCy parse tree
        glamorise.customized_displacy()
    if jupyter:
        mc.printmd("**GLAMORISE Internal Properties**")
    else:
        print("GLAMORISE Internal Properties")
    dump(glamorise)

    if jupyter:
        mc.printmd("**GLAMORISE Result**")
        # display the result as a pandas dataframe
        display(glamorise.pd)
    else:
        print("GLAMORISE Result")
        # print the result as a pandas dataframe
        print(glamorise.pd)


    print("timer_pre : {:.2f} sec".format(glamorise._timer_pre.last))
    print("timer_nlidb_execution_first_and_second_attempt : {:.2f} sec".format(glamorise._timer_nlidb_execution_first_and_second_attempt.last))    
    print("timer_nlidb_execution_third_attempt : {:.2f} sec".format(glamorise._timer_nlidb_execution_third_attempt.last))           
    print("timer_nlidb_json_result_set : {:.2f} sec".format(glamorise._timer_nlidb_json_result_set.last))
    print("timer_pos : {:.2f} sec".format(glamorise._timer_pos.last))
    print("timer_exibition : {:.2f} sec".format(glamorise._timer_exibition.last))


def print_total_timers():
    for (key, value) in Timer.timers.items():
        print("total {} : {:.2f} sec".format(key, value))

jupyter = is_jupyter_notebook()        