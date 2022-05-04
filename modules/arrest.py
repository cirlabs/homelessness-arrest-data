import re
import string

import pandas as pd
import shortuuid


class Subject:
    def __init__(self, gender, race, surname=None, given_name=None,full_name=None, dob=None, age=None, ethnicity=None):
        """Create a new Subject object with surname, given_name, dob, gender, race, ethnicity."""
        if full_name is None:
            self.full_name = given_name + surname
        self.dob = dob if dob is not None else ''
        self.gender = gender
        self.race = race
        self.ethnicity = ethnicity if ethnicity is not None else ''

    def calculate_age_at_arrest(arrest_date, subject_dob):
        birth_date_bool = (arrest_date.month, arrest_date.day) < (
            subject_dob.month,
            subject_dob.day,
        )
        return arrest_date.year - dob.year - birth_date_bool

    def determine_necessary_length(number_of_ids):
        """
        """
        shortuuid.set_alphabet('ABCDEFGHJKLMNPQRSTUVWXYZ23456789')
        alphabet_len = round(len(shortuuid.get_alphabet()) * 0.75)
        id_len = 2
        while (alphabet_len ** id_len) < number_of_ids:
            id_len += 1
        else:
            return(id_len)

    def generate_subject_uuids(df, field):
        field_ids = list(set(df[field]))
        number_of_ids = len(field_ids)
        length = determine_necessary_length(number_of_ids)
        generated = [shortuuid.random(length) for x in range(1, number_of_ids*2)]
        valid = list(set([x for x in generated if re.search('\D', x)]))
        if len(valid) >= number_of_ids:
            print(
                f'{len(valid)} ids generated for {number_of_ids} entities.\n\nSample: {valid[0:10]}')
            return dict(zip(field_ids, valid[0:number_of_ids]))
        else:
            print(f'Number of generated values short by {ids_length-valid}')

