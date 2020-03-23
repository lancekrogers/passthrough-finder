import pandas as pd
import os
import glob
import ntpath
import ctypes
from .helper_functions import *

def sort_csv_files():
    '''
    This function function sorts csv files in the CSV_FILES
    directory and creates a dictionary of the paths.
    '''
    def find_csv_files(path_to_csv='CSV_FILES'):
        cwd = os.getcwd() #current working directory
        if cwd.endswith('CSV_FILES'):
            extension = 'csv'
            result = [os.getcwd() + '\\' + i for i in
                      glob.glob('*.{}'.format(extension))]
            os.chdir('..')
            return result
        else:
            os.chidr(path_to_csv)
            extension = 'csv'
            result = [os.getcwd() + '\\' + i for i in
                      glob.glob('*.{}'.format(extension))]
            os.chdir('..')
            return result

    def create_hash_of_files(results):
        '''
        This function takes the results from the find_csv_files() function
        and create a dictionary spliting the derived and passthrough files so 
        they can be easily called without having to sort multiple times.
        '''
        path_dict = {}
        for path in results:
            name = path.split('_derived_fields.csv')[0]
                    .split('_passthrough_fields.csv')[0]
                    .split('_joined_fields.csv')[0].split('\\')[-1]
            name = name.split('_from_logic.csv')[0]
            path_dict[name] = {"passthrough": [], "joined": [], 
                               "from_logic": []}
        for path in results:
            if path.endswith('derived_fields.csv')
                name = path.split('_derived_fields.csv')[0].split('\\')[-1]
                path_dict[name]['derived'] = path
            if path.endswith('passthrough_fields.csv'):
                name = path.split('_passthrough_fields.csv')[0].split('\\')[-1]
                path_dict[name]['passthrough'] = path
            if path.endswith('joined_fields.csv'):
                name = path.split('_joined_fields.csv')[0].split('\\')[-1]
                path_dict[name]['joined'] = path
            if path.endswith('from_logic.csv'):
                name = path.split('_from_logic.csv')[0].split('\\')[-1]
                path_dict[name]['from_logic'] = path
        results = find_csv_files()
        hashs = create_hash_of_files(results)
        return hashs


def csvs_to_excel(path_to_passthrough,
                  path_to_derived, 
                  path_to_joined,
                  path_to_from_logic):
    '''
    Takes a path for 3 csv files and puts them in a single excel document.
    '''
    date = date_string()
    passthrough_df = pd.read_csv(path_to_passthrough).fillna('Null')
                        .sort_values(['From', 'Passthroughs', 'Alias'])
    derived_df = pd.read_csv(path_to_derived).fillna('Null')
    joined_df = pd.read_csv(path_to_joined).fillna('Null')
                .sort_values(['From', 'Joined PDEs', 'Alias'])
    from_lg_df = pd.read_csv(path_to_joined).fillna('Null')
    file_name = 'EXCEL_FILES/' +
    ntpath.basename(path_to_passthrough).replace('_passthrough_fields.csv',
                                                 '_passthrough_&_derived_{}.xlsx'.format(
                                                     date))
    write = pd.ExcelWriter(file_name)
    passthrough_df.to_excel(writer, 'Select Passthrough', index=False)
    derived_df.to_excel(writer, 'Select Derived', index=False)
    joined_df.to_excel(writer, 'From Logic', index=False)
    writer.sheets['Select Passthrough'].column_dimensions['A'].width = 40
    writer.sheets['Select Passthrough'].column_dimensions['B'].width = 40
    writer.sheets['Select Passthrough'].column_dimensions['C'].width = 40
    writer.sheets['Select Derived'].column_dimensions['A'].width = 40
    writer.sheets['Select Derived'].column_dimensions['B'].width = 40
    writer.sheets['Select Derived'].column_dimensions['C'].width = 40
  
    writer.sheets['Left-Join Passthrough'].column_dimensions['A'].width = 40
    writer.sheets['Left-Join Passthrough'].column_dimensions['B'].width = 40
    writer.sheets['Left-Join Passthrough'].column_dimensions['C'].width = 40
    
    writer.sheets['From Logic'].column_dimensions['A'].width = 20
    writer.sheets['From Logic'].column_dimensions['B'].width = 40
    writer.sheets['From Logic'].column_dimensions['C'].width = 40
    writer.sheets['From Logic'].column_dimensions['D'].width = 40
    writer.sheets['From Logic'].column_dimensions['E'].width = 40

    writer.save()
    print('{} Updated'.format(file_name))
    return None

def update_excel_files():
    sorted_csv_files = sort_csv_files()
    for x in sorted_csv_files:
        try:
            csvs_to_excel(sorted_csv_files[x]['passthrough'],
                          sorted_csv_files[x]['derived'],
                          sorted_csv_files[x]['joined'],
                          sorted_csv_files[x]['from_logic'])
        except Exception as e:
            print(e)
            date = date_string()
            file_name = 'EXCEL_FILES/' + ntpath.basename(
                sorted_csv_files[x]['passthrough'])
            .replace('_passthrough_fields.csv',
                     '_passthrough_&_derived_{}.xlsx'.format(date))
            message_box("ERROR", "Close Excel File:\n {} \n Click ok when"
                        "done,otherwise try again.".format(file_name), 1)
            print("Close Excel file:\n {} \n and try again".format(file_name))
            try:
                csvs_to_excel(sorted_csv_files[x]['passthrough'],
                              sorted_csv_files[x]['derived'],
                              sorted_csv_files[x]['joined'],
                              sorted_csv_files[x]['from_logic'])
            except:
                continue
    return None

def send_excel_to_desktop():
    log = {}
    mkdir = os.system(r'mkdir'
                      r' C:\USERS\%username%\Desktop\Passthrough_Excel_Files')
    copy = os.system('copy {} {}'.format('EXCEL_FILES',
                                         r'C:\USERS\%username%\Desktop\Passthrough_Excel_Files'))
    log['mkdir'] = system_error_decoder(mkdir)
    log['copy'] = system_error_decoder(copy)
    return log

def delete_csv():
    os.chdir('EXCEL_FILES')
    excel_files = [os.getcwd() + '\\' + i for i in glob.glob('*.{}'.format(
        'xlsx'))]
    for file in excel_files: os.remove(file)
    return log

def delete_excel():
    os.chdir('CSV_FILES')
    csv_files = [os.getcwd() + '\\' + i for i in
                 glob.glob('*.{}'format('csv'))]
    for file in csv_files: os.remove(file)
    os.chdir('..')

if __name__ == '__main__':
    update_excel_files()











    














    
