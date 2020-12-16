def dump(obj):
  for attr in dir(obj):
    # only the properties that are important to print
    if attr in ['pre_aggregation_functions', 'pre_aggregation_fields', 'pre_group_by_fields',
                'pre_time_scale_aggregation_functions', 'pre_time_scale_aggregation_fields', 'pre_time_scale_group_by_fields',
                'pre_having_fields', 'pre_having_conditions', 'pre_having_values', 'pre_having_units',
                'pre_group_by', 'pre_cut_text', 'pre_replaced_text', 'pre_prepared_query',
                'pos_roup_by_fields', 'pos_glamorise_sql', 'pos_nlidb_sql'
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