class Charge:
    def __init__(self, original_code, code_type=None):
        """Create a new Charge object."""
        if code_type is None:
            self.code_type, self.code = self.parse_code_type(original_code)
        else:
            self.code_type = code_type
            self.code = original_code

    @classmethod
    def parse_code_type(cls, original_code, other_codes=[]):
        """Parse code underlying an arrest charge (e.g. 29820(B)) from the code type (e.g. 'PC' for California Penal Code or 'VC' for California Vehicle Code) if the code type is valid.

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
        statute_codes = ['BP','FG','HS','PC','PU','VC','WI','US']
        codes = '|'.join(statute_codes+other_codes)
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

        >>> parse_meta('484 (A)/666', 'PC')
        ('484 (A)', '666')

        >>> parse_meta('647(J)', 'PC')
        ('647(J)', '')
        """
        meta_code = ''
        if code_type != '':
            if re.search('664\s?\/?', code):
                meta_code = '664'
                code = re.sub('664\s?\/?', '', code)
            elif re.search('\s?\/?666', code):
                meta_code = '666'
                code = re.sub('\s?\/?666', '', code)
        return code, meta_code

    @classmethod
    def parse_subparts(cls, text):
        """Helper function for parse_section_and_subparts. Parses a string of
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
        >>> parse_subparts('(A)(2)(A)')
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
    def parse_section(cls, code):
        """Helper function for parse_section. Parses the component
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
        >>> parse_section('12031 (A)(2)(A)')
        '12031'

        >>> parse_section('273A(B)')
        '273A'
        """
        alphanumeric_sections = ['118A', '146A', '146B', '146C', '146D', '146E',
        '146G', '171B', '171C', '171D', '171D.2', '171F.1', '171F.2', '172A',
        '172B', '172B.1', '172D', '172D.1', '172G', '172G.1', '172L', '266A',
        '266B', '266C', '266D', '266E', '266F', '266G', '266H', '266I', '266J',
        '270A', '270C', '271A', '273A', '273AB', '273D', '273E', '273F', '273G',
        '273I', '288A', '303A', '308B', '330A', '330B', '330C', '337A', '337A.1',
        '337A.2', '337A.3', '337A.4', '337A.5', '337A.6', '337B', '337C', '337D',
        '337E', '337F', '337G', '337H', '337I', '337J', '337K', '337S', '337U',
        '337V', '337W', '337X', '337Y', '347B', '351A', '369D', '369G', '369H',
        '373A', '374C', '374D', '381A', '381B', '381C', '381D', '381E', '383A',
        '383B', '383C', '384A', '384C', '384D', '384E', '384H', '402A', '402B',
        '402C', '405A', '405B', '470A', '470B', '476A', '484B', '484C', '484E',
        '484F', '484G', '484H', '484I', '484J', '487A', '487B', '487C', '487D',
        '487E', '487F', '487G', '487H', '487I', '487J', '487K', '496A', '496B',
        '496C', '496D', '496E', '499B', '499C', '499D', '504A', '504B', '506B',
        '529A', '531A', '532A', '532B', '532C', '532D', '532E', '532F', '536A',
        '537B', '537C', '537E', '537F', '537G', '538A', '538B', '538C', '538D',
        '538E', '538F', '538G', '538H', '587A', '587B', '587C', '588A', '588B',
        '593A', '593B', '593C', '593D', '593E', '593F', '593G', '597A', '597B',
        '597C', '597E', '597F', '597G', '597H', '597I', '597J', '597K', '597L',
        '597M', '597N', '597O', '597P', '597Q', '597R', '597S', '597T', '597U',
        '597V', '597X', '597Z', '598A', '598B', '598C', '598D', '599E', '599F',
        '625B', '625C', '639A', '640A', '640A.1', '640A.2', '640B', '640B.1',
        '640B.2', '647B', '647C', '647E', '648A', '649A', '653AA', '653B', '653C',
        '653D', '653F', '653G', '653H', '653I', '653J', '653K', '653M', '653N',
        '653O', '653P', '653Q', '653R', '653S', '653T', '653U', '653W', '653X',
        '653Y', '653Z']
        pattern = '|'.join(alphanumeric_sections)
        if len(re.findall(pattern, code)) > 0:
            return re.findall(pattern, code)[0]
        else:
            return re.match('\d+(\.?\d+)*', code)[0]

    @classmethod
    def parse_section_and_subparts(cls, code, arrests=True):
        """Parses the subparts in a charge code from the section.

        Parameters
        ----------
        code : str
            The code underlying an arrest charge, typically composed of a
            (potentially alphanumeric) section code followed by zero or more
            characters denoting subparts.

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
        >>> parse_section_and_subparts('12031 (A)(2)(A)')
        ('12031', '(A)', '(2)', '(A)', '')
        """
        if re.match('\d+(\.?\d+)*', code) != None:
            if arrests==True:
                section = cls.parse_section(code)
            elif arrests==False:
                section = code.split('(')[0]
            subparts_text = re.sub(re.escape(section), '', code)
        else:
            section = ''
            subparts_text = ''

        subdivision, paragraph, subparagraph, clause = cls.parse_subparts(
            subparts_text)
        return section, subdivision, paragraph, subparagraph, clause

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

def format_unique(values):
    """Format unique values as a string, separated by a comma.
    Ignores null values and empty strings.
    """
    string_values = [str(x) for x in values]
    s = set([x for x in string_values if x != '' and x != 'nan'])
    text = ', '.join(s)
    return text

export_columns = ['_person_id', '_census_race', '_census_ethnicity',
          '_gender', '_arrest_age', '_housing_status', '_arrest_id',
          '_arrest_date', '_original_charge_code',
          '_original_charge_description', '_code_type', '_section',
          '_meta_code', '_charge_reconstructed', '_municipal',
          '_offense_level', '_charge_description', '_incongruity', '_violent',
          '_warrant', '_fta', '_supervision', '_felony', '_federal',
          '_potential_offense_levels', '_levels_congruent',
          '_code_type_of_felony', '_pcs', '_disorder']
