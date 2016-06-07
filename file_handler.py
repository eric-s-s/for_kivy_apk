'''for sending and retrieving main info to file'''

import json
import dicestats as ds
import tableinfo as ti

from main import PlotObject


def make_table_json(dtable):
    '''takes a table and converts it into json str of '[dice_list, freqs]' '''
    d_list = [(repr(die), num) for die, num in dtable.get_list()]
    return json.dumps([d_list, dtable.frequency_all()])
def parse_dice(dice_lst):
    '''takes a list of [['die-repr':number], [..]] and makes a dice_list'''
    out = []
    for string, num in dice_lst:
        if 'Weighted' in string:
            dic_str = string[string.find('{') + 1: string.find('}')]
            pairs = dic_str.split(',')
            pair_lst = [item.split(':') for item in pairs]
            pair_lst = [(int(pair[0]), int(pair[1])) for pair in pair_lst]
            input_dic = dict(pair_lst)
            if 'Mod' in string:
                mod_str = string.split('}')[1]
                mod = int(mod_str[1:-1])
                out.append((ds.ModWeightedDie(input_dic, mod), num))
            else:
                out.append((ds.WeightedDie(input_dic), num))
        else:
            numbers = string[string.find('(') + 1: string.find(')')]
            if 'Mod' in string:
                size, mod = numbers.split(',')
                out.append((ds.ModDie(int(size), int(mod)), num))
            else:
                out.append((ds.Die(int(numbers)), num))
    return out

def make_table(json_str):
    '''takes a json_str of a table and makes a table'''
    dice_dic, tuples = json.loads(json_str)
    dice_list = parse_dice(dice_dic)
    new = ds.DiceTable()
    new.add(1, tuples)
    for die, num in dice_list:
        new.update_list(num, die)
    return new

def create_plot_object(table):
    '''converts the table into a PlotObject'''
    new_object = PlotObject()
    new_object.text = str(table).replace('\n', ' \\ ')
    graph_pts = ti.graph_pts(table, axes=False)
    y_vals = [pts[1] for pts in graph_pts]

    new_object.x_min, new_object.x_max = table.values_range()
    new_object.y_min = min(y_vals)
    new_object.y_max = max(y_vals)
    new_object.pts = graph_pts
    new_object.orig = table.frequency_all()
    new_object.dice = table.get_list()
    return new_object

def make_plot_obj_dic(plot_obj):
    '''takes a PlotObject and converts attr to dictionary for json'''
    out = {}
    properties = plot_obj.__dict__.keys()
    for prop in properties:
        val = getattr(plot_obj, prop)
        if isinstance(val, list):
            out[prop] = val[:]
        else:
            out[prop] = val
    out['dice'] = [(repr(die), num) for die, num in out['dice']]
    return out

def make_plot_obj(plot_obj_dic):
    '''takes a plot_obj_dic (from json.loads) and makes a PlotObject'''
    new = PlotObject()
    for attr, val in plot_obj_dic.items():
        if attr == 'dice':
            new.dice = parse_dice(plot_obj_dic['dice'])
        elif attr == 'pts' or attr == 'orig':
            new_val = [(pair[0], pair[1]) for pair in val]
            setattr(new, attr, new_val)
        else:
            setattr(new, attr, val)
    return new
    
def make_history_json(history):
    '''takes a list of PlotObjects, converts to list of dictionary and returns
    a json  string'''
    new_list = []
    for p_obj in history:
        new_list.append(make_plot_obj_dic(p_obj))
    return json.dumps(new_list)
    
def make_history(json_string):
    '''takes a json string and converts to a list of PlotObjects'''
    to_convert = json.loads(json_string)
    out = []
    for plot_obj_dic in to_convert:
        out.append(make_plot_obj(plot_obj_dic))
    return out

def write_history(history):
    '''takes a history and writes it to history.txt'''
    with open('history.txt', 'w') as to_write:
        to_write.write(make_history_json(history))
        
def read_history():
    '''returns a history from file or an empty list if no history. just in case,
    writes an empty list for if anything got corrupted'''
    try:
        to_read = open('history.txt', 'r')
        json_string = to_read.read()
        to_read.close()
        return make_history(json_string)
    except IOError:
        return []
    finally:
        write_history([])
    
def write_table(table):
    '''takes a table and writes to table.txt'''
    with open('table.txt', 'w') as to_write:
        to_write.write(make_table_json(table))
        
def read_table():
    '''returns a table from file or an empty table if no file. just in case,
    writes an empty table if anything got corrupted.'''
    try:
        to_read = open('table.txt', 'r')
        json_string = to_read.read()
        to_read.close()
        return make_table(json_string)    
    except IOError:
        return ds.DiceTable()
    finally:
        write_table(ds.DiceTable())  
    
        


