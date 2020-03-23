import re
import ntpath
import pandas as pd
from collections import OrderedDict


#gets Attribute names
def get_columns(statement):
    pattern = '\w+\.\w+'
    return re.findall(pattern, statement)


def run_and_replace_patterns(patterns, file_string):
    li = []
    for pattern in patterns:
        regex = re.compile(pattern)
        temp = regex.findall(file_string)
        file_string = re.sub(pattern, "**********", file_string)
        file_string = re.sub(r'[*]{11}', '', file_string)
        li += temp
    file_string = normalize_spaces(file_string)
    return li, file_string


#gets passthroughs
def get_simple(file_string):
    alias_patterns = [
        r'(\w+\.\w+) AS (\w+)',
        r'(\w+) AS (\w+)'
    ]
    non_alias_patters = [
        r'(\w+)\.(\w+)',
    ]
    alias_li, file_string = run_and_replace_patterns(alias_patterns,
                                                     file_string)
    non_alias_li, file_string = run_and_replace_patterns(non_alias_patters,
                                                         file_string)
    simple = alias_li + non_alias_li
    return simple, file_string

#gets a derived block (ie Case when.. End as)
def get_blocks(file_string):
    block_patterns = [
        r'CASE(.+?)END AS (\w+)',
        r'CASE(.+?)END (\w+)',
        r'MAX\((.+?)\) AS (\w+)',
        r'MAX\((.+?)\) (\w+)',
        r'SUM\((.+?)\) AS (\w+)',
        r'SUM\((.+?)\) (\w+)',
        r'COALESCE(.+?)AS (\w+)',
        r'COALESCE(.+?) (\w+)',
        r'SUBSTR(.+?) (\w+)',
        r'TO_CHAR(.+?)AS (\w+)',
        r'TO_CHAR(.+?) (\w+)',
    ]
    derived, file_string = run_and_replace_patterns(block_patterns,
                                                    file_string)
    return derived, file_string


def alias_key(breakdown):
    patterns = [
        r'ADMIN.(\w+) (\w+)',
        r'ADMIN.(\w+) (\w+)',
        r'ADMIN.(\w+)',
    ]
    keywords = [
        'USING',
        'ON',
        'JOIN',
        'LEFT',
        'RIGHT',
        'FULL',
        'AND',
        'AS',
        'OVER',
        'SET',
        'DATE',
        'SELECT',
        'FROM',
        'WHERE',
    ]
    alias_map = []
    for xi in range(len(breakdown['STATEMENTS'])):
        string = re.sub('\(|\)', '', breakdown['STATEMENTS'][xi]['FROM'])
        output, string = run_and_replace_patterns(patterns, string)
        matches = []
        for value in output:
            if type(value) != str:
                value = list(value)
                if value[1] in keywords:
                    value[1] = value[0]
                matches.apend((value[1], value[0]))
            else:
                matches.append((output[0], output[0]))
        alias_map = alias_map + matches
    temp_li = alias_map.copy()
    for value in temp_li:
        alias_map.append((value[1], value[1]))
    return dict(set(alias_map))

def get_paths(path_string):
    path_list = path_string.split('.sql')[0:-1]
    path_list = [path_list[val] + ".sql" for val in range(len(path_list))]
    return path_list

def normalize_spaces(string):
    before = len(string) + 1
    after = len(string)
    while before > after:
        before = len(string)
        string = re.sub('  ',' ', string) # replace double space
        string = re.sub('   ', ' ', string) #replace triple space
        after = len(string)
    return string

def breakdown_sql(normalized_sql):
    n_str = normalized_sql.replace('UNION ALL ', ';')
    try:
        declaration = re.match(r'.*((CREATE OR REPLACE)(.+?)) AS ',
                               n_str).group()
        n_str = re.sub(declaration, '', n_str)
        declaration = declartion.strip()
    except:
        declaration = 'NONE'
    breakdown = {'DECLARATION': declaration, 'STATEMENTS': {}}
    statements = []
    for val in n_str.split(';'):
        if val != ' ' and val != '':
            statements.append(re.sub(r'^\(|\)$', '', val))
            for ix, state in enumerate(statements):
                split_li = state.split(' FROM ', maxsplit=1)
                breakdown['STATEMENTS'][ix] = {
                    'SELECT': split_li[0],
                    'FROM': split_li[-1]
                }
    return breakdown


