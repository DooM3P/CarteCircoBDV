import pandas as pd 

def import_txt_file(file_path, elections, tour, encoding='latin-1', delimiter=';'):
    def get_max_columns(csv_file_path):
        max_columns = 0
        with open(csv_file_path, 'r', encoding=encoding) as file:
            for line in file:
                columns = line.strip().split(delimiter)
                max_columns = max(max_columns, len(columns))
        return max_columns

    def adjust_column_headers(column_headers, max_columns):
        iteration = 2
        while len(column_headers) < max_columns:
            last_8 = column_headers[-8:]
            last_8 = [f"{name.split('_')[0]}_{iteration}" for name in last_8]
            column_headers.extend(last_8)
            iteration += 1
            column_headers = column_headers[:max_columns]
        return column_headers

    header = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter, nrows=1)
    column_names = list(header.columns)
    max_columns = get_max_columns(file_path)
    adjusted_column_headers = adjust_column_headers(column_names, max_columns)

    data = pd.read_csv(
        file_path,
        encoding=encoding,
        delimiter=delimiter,
        header=None, 
        names=adjusted_column_headers,
        skiprows=1,
        low_memory=False
    )

    data.insert(0, 'Elections', elections)
    data.insert(1, 'Tour', tour)
   
    return data

def process_and_merge_scores(df):
    # Identify fixed columns and candidate columns
    fixed_columns = df.columns[:23].to_list()
    candidate_columns = [
        'N°Panneau', 'Sexe', 'Nom', 'Prénom', 'Nuance', 'Voix', '% Voix/Ins', '% Voix/Exp'
    ]

    # Prepare id_vars and value_vars for melting
    id_vars = ['Code de la commune', 'Code du b.vote']
    value_vars = [f'{col}_{i}' if i > 1 else col for i in range(1, 23) for col in candidate_columns]

    # Select columns from the DataFrame
    df_selected = df[id_vars + value_vars]

    # Melt the DataFrame
    df_melted = df_selected.melt(id_vars=id_vars, value_vars=value_vars, var_name='candidate_info', value_name='value').dropna(axis=0, how='all', subset=['value'])

    # Extract candidate_num from candidate_info
    df_melted['candidate_num'] = df_melted['candidate_info'].str.extract(r'(\d+)$').fillna(1).astype(int)

    # Extract attribute from candidate_info
    df_melted['attribute'] = df_melted['candidate_info'].str.replace(r'_\d+$', '', regex=True)

    # Pivot the DataFrame
    df_pivot = df_melted.pivot_table(index=id_vars+['candidate_num'], columns='attribute', values='value', aggfunc='first').reset_index()

    # Rename columns
    df_pivot.columns.name = None

    # Reorder columns
    df_pivot = df_pivot[id_vars + candidate_columns]

    df = df[fixed_columns]

    # Merge with the original DataFrame
    df_merged = df.merge(df_pivot, on=id_vars, how='left')

    return df_merged

def process_and_merge_scores_eur(dfi):
    # Create a copy of the input DataFrame
    df = dfi.copy()
    
    # Identify fixed columns
    fixed_columns = df.columns[:23].to_list()
    
    # Rename columns by removing ' 1' at the end
    df.rename(columns={col: col[:-2] for col in df.columns if col.endswith(' 1')}, inplace=True)
    
    # Candidate columns without ' 1'
    candidate_columns = [
        'Numéro de panneau', 'Nuance liste', 'Libellé abrégé de liste', 'Libellé de liste', 
        'Voix', '% Voix/inscrits', '% Voix/exprimés', 'Sièges'
    ]
    
    # Prepare id_vars and value_vars for melting
    id_vars = ['Code commune', 'Code BV']
    value_vars = [f'{col} {i}' if i > 1 else col for i in range(1, 39) for col in candidate_columns]

    # Ensure all value_vars are in the DataFrame
    value_vars = [var for var in value_vars if var in df.columns]

    # Select columns from the DataFrame
    df_selected = df[id_vars + value_vars]

    # Melt the DataFrame
    df_melted = df_selected.melt(id_vars=id_vars, value_vars=value_vars, var_name='candidate_info', value_name='value').dropna(subset=['value'])

    # Extract candidate_num from candidate_info
    df_melted['candidate_num'] = df_melted['candidate_info'].str.extract(r'(\d+)$').fillna(1).astype(int)

    # Extract attribute from candidate_info
    df_melted['attribute'] = df_melted['candidate_info'].str.replace(r' \d+$', '', regex=True)

    # Pivot the DataFrame
    df_pivot = df_melted.pivot_table(index=id_vars + ['candidate_num'], columns='attribute', values='value', aggfunc='first').reset_index()

    # Rename columns
    df_pivot.columns.name = None

    # Ensure candidate_columns are in the correct order
    pivot_columns = id_vars + ['candidate_num'] + candidate_columns
    df_pivot = df_pivot.reindex(columns=pivot_columns)

    df = df[fixed_columns]
    # Merge with the original DataFrame
    df_merged = df.merge(df_pivot, on=id_vars, how='left')

    return df_merged