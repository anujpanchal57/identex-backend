import ast
import operator

from datetime import date, datetime
import json

# populates dictionary with specified keys and empty values
from pprint import pprint


def populate_empty_with_keys(dict, *args):
    for key in args:
        dict[key] = "" if key not in dict else dict[key]
    return dict



# sets primary key for the document
def set_primary_key(dict, key):
    if key in dict:
        dict['_id'] = dict[key]
        dict.pop(key, None)
    return dict


# removes specified keys from dictionary
def purge_for_keys(dict, *args):
    try:
        for key in args:
            dict.pop(key, None)
    except Exception as e:
        pass
    return dict


# convert to dict from byte
def convert_from_byte(data):
    return ast.literal_eval(data.decode('utf-8'))


# convert mongo cursor to dict
def convert_mongo_cursor_to_dict(cursor):
    dict = []
    for doc in cursor:
        dict.append(doc)
    return dict.copy()


# initialize dictionary with keys
def intialize_if_null(data, key, intitialize=''):
    if key not in data:
        data[key] = intitialize
    return data


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def date_to_str(search, date_fields=['etd', 'eta', 'ens_cutoff', 'vgm_cut_off', 'vessel_cut_off']):
    for item in search:
        if item in date_fields:
            search[item] = str(search[item]).split(' ')[0]
    return search


def populate_with_keyset(dict, *args):
    for key in args:
        dict[key] = key if key not in dict else dict[key]
    return dict


def index_with_lowest_timestamp(list, timestamp_key='timestamp'):
    result_index, lowest, index = -1, list[0][timestamp_key], 0
    for dict in list:
        if int(dict[timestamp_key]) <= lowest:
            lowest = int(dict[timestamp_key])
            result_index = index
        index += 1
    return result_index


def index_with_highest_timestamp(list, timestamp_key='timestamp'):
    result_index, lowest, index = -1, list[0][timestamp_key], 0
    for dict in list:
        if int(dict[timestamp_key]) >= lowest:
            lowest = int(dict[timestamp_key])
            result_index = index
        index += 1
    return result_index


def swap_position_in_array(array, index1, index2):
    temp = array[index1]
    array[index1] = array[index2]
    array[index2] = temp
    return array


def sort_list_of_dict(array, key):
    if key in ['etd', 'eta']:
        for index in range(0, len(array)):
            array[index]['etd'] = datetime.strptime(array[index]['etd'], '%d-%b-%y')
    array.sort(key=operator.itemgetter(key))
    if key in ['etd', 'eta']:
        for index in range(0, len(array)):
            array[index]['etd'] = array[index]['etd'].strftime('%d-%b-%y')
    return array


def split_into_categories(array, category):
    sort_list_of_dict(array, category)
    final = []
    if len(array)>0:
        current_category = array[0][category]
        splitter = []
        for item in array:
            if item[category] == current_category:
                splitter.append(item)
            else:
                final.append(splitter.copy())
                splitter = []
                current_category = item[category]
                splitter.append(item)
        final.append(splitter)
    return final