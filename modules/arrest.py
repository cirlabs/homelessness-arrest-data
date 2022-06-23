import re
import string

import law
import numpy as np
import pandas as pd
import shortuuid


class Subject:
    census_races = ['American Indian and Alaska Native', 'Asian', 'Black or African American', 'Native Hawaiian and Other Pacific Islander', 'Other/Unknown', 'White']

    census_ethnicities = ['Hispanic or Latino (of any race)', 'Not Hispanic or Latino', 'Unknown']

    def __init__(self, gender, race, surname=None, given_name=None,full_name=None, dob=None, age=None, ethnicity=None):
        """Create a new Subject object with surname, given_name, dob, gender, race, ethnicity."""
        if full_name is None:
            self.full_name = given_name + surname
        self.dob = dob if dob is not None else ''
        self.gender = gender
        self.race = race
        self.ethnicity = ethnicity if ethnicity is not None else ''

    @classmethod
    def calculate_age_at_arrest(cls, arrest_date, subject_dob):
        birth_date_bool = (arrest_date.month, arrest_date.day) < (
            subject_dob.month,
            subject_dob.day,
        )
        return arrest_date.year - subject_dob.year - birth_date_bool

    @classmethod
    def determine_necessary_length(cls, number_of_ids):
        """
        """
        shortuuid.set_alphabet('ABCDEFGHJKLMNPQRSTUVWXYZ23456789')
        alphabet_len = round(len(shortuuid.get_alphabet()) * 0.75)
        id_len = 2
        while (alphabet_len ** id_len) < number_of_ids:
            id_len += 1
        else:
            return(id_len)

    @classmethod
    def generate_subject_uuids(cls, df, field, length=None):
        field_ids = list(set(df[field]))
        number_of_ids = len(field_ids)
        if length == None:
            length = cls.determine_necessary_length(number_of_ids)
        generated = [shortuuid.random(length) for x in range(1, number_of_ids*2)]
        valid = list(set([x for x in generated if re.search('\D', x)]))
        if len(valid) >= number_of_ids:
            print(
                f'{len(valid)} ids generated for {number_of_ids} entities.\n\nSample: {valid[0:10]}')
            return dict(zip(field_ids, valid[0:number_of_ids]))
        else:
            print(f'Number of generated values short by {abs(length-len(valid))}')

class Charge:

    ca_section_components = ['_section', '_subdivision', '_paragraph', '_subparagraph', '_clause']
    or_section_components = ['_section', '_subsection', '_paragraph', '_subparagraph', '_subsubparagraph']

    def __init__(self, original_code, code_type=None):
        """Create a new Charge object."""
        if code_type is None:
            self.code_type, self.code = self.parse_code_type(original_code)
        else:
            self.code_type = code_type
            self.code = original_code

    @classmethod
    def parse_code_type(cls, original_code, other_codes=[]):
        """Parse code underlying a Californa arrest charge (e.g. 29820(B)) from the code type (e.g. 'PC' for California Penal Code or 'VC' for California Vehicle Code), if the code type is valid.

        Parameters
        ----------
        value : str
            Text representing the code (i.e. section and subparts) and code type (e.g. 'PC' for California Penal Code) underlying
            arrest charge

        Returns
        -------
        tuple

        Examples
        --------
        >>> parse_code_type('PC29820 (B)')
        ('PC', '29820 (B)')

        >>> parse_code_type('B/W-FEL')
        ('', 'B/W-FEL')
        """
        statute_codes = law.California.code_types
        codes = '|'.join(other_codes+statute_codes)
        pattern = f'({codes})'
        if match := re.search(f'{pattern}$', original_code) or re.search(
            f'^{pattern}', original_code
        ):
            code_type = match.group(0)
            code = re.sub(f'{code_type}', '', original_code)
        else:
            code_type = ''
            code = original_code
        return code_type, code

    @classmethod
    def parse_meta(cls, code, code_type):
        """Parses information regarding attempted charges or modification of
        charges because subject has priors.

        Parameters
        ----------
        code : str
            Text representing the code (i.e. section and subparts) underlying
            arrest charge

        code_type: str
            Text representing the type of code corresponding to arrest charge,
            e.g. 'PC' for California Penal Code
            - If '', simply return tuple of `code` arg and empty string.

        Returns
        -------
        tuple

        Examples
        --------
        >>> parse_meta('664 /286(C)', 'PC')
        ('286(C)', '664')

        >>> parse_meta('647(J)', 'PC')
        ('647(J)', '')
        """
        meta_code = ''
        if code_type == 'PC':
            if re.search('664\s?\/?', code):
                meta_code = '664'
                code = re.sub('664\s?\/?', '', code)
            elif re.search('484\s?\(A\)\/666', code):
                code = '484(A)/666'
        return code, meta_code

    @classmethod
    def _parse_subparts(cls, text):
        """Helper function for parse_code. Parses a string of
        subparts into separate strings.

        Parameters
        ----------
        text : str
            A string following the numerical components of a charge section

        Returns
        -------
        list of strings

        Example
        --------
        >>> _parse_subparts('(A)(2)(A)')
        ['(A)', '(2)', '(A)', '']
        """
        expression = re.compile(r'([a-zA-Z]|[0-9]+)\1*')
        subparts = [match.group() for match in expression.finditer(text)]
        if len(subparts) > 4 or len(subparts) == 0:
            subparts = ['' for x in range(4)]
        else:
            subparts = ['(' + x + ')' for x in subparts]
            subparts += [''] * (4 - len(subparts))
        return subparts

    @classmethod
    def _parse_section_and_subparts(cls, code, state):
        """Helper function for parse_code. Parses the component
        subparts into subdivision, paragraph, subparagraph, clause.

        Parameters
        ----------
        code : str
            The code underlying an arrest charge, typically composed of a
            (potentially alphanumeric) section code followed by zero or more
            characters denoting subparts.

        Returns
        -------
        str

        Examples
        --------
        >>> _parse_section('12031 (A)(2)(A)')
        '12031'

        >>> _parse_section('273A(B)')
        '273A'
        """
        if state == 'OR':
            pattern = '|'.join([x+'\.\d+' for x in law.Oregon.alphanumeric_sections])
        elif state == 'CA':
            pattern = '|'.join(law.California.alphanumeric_sections)

        if len(re.findall(pattern, code)) > 0:
            return re.findall(pattern, code)[0]
        else:
            return re.match('\d+(\.?\d+)*', code)[0]

    @classmethod
    def parse_code(cls, code, state, arrests=True):
        """Parses the subparts in a charge code from the section.

        Parameters
        ----------
        code : str
            The code underlying an arrest charge, typically composed of a
            (potentially alphanumeric) section code followed by zero or more
            characters denoting subparts.

        state : str

        arrests : bool, default True
            If arrests==False, this method is being called on a canonical source
            like chsoff, and will isolate section by first paren. If this method
            is being called on arrest data (arrests=True), then parentheses are
            not as reliable for demarcating sections and subparts, and parsing
            will proceed through regular expressions.


        Returns
        -------
        tuple

        Examples
        --------
        >>> parse('12031 (A)(2)(A)')
        ('12031', '(A)', '(2)', '(A)', '')
        """
        if re.match('\d+(\.?\d+)*', code) != None:
            if arrests==True:
                section = cls._parse_section_and_subparts(code, state)
            elif arrests==False:
                section = code.split('(')[0]
            subparts_text = re.sub(re.escape(section), '', code)
        else:
            section = ''
            subparts_text = ''

        subdivision, paragraph, subparagraph, clause = cls._parse_subparts(
            subparts_text)
        return section, subdivision, paragraph, subparagraph, clause

    @classmethod
    def flag_level_incongruity(cls, offense_level, potential_offense_levels):
        if type(potential_offense_levels) is str:
            if re.search(offense_level, potential_offense_levels):
                return True
            else:
                return False
        else:
            return np.nan


