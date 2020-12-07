from simple_sqllite import SimpleSQLLite
from mock_nlidb import MockNlidb
from nalir_nlidb import NalirNlidb
from glamorise import Glamorise



# this child class is aware of the NLIDB
# the implementation has to be changed depending on the NLIDB
class GlamoriseNlidb(Glamorise):

    def __init__(self, lang = "en_core_web_sm", NLIDB = 'Mock'):
        super(GlamoriseNlidb, self).__init__(lang)
        # NLIDB instance
        if NLIDB == 'Mock':
            self.__nlidb = MockNlidb()
        elif NLIDB == 'NaLIR':
            self.__nlidb = NalirNlidb()
        
        

    def _send_question_receive_answer(self):
        # send the NLQ question and receive the JSON with the columns and result set
        columns, result_set = self.__nlidb.execute_query(self.prepared_query)
        return columns, result_set

    def _translate_fields(self, fields):
        # translate the field to the appropriate column name
        for i in range(len(fields)):
            # ask the NLIDB for the appropriate column name
            fields[i] = self.__nlidb.field_synonym(fields[i].replace(' ', '_'))
        # the trick to convert fields that were converted to more than one column
        # E.g.: month -> year, month
        if fields:
            fields_str = ','.join(fields)
            fields = fields_str.split(',')
            fields = [field.strip() for field in fields]
        return fields

    def _translate_all_fields(self):
        # translate all fields that GLAMORISE is aware of
        self._aggregation_fields = self._translate_fields(self._aggregation_fields)
        self._group_by_fields = self._translate_fields(self._group_by_fields)
        self._time_scale_aggregation_fields = self._translate_fields(self._time_scale_aggregation_fields)
        self._time_scale_group_by_fields = self._translate_fields(self._time_scale_group_by_fields)
        self._having_fields = self._translate_fields(self._having_fields)