import pandas as pd

def find_any_true(values):
    return True in set(values)

def format_for_order(values):
    """Format collection of values as a string and retain order."""
    string_values = [str(x) for x in values]
    text = ', '.join(string_values)
    return text

def format_unique(values):
    """Format unique values as a string, separated by a comma.
    Ignores null values and empty strings.
    """
    string_values = [str(x) for x in values]
    s = set([x for x in string_values if x != '' and x != 'nan'])
    text = ', '.join(s)
    return text

def categorize_serious_charges(row, offense_level_available):
    """Helper function for transform_to_sets().
    Categorizes whether arrest includes a violent charge
    and, if offense level is available, a felony charge.

    Parameters
    ----------

    row : pd.Series
        row in a charge DataFrame representing a single arrest charge

    offense_level_available : bool
        Takes argument passed to transform_to_sets() (default True).

    Returns
    -------
    tuple
    """
    felony = 'unknown'
    if offense_level_available == True:
        if row['_felony_set'] == 'False':
            felony = 'no felony charges'
        elif 'True' in row['_felony_set']:
            felony = 'at least one felony charge'
    if 'True' in row['_violent_set']:
        violent = 'at least one violent charge'
    else:
        violent = 'no violent charge'
    return felony, violent

def transform_to_sets(df, offense_level_available=True):
    """Produce sets of unique values for charges such that each row in the
    resultant dataframe represents a single arrest.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame that should be read in from 04_outputs/ and begin with c01.

    offense_level_available : bool
        Whether charge offense level information is available (default True)

    Returns
    -------
    pd.DataFrame

    """
    set_fields = ['_arrest_id', '_code_type', '_charge_reconstructed', '_charge_description', '_violent']
    if offense_level_available == True:
        set_fields += ['_felony']
    charge_sets = df[set_fields].groupby(['_arrest_id'], dropna=False).agg(format_unique)
    charge_sets.columns = charge_sets.columns.map(lambda x: x + '_set')
    charge_sets.reset_index(inplace=True)
    print('Charge sets produced. Now working on non-procedural charge sets.')
    np_set_fields = ['_arrest_id', '_code_type', '_charge_reconstructed', '_charge_description']
    procedural_fields = ['_warrant', '_fta', '_supervision']
    df['_procedural'] = df[procedural_fields].sum(axis=1) > 0
    non_procedural_charge_sets = (
        df[df['_procedural'] == False][np_set_fields]
        .groupby(['_arrest_id'], dropna=False)
        .agg(format_unique)
    )
    non_procedural_charge_sets.columns = non_procedural_charge_sets.columns.map(
        lambda x: 'np' + x + '_set'
    )
    non_procedural_charge_sets.reset_index(inplace=True)
    print('Now merging procedural and non-procedural charge sets.')
    charge_set_df = pd.merge(
        charge_sets, non_procedural_charge_sets, how='left', validate='1:1'
    )
    print('Now categorizing serious charges.')
    charge_set_df[['_felony', '_violent']] = charge_set_df.apply(
        lambda x: categorize_serious_charges(x, offense_level_available), axis=1, result_type='expand'
    )
    if offense_level_available == True:
        charge_set_df.drop(labels=['_violent_set', '_felony_set'], axis=1, inplace=True)
    else:
        charge_set_df.drop(labels=['_violent_set'], axis=1, inplace=True)
    print('Done!')
    return charge_set_df

def assess_arrest_type(row):
    """Helper function for assess_charges(), which assesses the number of charges that can be described as "procedural" (e.g. failure to appear, supervisioon violation) and compares that to the total charge count. Then it counts a superset of "procedural" charges and other low-level charges like disorderly conduct, and compares that to the total charge count.

    Parameters
    ----------
    row : pd.Series
        Represents a row in a charge DataFrame, and describes a single arrest charge.

    Returns
    -------
    string
    """
    if row['_procedural'] == row['total_charge_count']:
        arrest_type = 'procedural only'
    elif row['_low-level'] == row['total_charge_count']:
        arrest_type = 'low-level only'
    else:
        arrest_type = 'varied charges'
    return arrest_type

def assess_charges(df):
    """Helper function for transform_to_counts()
    """
    df['_nature_of_charges'] = df.apply(
        lambda x: assess_arrest_type(x), axis=1)
    print('Charges assessed. Now transforming dataframe.')
    reshaped_df = df[
        [
            '_arrest_id',
            '_warrant',
            '_supervision',
            '_fta',
            '_pcs',
            '_disorder',
            '_municipal'
        ]
    ].melt(
        id_vars=['_arrest_id'],
        var_name='_charge_type',
        value_name='_count',
    )
    reshaped_df['_charge_type'] = reshaped_df['_charge_type'].str.replace(
        '_', '')
    categorized_df = (
        reshaped_df[reshaped_df['_count'] > 0]
        .groupby(['_arrest_id'])
        .agg(_charge_types=('_charge_type', format_unique))
    ).reset_index()
    final_df = pd.merge(df[['_arrest_id', '_nature_of_charges']], categorized_df, how='left', validate='1:1')
    final_df['_charge_types'].fillna('varied', inplace=True)
    print('Done!')
    return final_df

def transform_to_counts(df):
    """Produce counts of values for particular categories

    Parameters
    ----------

    df : pd.DataFrame, which should be read in from
    04_outputs/ and begin with c01.

    Returns
    -------
    pd.DataFrame
    """
    procedural_fields = ['_warrant', '_fta', '_supervision']
    low_level_fields = ['_warrant', '_fta',
                '_supervision', '_pcs', '_disorder', '_municipal']
    df['_charge_reconstructed'].fillna('', inplace=True)
    df['_procedural'] = df[procedural_fields].sum(axis=1) > 0
    df['_low-level'] = df[low_level_fields].sum(axis=1) > 0
    count_fields = [
        '_arrest_id',
        '_low-level',
        '_procedural',
        '_warrant',
        '_supervision',
        '_fta',
        '_pcs',
        '_disorder',
        '_municipal',
        '_charge_reconstructed',
    ]
    charge_counts = df[count_fields].groupby(['_arrest_id'], dropna=False).agg(sum)
    charge_counts.reset_index(inplace=True)
    total_charge_counts = (
        df[count_fields]
        .groupby(['_arrest_id'])
        .agg(total_charge_count=('_charge_reconstructed', 'count'))
        .reset_index()
    )
    print('Charge counts produced. Now assessing procedural and low-level charges.')
    count_df = pd.merge(charge_counts, total_charge_counts, validate='1:1')
    final_count_df = assess_charges(count_df)
    return final_count_df
