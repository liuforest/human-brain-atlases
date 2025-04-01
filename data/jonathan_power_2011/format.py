# %% load a dataframe of Johnathan Power's 2011 atlas. 
# - use original compiled src file from via https://www.jonathanpower.net/2011-neuron-bigbrain.html
# - 264 regions stripped down to 227

import pandas as pd

def get_atlas_df(src: str):
    
    # excel columns to df labels
    cols = {'A': 'ROI',
            'G': 'mni_x_coord',
            'H': 'mni_y_coord',
            'I': 'mni_z_coord',
            'AF': 'RSN_label_numeric',
            'AK': 'RSN'}

    # read the excel file
    df = pd.read_excel(src, usecols = ', '.join(cols.keys()), names=cols.values(), header=1, engine='openpyxl')
    
    return df

def format_atlas(df: pd.DataFrame):

    # combine x, y, z coords & drop the individual columns
    df['mni_coords'] = df[['mni_x_coord', 'mni_y_coord', 'mni_z_coord']].apply(tuple, axis=1)
    df.drop(columns=['mni_x_coord', 'mni_y_coord', 'mni_z_coord'], inplace=True)

    # drop uncertain & cerebellar regions
    df = df[~df['RSN'].isin(['Uncertain', 'Cerebellar', 'Memory retrieval?'])]

    # rename columns containing 'somato to 'sensorimotor'
    df['RSN'] = df['RSN'].apply(lambda entry: f'Sensorimotor' if 'somato' in entry.lower() else entry)

    # rename columns containing 'attention' to 'attention'
    df['RSN'] = df['RSN'].apply(lambda entry: f'Attention' if 'attention' in entry.lower() else entry)

    # change all spaces and dashes to underscore, and lowercase everything
    df['RSN'] = df['RSN'].apply(lambda entry: entry.replace(" ", "_").replace("-", "_").lower())

    # rearrange by count of RSN occurrences and ROI
     
    df['rsn_count'] = df['RSN'].map(df['RSN'].value_counts())
    df = df.sort_values(by=['rsn_count', 'ROI'], ascending=False).reset_index(drop=True)
    
    # delete rsn count column
    del df['rsn_count']

    return df



# %% run script as main
if __name__ == '__main__':
    atlas_src = f'src/Neuron_consensus_264.xlsx'
    df = get_atlas_df(atlas_src)
    df = format_atlas(df)
    
    # save df to csv file in current directory
    df.to_csv('atlas.csv', index=False)
    
# %%
