'''for sending and retrieving main info to file'''

import json
from cPickle import UnpicklingError
import dicetables as dt
import numpy as np




def make_table_json(dtable):
    '''takes a table and converts it into json str of '[dice_list, freqs]' '''
    d_list = [(repr(die), num) for die, num in dtable.get_list()]
    return json.dumps([d_list, dtable.frequency_all()], indent=2)
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
                out.append((dt.ModWeightedDie(input_dic, mod), num))
            else:
                out.append((dt.WeightedDie(input_dic), num))
        else:
            numbers = string[string.find('(') + 1: string.find(')')]
            if 'Mod' in string:
                size, mod = numbers.split(',')
                out.append((dt.ModDie(int(size), int(mod)), num))
            else:
                out.append((dt.Die(int(numbers)), num))
    return out

def make_table_basis(json_str):
    '''takes a json_str of a table and makes a table'''
    dice_dic, tuples = json.loads(json_str)
    dice_list = parse_dice(dice_dic)
    return dice_list, tuples

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

def make_plot_obj_dic(plot_obj):
    '''takes a plot_obj dic and makes a deep-ish copy and preps dicelist
    for json'''
    out = {}
    for key, val in plot_obj.items():
        if isinstance(val, list):
            out[key] = val[:]
        else:
            out[key] = val
    out['dice'] = [(repr(die), num) for die, num in out['dice']]
    return out

def make_plot_obj(plot_obj_dic):
    '''takes a plot_obj_dic (from json.loads) and makes a PlotObject'''
    new = {}
    for attr, val in plot_obj_dic.items():
        if attr == 'dice':
            new['dice'] = parse_dice(plot_obj_dic['dice'])
        elif attr == 'pts' or attr == 'orig':
            new_val = [(pair[0], pair[1]) for pair in val]
            new[attr] = new_val
        else:
            new[attr] = val
    return new

def make_history_json(history):
    '''takes a list of PlotObjects, converts to list of dictionary and returns
    a json  string'''
    new_list = []
    for p_obj in history:
        new_list.append(make_plot_obj_dic(p_obj))
    return json.dumps(new_list, indent=2)

def make_history(json_string):
    '''takes a json string and converts to a list of PlotObjects'''
    to_convert = json.loads(json_string)
    out = []
    for plot_obj_dic in to_convert:
        out.append(make_plot_obj(plot_obj_dic))
    return out

def write_history(history):
    '''takes a history and writes it to history.txt'''
    with open('history.txt', 'w') as f:
        f.write(make_history_json(history))

def read_history():
    '''returns a history from file or an empty list if no history. just in case,
    writes an empty list for if anything got corrupted'''
    try:
        f = open('history.txt', 'r')
        json_string = f.read()
        f.close()
        return ('ok', make_history(json_string))
    except IOError:
        write_history([])
        return ('no file', [])
    except (TypeError, AttributeError, ValueError):
        write_history([])
        return ('corrupted file', [])


def write_table(table):
    '''takes a table and writes to table.txt'''
    with open('table.txt', 'w') as f:
        f.write(make_table_json(table))

def read_table():
    '''returns a table from file or an empty table if no file. just in case,
    writes an empty table if anything got corrupted.'''
    try:
        f = open('table.txt', 'r')
        json_string = f.read()
        f.close()
        return make_table_basis(json_string)    
    except IOError:
        return [[], [[0, 1]]]


def check_data(plot_obj):
    '''checks history to see if plot_obj has expected data.  if ok, returns 'ok'
    else returns a msg starting with 'error:' '''
    expected = {'y_min':float, 'text':str, 'y_max':float, 'orig':list,
                'x_max':(int, long), 'x_min':(int, long), 'pts':list,
                'dice':list}
    if not isinstance(plot_obj, dict):
        return 'error: not a dict'
    try:
        for key, val_type in expected.items():
            if not isinstance(plot_obj[key], val_type):
                return 'error: {} not {}'.format(key, val_type)
    except KeyError:
        return 'error: missing key'
    msg = 'ok'
    for freq, val in plot_obj['orig']:
        if (not isinstance(freq, (int, long)) or
                not isinstance(val, (int, long))):
            msg = 'error: corrupted "orig"'
    if msg == 'ok':
        for x_pt, y_pt in plot_obj['pts']:
            if not isinstance(x_pt, (int, long)) or not isinstance(y_pt, float):
                msg = 'error: corrupted "pts"'
    if msg == 'ok':
        for die, num in plot_obj['dice']:
            if not isinstance(die, dt.ProtoDie) or not isinstance(num, int):
                msg = 'error: dicelist at ({!r}, {})'.format(die, num)
    return msg
def check_history(history):
    '''checks a history(a non-empty iterable containing plot_objects. to make
    sure it has the correct kind of data. if ok, returns 'ok' else returns a msg
    starting with 'error' '''
    for plot_obj in history:
        msg = check_data(plot_obj)
        if 'error:' in msg:
            break
    return msg

def write_history_np(history):
    '''takes a numpy array and writes it'''
    np.save('numpy_history', history)

def read_history_np():
    '''tries to find the np file and read it returns a np array and a message'''
    empty_hist = np.array([], dtype=object)
    try:
        history = np.load('numpy_history.npy')
        if history.size:
            msg = check_history(history)
            if 'error:' in msg:
                history = empty_hist
        else:
            if history.dtype != np.dtype('O'):
                msg = 'error: wrong array type'
                history = empty_hist
            else:
                msg = 'ok: no history'
    except IOError:
        history = empty_hist
        msg = 'error: no file'
    except (UnpicklingError, AttributeError, EOFError, ImportError,
            IndexError):
        history = empty_hist
        msg = 'error: file corrupted'
    return msg, history  