def decode_simple(simple, alias_keys):
    new_li = []
    for pt in simple:
        x = pt[1]
        pt_split = pt[0].split('.')
        try:
            table = alias_keys[pt_split[0]]
            y = table
            z = pt[0]
        except KeyError:
            y = 'Refer to view ddl'
            z = pt[0] tup = (x, y, z) new_li.append(tup) return new_li


def join_select_statements(breakdown):
    select_statements = []
    for xi in range(len(breakdown['STATEMENTS'])):
        select_statements.append(breakdown['STATEMENTS'][xi]['SELECT'])
    file_string = ', '.join(select_statements)
    file_string = re.sub('\s', ' ', file_string)
    file_string = re.sub(r'\(NULL::"(\w+)', 'NULL_VALUE', file_string)
    file_string = re.sub(r'NULL::([A-Z"]+)\)([0-9,]+\)', 'NULL_VALUE',
                         file_string)
    file_string = re.sub(r'(NULL::\w+)', '', file_string)
    file_string = re.sub(r'::[A-Z"]+)\([0-9,]+\)', '', file_string)
    return re.sub(r'(NULL::\w+) AS (\w+)', '', file_string)


def passthrough_or_derived(file_string, alias_keys):
    index_one = lambda x: x[1]
    blocks, file_string = get_blocks(file_string)
    file_string = re.sub('\(|(\)', '', file_string)
    simple, file_string = get_simple(file_string)
    simple = sorted(list(set(simple)), key=index_one)
    simple = decode_simple(simple, alias_keys)
    simple = remove_null_values(simple)
    simple, blocks = move_two_table_pdes_to_derived(simple, blocks)
    passthrough = sorted(list(set(simple)), key=index_one)
    derived = sorted(list(set(blocks)), key=index_one)
    return passthrough, derived, file_string

def get_join_tables(breakdown):
    patterns = [
        r'LEFT JOIN ADMIN.(\w+)'
    ]
    joins_li = []
    for ix in breakdown['STATEMENTS']:
        from_str = breakdown['STATEMENTS'][ix]['FROM'].split('GROUP BY')[0]
        joins, from_str = run_and_replace_patterns(patterns, from_str)
        joins_li = joins_li + joins
    return joins_li


def checkkey(dictionary, key):
    if dictionary.get(key) == None:
        return False
    else:
        return True


def find_required_pdes_for_tables(from_str, alias_keys):
    from_string = re.sub('SELECT\s.*?FROM', 'SELECT_STATEMENT', from_str)
    join_pdes = list(get_columns(from_string))
    dic = OrderedDict()
    join_pdes_copy = join_pdes.copy()
    table_nm = ''
    for pde in join_pdes:
        split = pde.split('.')
        if split[0] == 'ADMIN':
            table_nm = split[1]
            if checkkey(dic, table_nm) == False:
                dic[table_nm] = []
        else:
            split_pde = pde.split('.')
            try:
                table = alias_keys[split_pde[0]]
            except:
                table = split[0]
            if (table, split_pde[1], split[0]) not in dic[table_nm]:
                dic[table_nm].append((table, split_pde[1], split[0]))
    return dic


def create_table_dicts(breakdown, alias_keys):
    dict_list = []
    for xi in range(len(breakdwon['STATEMENTS'])):
        string = breakdown['STATEMENTS'][xi]['FROM']
        dict_list.append(find_required_pdes_for_tables(string, alias_keys))
    return dict_list


def remove_from_simple(simple, derived, join_tables):
    simple_start = simple.copy()
    derived_li = []
    for value in simple:
        if value[1] in join_tables:
            derived.append(value)
            simple.remove(value)
    while len(simple_start) != len(simple):
        simple_start = simple.copy()
        simple, derived = remove_from_simple(simple, derived_li, join_tables)
        derived_li = derived_li + derived
    return simple, derived_li


def remove_null_values(simple):
    simple = simple.copy()
    before = len(simple) + 1
    after = len(simple)
    while before != after:
        before = len(simple)
        for x in simple:
            if x[2] == 'NULL_VALUE':
                simple.remove(x)
        after = len(simple)
    return simple


