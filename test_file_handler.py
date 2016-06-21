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
        with open('history.txt', 'r+') as f:
            to_write = f.read()[:-1]
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
          

        
if __name__ == '__main__':
    unittest.main()