def normalize_text(value, punctuation=False):
    """Optionally removes punctuation, removes redundant whitespace, normalizes case

    Parameters
    ----------
    value : str
        The string to operate on
    punctuation : bool, default False
        If True, sub any punctuation character with whitespace

    Returns
    -------
    str

    Examples
    --------
    >>> clean_string('1400   alder dr. ', punctuation=True)
    '1400 ALDER DR'

    >>> clean_string('P.O. Box 123', punctuation=True)
    'PO BOX 1234'

    >>> clean_string('P.O. Box 123')
    'P.O. BOX 1234'
    """
    if punctuation == True:
        value = value.translate(str.maketrans('', '', string.punctuation))
    value = re.sub('\s{2,}', ' ', value)
    return value.strip().upper()

def find_any_true(values):
    return True in set(values)

def format_for_order(values):
    """Format collection of values as a string and retain order."""
    string_values = [str(x) for x in values]
    text = ', '.join(string_values)
    return text

def format_unique(values, keep_unknowns_if_alone=True):
    """Format unique values as a string, separated by a comma.
    Ignores null values and empty strings.
    """
    default_to_ignore = ['', 'nan']
    unknowns_to_ignore = ['unknown', 'UNKNOWN', 'no address information']
    string_values = [str(x) for x in values if x not in default_to_ignore]
    string_values.sort()
    if keep_unknowns_if_alone == True and set(string_values).issubset(set(unknowns_to_ignore)) == False:
        s = list(set([x for x in string_values if x not in unknowns_to_ignore]))
    else:
        s = list(set([x for x in string_values]))
    s.sort()
    text = ', '.join(s)
    return text

person_export_columns = ['_person_id', '_arrest_id', '_age_at_arrest', '_ethnicity', '_race', '_gender','_housing_status', '_subcategory', '_category', '_source']
clean_export_columns = ['_person_id', '_census_race', '_census_ethnicity',
          '_gender', '_age_at_arrest', '_housing_status', '_arrest_id',
          '_arrest_date', '_original_charge_code',
          '_original_charge_description', '_code_type', '_section',
          '_meta_code', '_charge_reconstructed', '_ordinance',
          '_offense_level', '_charge_description', '_incongruity',
           '_felony',  '_potential_offense_levels', '_levels_congruent', '_code_type_of_felony']