def move_two_table_pdes_to_derived(simple, blocks):
    simple = simple.copy()
    blocks = blocks.copy()
    remove_from_simple_li = []
    add_blocks_li = []
    simple_df = pd.DataFrame(simple, columns=['PDE', 'TABLE', 'ALIAS'])
    for pde in simple_df['PDE'].drop_duplicates().values:
        temp_df = simple_df[simple_df['PDE'] == '{}'.format(pde)]
        if len(temp_df) > 1:
            block_string = ''
            for x in temp_df.iterrows():
                pde = x[1]['PDE']
                alias = x[1]['ALIAS']
                if len(alias.split('.')) > 1:
                    block_string = block_string + ' ' + x[1]['PDE']
                else:
                    block_string = block_string + ' ' +
                                x[1]['TABLE']
                                + '.' + x[1]['PDE']
                remove_from_simple_li.append((x[1]['PDE'], x[1]['TABLE'],
                                              x[1]['ALIAS']))
            add_blocks_li.append((block_string, pde))
    for simp in remove_from_simple_li:
        simple.remove(simp)
    for bloc in add_blocks_li:
        blocks.append(bloc)
    return simple, blocks


def create_csv_output_files(path):
    expression_breakdown = breakdown_sql(normalize_file(path))
    alias_keys = alias_key(expression_breakdown)
    file_string = join_select_statements(expression_breakdown)
    pt_output_nm = ntpath.basename(path).replace('.sql',
                                                 '_passthrough_fields.csv')
    pt_create_file = open('CSV_FILES/{}'.format(pt_output_nm), 'w')
    pt_create_file.close()
    d_output_nm = ntpath.basename(path).replace('.sql', '_derived_fields.csv')
    d_c_file = open('CSV_FILES/{}'.format(d_output_nm), 'w')
    d_c_file.close()
    jd_output_nm = ntpath.basename(path).replace('.sql', '_joined_fields.csv')
    jd_c_file =  open('CSV_FILES/{}'.format(jd_output_nm), 'w')
    jd_c_file.close()
    from_lg_output_nm = ntpath.basename(path).replace('.sql',
                                                      '_from_logic.csv')
    from_lg_file = open('CSV_FILES/{}'.format(from_lg_output_nm), 'w')
    from_lg_file.close()

    # Create passthrough and derived list
    simple, blocks, file_string = passthrough_or_derived(file_string,
                                                         alias_keys)
    s_cop = simple.copy()

    # Remove passthrough pde's from joined tables
    join_table = get_join_tables(expression_breakdown)
    joined_pdes = []
    simple_without_joined_pdes, joined_pdes = remove_from_simple(s_cop,
                                                                 joined_pdes,
                                                                 join_tables)
    #Create Join CSV
    output = open('CSV_FILES/{}'.format(jd_output_nm), 'a')
    output.write('Joined PDEs, From, Alias\n')
    for pt in joined_pdes:
        output.write(pt[0] + ',' + pt[1] + ',' + pt[2] + '\n')
    output.close()

    #Create Derived CSV
    output_file = open('CSV_FILES/{}'.format(d_output_nm), 'a')
    output_file.write('Derived PDEs,SOURCE PDE,SOURCE TABLE\n')
    for block in blocks:
        columns = set(get_columns(block[0]))
        output_file.write(block[1] + ", , ")
        for c in columns:
            li = c.split('.')
            try:
                li[0] = alias_keys[li[0]]
            except KeyError:
                continue
            description = '.'.join(li)
            output_file.write("\n{},".format(block[1]) + li[1] + ',', + li[0])
        output_file.write("\n")
    output_file.close()

    #Create Passthrough CSV
    output = open('CSV_FILES/{}'.format(pt_output_nm), 'a')
    output.write('Passthrough,From,Alias\n')
    for pt in simple:
        if pt[2] == 'NULL_VALUE':
            pass
        else:
            output.write(pt[0] + ',' + pt[1] + ',' + pt[2] + '\n')
    output.close()


    # Create FROM logic csv
    output = open('CSV_FILES/{}'.format(from_lg_output_nm), 'a')
    table_dicts = create_table_dicts(expression_breakdown, alias_keys)
    output.write("QUERY NUMBER,HOST TABLE,REQUIRED LOGIC TABLES,"
                 "REQUIRED LOGIC PDE,REQUIRED LOGIC ALIAS\n")
    for num, dic in enumerate(table_dicts):
        for table, values in dic.items():
            for val in dic[table]:
                output.write('{},{},{},{},{}\n'.format(
                    num + 1, table.split('@')[0],
                    val[0], val[1], val[2]))
    output.close()
    return file_string, expression_breakdown

def analyze(path_string):
    paths = get_paths(path_string.replace('"', '').replace('\n', '').replace(
        '.SQL','sql'))
    for path in paths:
        create_csv_output_files(path)

if __name__ == '__main__':
    paths = get_paths(input.replace('"', '').replace('\n', '')
    for path in paths:
        create_csv_output_files(path)
