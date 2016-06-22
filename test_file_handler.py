# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
'''tests for the longintmath.py module'''
from __future__ import absolute_import
import os
import json
import unittest
import file_handler as fh
import dicetables as dt
import numpy as np


def create_plot_object(table):
    '''converts the table into a PlotObject'''
    new_object = {}
    new_object['text'] = str(table).replace('\n', ' \\ ')
    graph_pts = dt.graph_pts(table, axes=False)
    y_vals = [pts[1] for pts in graph_pts]

    new_object['x_min'], new_object['x_max'] = table.values_range()
    new_object['y_min'] = min(y_vals)
    new_object['y_max'] = max(y_vals)
    new_object['pts'] = graph_pts
    new_object['orig'] = table.frequency_all()
    new_object['dice'] = table.get_list()
    return new_object


class Testfh(unittest.TestCase):
    def assertArrayEqual(self, nparray_1, nparray_2):
        self.assertTrue((nparray_1.tolist() == nparray_2.tolist() and
                         nparray_1.dtype == nparray_2.dtype))
    

    def test_make_table_json_empty_table(self):
        self.assertEqual(fh.make_table_json(dt.DiceTable()),
                         json.dumps([[], [[0, 1]]], indent=2))
    def test_make_table_json_non_empty_table(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(2))
        table.add_die(2, dt.Die(1))
        string = json.dumps([[["Die(1)", 2], ["Die(2)", 1]], [[3, 1], [4, 1]]],
                            indent=2)
        self.assertEqual(fh.make_table_json(table), string)
    def test_parse_dice_list_with_die(self):
        input_list = [["Die(2)", 5]]
        dice_list = [(dt.Die(2), 5)]
        self.assertEqual(fh.parse_dice(input_list), dice_list)
    def test_parse_dice_list_with_moddie(self):
        input_list = [["ModDie(2, -3)", 5]]
        dice_list = [(dt.ModDie(2, -3), 5)]
        self.assertEqual(fh.parse_dice(input_list), dice_list)
    def test_parse_dice_list_with_weighteddie(self):
        input_list = [["WeightedDie({1:0, 2:1})", 5]]
        dice_list = [(dt.WeightedDie({2:1}), 5)]
        self.assertEqual(fh.parse_dice(input_list), dice_list)
    def test_parse_dice_list_with_modweighteddie(self):
        input_list = [["ModWeightedDie({1:0, 2:1}, 4)", 5]]
        dice_list = [(dt.ModWeightedDie({1:0, 2:1}, 4), 5)]
        self.assertEqual(fh.parse_dice(input_list), dice_list)
    def test_parse_dice_list_with_empty_list(self):
        input_list = []
        dice_list = []
        self.assertEqual(fh.parse_dice(input_list), dice_list)
    def test_parse_dice_list_with_multi_die_list(self):
        input_list = [["Die(2)", 5], ["Die(3)", 2]]
        dice_list = [(dt.Die(2), 5), (dt.Die(3), 2)]
        self.assertEqual(fh.parse_dice(input_list), dice_list)
    def test_make_table_info_empty_table(self):
        table = dt.DiceTable()
        json_string = fh.make_table_json(table)
        dice_list, tuples = fh.make_table_basis(json_string)
        tuples = [(pair[0], pair[1]) for pair in tuples]
        self.assertEqual(table.frequency_all(), tuples)
        self.assertEqual(table.get_list(), dice_list)
    def test_make_table_non_empty_table(self):
        table = dt.DiceTable()
        table.add_die(2, dt.Die(2))
        table.add_die(3, dt.ModDie(3, -1))
        table.add_die(4, dt.WeightedDie({1:2}))
        table.add_die(5, dt.ModWeightedDie({2:3, 3:1}, 6))
        json_string = fh.make_table_json(table)
        dice_list, tuples = fh.make_table_basis(json_string)
        tuples = [(pair[0], pair[1]) for pair in tuples]
        self.assertEqual(table.frequency_all(), tuples)
        self.assertEqual(table.get_list(), dice_list)
    def test_make_plot_obj_dic_on_empty_table(self):
        table = dt.DiceTable()
        p_obj = create_plot_object(table)
        dic = {'text': '', 'x_min': 0, 'x_max': 0, 'y_min':100.0, 'y_max':100., 
               'pts': [(0, 100.)], 'orig': [(0, 1)], 'dice': []}
        self.assertEqual(dic, fh.make_plot_obj_dic(p_obj))
    def test_make_plot_obj_dic_on_table(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(2))
        p_obj = create_plot_object(table)
        dic = {'text': '1D2', 'x_min': 1, 'x_max': 2, 'y_min':50., 'y_max':50., 
               'pts': [(1, 50.), (2, 50.)], 'orig': [(1, 1), (2, 1)], 
               'dice': [('Die(2)', 1)]}
        self.assertEqual(dic, fh.make_plot_obj_dic(p_obj))
    def test_make_plot_obj_dic_on_table_with_more_dice(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(2))
        table.add_die(2, dt.Die(1))
        p_obj = create_plot_object(table)
        dic = {'text': '2D1 \\ 1D2', 'x_min': 3, 'x_max': 4, 'y_min':50.,
               'y_max':50., 
               'pts': [(3, 50.), (4, 50.)], 'orig': [(3, 1), (4, 1)], 
               'dice': [('Die(1)', 2), ('Die(2)', 1)]}
        self.assertEqual(dic, fh.make_plot_obj_dic(p_obj))
    def test_make_plot_obj_dic_cant_mutate_original(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(2))
        p_obj = create_plot_object(table)
        p_obj_dic = fh.make_plot_obj_dic(p_obj)
        p_obj_dic['text'] = 0
        self.assertEqual(p_obj['text'], '1D2')
        p_obj_dic['orig'][0] = 0
        self.assertEqual(p_obj['orig'], [(1, 1), (2, 1)])
    def test_make_plot_obj_works_on_empty_table(self):
        table = dt.DiceTable()
        p_obj = create_plot_object(table)
        p_obj_dic = fh.make_plot_obj_dic(p_obj)
        new_obj = fh.make_plot_obj(p_obj_dic)
        self.assertEqual(p_obj, new_obj)
    def test_make_plot_obj_works_on_non_empty_table(self):
        table = dt.DiceTable()
        table.add_die(5, dt.ModWeightedDie({2:2}, -3))
        table.add_die(2, dt.Die(3))
        p_obj = create_plot_object(table)
        p_obj_dic = fh.make_plot_obj_dic(p_obj)
        new_obj = fh.make_plot_obj(p_obj_dic)
        self.assertEqual(p_obj, new_obj)
    
    def test_make_history_on_empty_list(self):
        self.assertEqual('[]', fh.make_history_json([]))
    def test_make_history_json_on_empty_table_p_object(self):
        table = dt.DiceTable()
        po_list = [create_plot_object(table)]
        dic = [fh.make_plot_obj_dic(po_list[0])]
        json_string = json.dumps(dic, indent=2)
        self.assertEqual(json_string, fh.make_history_json(po_list))
    def test_make_history_json_on_list_of_p_objects(self):
        table = dt.DiceTable()
        po_list = []
        po_list.append(create_plot_object(table))
        table.add_die(3, dt.Die(6))
        po_list.append(create_plot_object(table))
        table.add_die(2, dt.Die(2))
        po_list.append(create_plot_object(table))
        dumps_list = []
        for po in po_list:
            dumps_list.append(fh.make_plot_obj_dic(po))
        json_string = json.dumps(dumps_list, indent=2)
        self.assertEqual(json_string, fh.make_history_json(po_list))
    def test_make_history_empty_json(self):
        self.assertEqual([], fh.make_history('[]'))    
    def test_make_history_other_case(self):
        table = dt.DiceTable()
        po_list = []
        po_list.append(create_plot_object(table))
        table.add_die(3, dt.Die(6))
        po_list.append(create_plot_object(table))
        table.add_die(2, dt.Die(2))
        po_list.append(create_plot_object(table))
        
        json_string = fh.make_history_json(po_list)
        self.assertEqual(po_list, fh.make_history(json_string))
    def test_write_table_empty_table(self):
        table = dt.DiceTable()
        fh.write_table(table)
        with open('table.txt', 'r') as f:
            json_str = f.read()
            self.assertEqual(json_str, fh.make_table_json(table))
    def test_write_table_non_empty_table(self):
        table = dt.DiceTable()
        table.add_die(3, dt.Die(6))
        table.add_die(2, dt.ModDie(2, -1))
        fh.write_table(table)
        with open('table.txt', 'r') as f:
            json_str = f.read()
            self.assertEqual(json_str, fh.make_table_json(table))
    def test_read_table_no_file(self):
        os.remove('table.txt')
        dice_list, tuples = fh.read_table()
        self.assertEqual(tuples, [[0, 1]])
        self.assertEqual(dice_list, [])
    def test_read_table_with_file(self):
        table = dt.DiceTable()
        table.add_die(3, dt.Die(6))
        table.add_die(2, dt.ModDie(2, -1))
        fh.write_table(table)
        dice_list, tuples = fh.read_table()
        tuples = [(pair[0], pair[1]) for pair in tuples]
        self.assertEqual(table.frequency_all(), tuples)
        self.assertEqual(table.get_list(), dice_list)
        #new_table = fh.read_table()
        #self.assertEqual(table.frequency_all(), new_table.frequency_all())
        #self.assertEqual(table.get_list(), new_table.get_list())
    def test_write_history_empty_list(self):
        fh.write_history([])
        with open('history.txt', 'r') as f:
            json_str = f.read()
            self.assertEqual(json_str, '[]')    
    def test_write_history_other_case(self):
        table = dt.DiceTable()
        po_list = []
        po_list.append(create_plot_object(table))
        table.add_die(3, dt.Die(6))
        po_list.append(create_plot_object(table))
        table.add_die(2, dt.Die(2))
        po_list.append(create_plot_object(table))
        fh.write_history(po_list)
        with open('history.txt', 'r') as f:
            json_str = f.read()
            self.assertEqual(json_str, fh.make_history_json(po_list))
    def test_read_history_no_file(self):
        os.remove('history.txt')
        history = fh.read_history()
        self.assertEqual(history, ('no file', []))
        self.assertEqual(fh.read_history(), ('ok', []))
    def test_read_history_with_file(self):
        table = dt.DiceTable()
        po_list = []
        po_list.append(create_plot_object(table))
        table.add_die(3, dt.Die(6))
        po_list.append(create_plot_object(table))
        table.add_die(2, dt.Die(2))
        po_list.append(create_plot_object(table))
        fh.write_history(po_list)

        self.assertEqual(('ok', po_list), fh.read_history())
    def test_read_history_with_corrupted_file(self):
        table = dt.DiceTable()
        po_list = []
        po_list.append(create_plot_object(table))
        table.add_die(3, dt.Die(6))
        po_list.append(create_plot_object(table))
        table.add_die(2, dt.Die(2))
        po_list.append(create_plot_object(table))
        fh.write_history(po_list)
        with open('history.txt', 'r') as f:
            to_write = f.read()[:-1]
        with open('history.txt', 'w') as f:
            f.write(to_write)
        self.assertEqual(('corrupted file', []), fh.read_history())
        
        fh.write_history(po_list)
        with open('history.txt', 'w') as f:
            f.write('{1:2}')
        self.assertEqual(('corrupted file', []), fh.read_history())
        
        fh.write_history(po_list)
        with open('history.txt', 'w') as f:
            f.write('asdf')
        self.assertEqual(('corrupted file', []), fh.read_history())
        
        fh.write_history(po_list)
        with open('history.txt', 'w') as f:
            f.write('[[]]')
        self.assertEqual(('corrupted file', []), fh.read_history())
    
          
    def test_check_data_empty_table(self):
        table = dt.DiceTable()
        obj = create_plot_object(table)
        self.assertEqual(fh.check_data(obj), 'ok')
    def check_data_not_a_dictionary(self):
        self.assertEqual(fh.check_data('a'), 'error: not a dict')              
    def test_check_data_missing_key(self):
        table = dt.DiceTable()
        table.add_die(3, dt.Die(6))
        obj = create_plot_object(table)
        del obj['pts']
        self.assertEqual(fh.check_data(obj), 'error: missing key')
    def test_check_data_incorrect_type_at_key(self):
        table = dt.DiceTable()
        table.add_die(3, dt.Die(6))
        obj = create_plot_object(table)
        obj['pts'] = 'a'
        self.assertEqual(fh.check_data(obj), "error: pts not <type 'list'>")
    def test_check_data_incorrect_freq_in_orig(self):
        obj = create_plot_object(dt.DiceTable())
        obj['orig'] = [(1.0, 2)]
        self.assertEqual(fh.check_data(obj), 'error: corrupted "orig"')
    def test_check_data_long_in_freq_in_orig_ok(self):
        obj = create_plot_object(dt.DiceTable())
        obj['orig'] = [(10*1000, 2)]
        self.assertEqual(fh.check_data(obj), 'ok')
    def test_check_data_incorrect_val_in_orig(self):
        obj = create_plot_object(dt.DiceTable())
        obj['orig'] = [(10*1000, 2.0)]
        self.assertEqual(fh.check_data(obj), 'error: corrupted "orig"')
    def test_check_data_incorrect_x_pts_in_pts(self):
        obj = create_plot_object(dt.DiceTable())
        obj['pts'] = [(10.0, 2.0)]
        self.assertEqual(fh.check_data(obj), 'error: corrupted "pts"')
    def test_check_data_incorrect_y_pts_in_pts(self):
        obj = create_plot_object(dt.DiceTable())
        obj['pts'] = [(10, 2)]
        self.assertEqual(fh.check_data(obj), 'error: corrupted "pts"')
    def test_check_data_incorrect_num_in_dice(self):
        obj = create_plot_object(dt.DiceTable())
        obj['dice'] = [(dt.Die(6), 2.0)]
        self.assertEqual(fh.check_data(obj), 'error: dicelist at (Die(6), 2.0)')
    def test_check_data_incorrect_die_in_dice(self):
        obj = create_plot_object(dt.DiceTable())
        obj['dice'] = [('a', 2.)]
        self.assertEqual(fh.check_data(obj), 'error: dicelist at (\'a\', 2.0)')
    def test_check_data_all_die_types_pass(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(4))
        table.add_die(1, dt.ModDie(4,2))
        table.add_die(1, dt.WeightedDie({1:2}))
        table.add_die(1, dt.ModWeightedDie({1:2}, 3))
        table.add_die(1, dt.StrongDie(dt.Die(3), 3))
        obj = create_plot_object(table)
        self.assertEqual(fh.check_data(obj), 'ok')
    def test_check_history_breaks_at_first_error(self):
        obj1 = create_plot_object(dt.DiceTable())
        obj2 = create_plot_object(dt.DiceTable())
        obj1['orig'] = [(2.0, 1)]
        del obj2['pts']
        hist = np.array([obj1, obj2])
        self.assertEqual(fh.check_history(hist), 'error: corrupted "orig"')
    def test_check_history_ok_for_valid_hist(self):
        obj1 = create_plot_object(dt.DiceTable())
        obj2 = create_plot_object(dt.DiceTable())
        hist = np.array([obj1, obj2])
        self.assertEqual(fh.check_history(hist), 'ok')
        
    def test_read_write_hist_np_work_ok_for_normal_case(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(3))
        obj1 = create_plot_object(table)
        table.add_die(2, dt.Die(5))
        obj2 = create_plot_object(table)
        hist = np.array([obj1, obj2])
        fh.write_history_np(hist)
        msg, new_hist = fh.read_history_np()
        self.assertEqual(msg, 'ok')
        self.assertArrayEqual(hist, new_hist)
    def test_read_np_returns_error_and_empty_if_check_hist_has_error(self):
        fh.write_history_np(np.array([1,2,3]))
        msg, hist = fh.read_history_np()
        self.assertEqual(msg, 'error: not a dict')
        self.assertArrayEqual(hist, np.array([], dtype=object))
    def test_read_np_returns_error_and_empty_if_hist_empty_and_wrong_type(self):
        fh.write_history_np(np.array([]))
        msg, hist = fh.read_history_np()
        self.assertEqual(msg, 'error: wrong array type')
        self.assertArrayEqual(hist, np.array([], dtype=object))
    def test_read_np_returns_ok_and_empty_if_hist_empty_and_correct_type(self):
        fh.write_history_np(np.array([], dtype=object))
        msg, hist = fh.read_history_np()
        self.assertEqual(msg, 'ok: no history')
        self.assertArrayEqual(hist, np.array([], dtype=object))
    def test_read_np_returns_error_and_empty_if_no_file(self):
        os.remove('numpy_history.npy')
        msg, hist = fh.read_history_np()
        self.assertEqual(msg, 'error: no file')
        self.assertArrayEqual(hist, np.array([], dtype=object))
    def test_read_np_returns_error_and_empty_if_corrupted_file(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(3))
        obj1 = create_plot_object(table)
        table.add_die(2, dt.Die(5))
        obj2 = create_plot_object(table)
        hist = np.array([obj1, obj2])
        fh.write_history_np(hist)
        with open('numpy_history.npy', 'r') as f:
            to_write = f.read()[:-1]
        with open('numpy_history.npy', 'w') as f:
            f.write(to_write)
        msg, hist = fh.read_history_np()
        self.assertEqual(msg, 'error: file corrupted')
        self.assertArrayEqual(hist, np.array([], dtype=object))
        
if __name__ == '__main__':
    unittest.main()
