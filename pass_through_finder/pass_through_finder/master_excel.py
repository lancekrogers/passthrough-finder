import pandas as pd
import numpy as np
import os
import glob
import time
import datetime
from .helper_functions import *


def find_output_files(output_file_directory='APPLICATION_OUTPUT',
                      file_extension='xlsx'):
    cwd = os.getcwd()
    if cwd.endswith(output_file_directory):
        result = [os.getcwd() + '\\' + i for i in glob.glob('*.{}'.format(
            file_extensions))]
        os.chdir('..')
        return result
    else:
        os.chdir(output_file_directory)
        result = [os.getcwd() + '\\' + i for i in glob.glob('*.{}'.format(
            file_extension))]
        os.chdir('..')
        return result


def map_names_to_paths(list_of_paths):
    mapping = ()
    for path in list_of_paths:
        name = path.split('_passthrough_&_derived')[0].split(
            '\\')[-1].replace('_vw', '')
        mapping[name] = []
    for path in list_of_paths:
        name =  path.split('_passthrough_&_derived')[0].split(
            '\\')[-1].replace('_vw', '')
        mappin[name].append(path)
    try:
        check_path_mapping(mapping)
        return mapping
    except:
        print('Check to make sure that there is only one file per view')
        return "ERROR: Similar view files"


def check_path_mapping(mapping):
    for x in mapping:
        n = 0
        for a in mapping[x]: n += 1
        if n > 1:
            raise Exception


def passthrough_tab(path_to_file):
    excel_file = pd.ExcelFile(path_to_file)
    return excel_file.parse('Select Passthrough')


def derived_tab(path_to_file):
    excel_file = pd.ExcelFile(path_to_file)
    return excel_file.parse('Select Derived')


def join_tab(path_to_file):
    excel_file = pd.ExcelFile(path_to_file)
    return excel_file.paarse('Left-Join Passthroughs')


def all_excel_files(path_map):
    pt_master = pd.DataFrame(columns={'View', 'Passthroughs', 'From', 'Alias'})
    dr_master = pd.DataFrame(columns={'View', 'Derived PDEs', 'SOURCE PDE',
                                      'SOURCE TABLE'})
    jn_master = pd.DataFrame(columns={'View', 'Joined PDEs', 'From', 'Alias'})
    for file in sorted(path_map):
        pt_df = passthrough_tab(path_map[file][0])
        dr_df = derived_tab(path_map[file][0])
        jn_df = join_tab(path_map[file][0])
        pt_df['View'] = file
        dr_df['View'] = file
        jn_df['View'] = file
        pt_master = pd.concat([pt_master, pt_df]).reset_index(drop=True)
        dr_master = pd.concat([dr_master, dr_df]).reset_index(drop=True)
        jn_master = pd.concat([jn_master, jn_df]).reset_index(drop=True)
    pt_master = pt_master[['View', 'Passthroughs', 'From',
                           'Alias']].copy().sort_values(
                               ['View', 'From', 'Passthroughs', 'Alias'])
    dr_master = dr_master[['View', 'Derived PDEs', 'SOURCE TABLE']].copy()
    jn_master = jn_master[['View', 'Joined PDEs', 'From',
                           'Alias']].copy().sort_values(['View', 'From',
                                                         'Joined PDEs',
                                                         'Alias'])
    return pt_master, dr_master, jn_master


def create_master_excel_file():
    date = date_string()
    output_paths = find_output_files(output_file_directory='EXCEL_FILES')
    views_and_paths = map_names_to_paths(output_paths)
    passthrough_df, derived_df, joined_df = all_excel_files(views_and_paths)
    file_name = 'EXCE_FILES/master_passthrough_derived_{}.xlsx'.format(date)
    writer = pd.ExcelWriter(file_name)
    passthrough_df.to_excel(writer, 'Select Passthrough', index=False)
    derived_df.to_excel(writer, 'Select Derived', index=False)
    joined_df.to_excel(writer, 'Left-Join Passthroughs', index=False)
    writer.save()
    print('{} Updated'.format(file_name))
    return None


if __name__ == '__main__':
    create_master_excel_file()
