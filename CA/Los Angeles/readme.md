# Los Angeles

## Date range

Los Angeles provided data on arrests from January 2009 through January 2021.

![Bar chart depicting the years that of data provided by each jurisdiction](methodology/visuals/arrest_dates.png)


## Fields

| Field                        | Example                   | Description                                                                                                                                                                                                     |
|------------------------------|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| _person_id                   | P25LZ                     | Randomly generated five-character ID code assigned to individuals based on a combination of given name, surname, date of birth, and gender.                                                                     |
| _census_race                 | Black or African American | All races recorded for this arrestee, normalized to match U.S. Census Bureau race designations except in cases that the field specifies U.S. Census Bureau ethnicity designations.                              |
| _census_ethnicity            | Not Hispanic or Latino    | One of the following values: 'Not Hispanic or Latino', 'Hispanic or Latino (of any race)', 'Unknown'                                                                                                            |
| _gender                      | M                         | One of the following values: 'M', 'F', 'U' (Unknown)                                                                                                                                                            |
| _age_at_arrest               | 37                        | To help preserve arrestee privacy, I've calculated their age at the time of arrest to provide instead of their date of birth.                                                                                   |
| _housing_status              | unhoused                  | One of the following values: 'housed', 'unhoused', 'no information', 'unknown'. See the Housing Status section in the methodology documentation.                                                                |
| _arrest_id                   | P25LZ_2020-02-20_14:30:00 | This is simply the _arrest_id field concatenated to the date and time of arrest.                                                                                                                                |
| _arrest_date                 | 2020-02-20 14:30:00       | The date and time of the arrest.                                                                                                                                                                                |
| _original_charge_code        | 484(A)PC                  | This reflects the original information entered regarding the code corresponding to an arrest charge.                                                                                                            |
| _original_charge_description | GRAND THEFT (OVER $400)   | This reflects the original description entered regarding an arrest charge.                                                                                                                                      |
| _code_type                   | PC                        | This is an extracted or imputed field describing the type of code under which a charge exists. See all code types [here](https://leginfo.legislature.ca.gov/faces/codes.xhtml).                                 |
| _section                     | 484                       | This is an extracted or imputed field corresponding to the section of an arrest charge. See PEN/PC §484 [here](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PEN&sectionNum=484). |
| _meta_code                   |                           | In some cases, an additional section is applied to a charge that further describes it as, e.g., [PEN/PC §664](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PEN&sectionNum=664).  |
| _charge_reconstructed        | PC484(A)                  | This is a concatenation of _code_type, _section, and arbitrarily many subpart components of the section of an arrest charge.                                                                                    |
| _ordinance                   |                           | Boolean field specifying whether the charge is an ordinance (whether municipal, county, or transit).                                                                                                            |
| _offense_level               | M                         | This reflects the original information entered regarding the severity or level of the charge, typically 'M' (Misdemeanor), 'F' (Felony), 'I' (Infraction), or 'V' (Violation)                                   |
| _charge_description          | THEFT PERSONAL PROPERTY   | This is the description of the charge as it exists in reference data obtained from the California Office of the Attorney General [here](https://oag.ca.gov/law/code-tables).                                    |
| _incongruity                 | _offense_level            | If any feature of the original data does not match the reference data, it is recorded here.                                                                                                                     |
| _felony                      | FALSE                     | Boolean field specifying whether the charge is a felony.                                                                                                                                                        |
| _potential_offense_levels    | F                         | This reflects the potential offense levels (sometimes called severities) of a charge, per reference data.                                                                                                       |
| _levels_congruent            | FALSE                     | This is a Boolean field specifying whether the recorded offense level is among the potential offense levels listed in the reference data.                                                                       |
| _code_type_of_felony         |                           | This field captures the code type of a charge if it is a felony.                                                                                                                                                |
