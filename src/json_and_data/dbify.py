# dbify.py

# - json2database.json2database.run()  --   runs input and output files
# - json2database.recursive.process()  --   wraps the 'dbification' process
# - json2database.recursive.dbify_json_dict()  --   wraps the queue of dbify
#  dbify.py can become a new package in itself. json_and_data would use that.

import json
import os

# import JSON validation
# todo Once the following packages are available from PyPI, change these
#  imports:  json_and_validation
from json_and_validation import *


###
# Working version.
def dbify_queue_of_tuples(tuples_of_json_dicts: list,
                          table_id: int) -> list:
    """ Recursive algorithm to split a nested JSON object into several,
    flat JSON objects. Flat JSON objects have no JSON objects nested within.
    Returns a list of tuples: the first element is the 'name' of the JSON
    object in this tuple; the second element is the flat JSON object. """
    if len(tuples_of_json_dicts) == len([]):
        return []
    output_list = []
    add_to_queue = []
    dbified_json_dict = {}
    for current_tuple in tuples_of_json_dicts:
        table_name, json_dict = current_tuple
        dbified_json_dict.clear()
        for current_key in json_dict.keys():
            current_value = json_dict[current_key]
            if type(current_value) != dict:
                dbified_json_dict[current_key] = current_value
            else:
                # here current_value is a nested JSON dictionary:
                # then simplify the current JSON dictionary with the record
                # {key: key_table_id.json} and add a new pair (
                # key_table_id.json, current_value) to the queue
                table_id += 1
                nested_table_name = "" + current_key + "_table_" + str(
                    table_id) + ".json"
                dbified_json_dict[current_key] = nested_table_name
                add_to_queue.append((nested_table_name, current_value))
        output_list.append((table_name, dbified_json_dict.copy()))
    output_list.extend(dbify_queue_of_tuples(add_to_queue, table_id))
    return output_list


def dbify_json_dict(json_dict: dict) -> list:
    """ Bootstraps the dbify processing . """
    tuples_of_json_dicts = [("root", json_dict)]
    return dbify_queue_of_tuples(tuples_of_json_dicts, 0)


def dbify(input_dir: str = './data/json/input/',
          output_dir: str = './data/json/output/') -> None:
    """ Reads JSON files from input_dir, skipping files with invalid JSON
    syntax, and outputs the dbified version of each file into output_dir. """
    # Getting the list of valid JSON input files
    list_of_input_files = os.listdir(input_dir)
    list_of_valid_json_files = [
        file
        for file in list_of_input_files if is_valid_json_file(
            input_dir + file
        )
    ]
    print()
    print(" > Found %s valid JSON files." % len(list_of_valid_json_files))

    # Writing dbified JSON files from each valid input file
    for input_filename in list_of_valid_json_files:
        print()
        print("  >>  dbifying %s..." % input_filename)

        # load input_filename as dict with json.load
        input_json_dict: dict
        with open(input_dir + input_filename, 'r') as input_file:
            input_json_dict = json.load(input_file)

        # output a dbified dict into a result dict
        dbified_json_dict = dbify_json_dict(input_json_dict)

        # dump the dbified dict into the output_filename with json.dump
        dbified_prefix = 'dbified_'
        output_filename = output_dir + dbified_prefix + input_filename
        with open(output_filename, 'w') as output_file:
            json.dump(dbified_json_dict,
                      output_file,
                      indent=4)
    print(" > Operation complete.")


if __name__ == "__main__":
    print("Running dbify.py directly.")
    dbify()
