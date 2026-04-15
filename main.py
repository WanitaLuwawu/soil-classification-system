import pandas as pd
import data_reader as dr
import sieve_analysis as sa_sieve
import soil_analysis as sa
import soil_properties as sp
import hydrometer_analysis as sa_hydrometer
import atterberg_limits_analysis as sa_atterberg

file = 'Sample Soil Data.xlsx'

# read sieve analysis data
tables = dr.read_tables(
    file,
    'WS8 Sieve Analysis',
    ['Experimental Mass', 'Coarse Portion', 'Fine Portion'],
    has_header=[False, True, True]
)

sample_data = dr.read_sample_data(file, 'WS8 Data Sheet')

# extract values
experimental_mass = dict(zip(tables['Experimental Mass'].iloc[:, 0], tables['Experimental Mass'].iloc[:, 1]))
initial_total_weight = experimental_mass['Initial Total Weight [g]']
fines_weight = experimental_mass['Fines Total Weight Before Wash [g]']

# process sieve
coarse = sa_sieve.process_coarse(tables['Coarse Portion'], initial_total_weight)
fine = sa_sieve.process_fine(tables['Fine Portion'], tables['Coarse Portion'], fines_weight)

full_data = sa_sieve.combine_data(coarse, fine)

# gradation
D10 = sa.get_D_value(full_data, 10)
D30 = sa.get_D_value(full_data, 30)
D60 = sa.get_D_value(full_data, 60)

Cu = D60 / D10
Cc = (D30**2) / (D10 * D60)

# soil properties
properties = sp.compute_properties(sample_data)

# read sieve analysis of hydrometer sample
tables = dr.read_tables(
    file, 'WH25 Sieve Analysis',
    ['Experimental Mass', 'Sieve Analysis Before Hydrometer Testing', 'Sieve Analysis After Hydrometer Testing'],
    has_header=[False, True, True]
)

# read hydrometer analysis of hydrometer sample
hydrometer_tables = dr.read_tables(
    file, 'WH25 Hydrometer Analysis',
    ['Hygroscopic Moisture Content Data', 'Hydrometer Test Sample Data', 'Hydrometer Test Data'],
    has_header=[False, False, True]
)

# read sample datasheet
hy_sample_data = dr.read_sample_data(file, 'WH25 Data Sheet')

# prepare inputs
experimental_mass = dict(zip(tables['Experimental Mass'].iloc[:, 0], tables['Experimental Mass'].iloc[:, 1]))
moisture_content_data = dict(zip(hydrometer_tables['Hygroscopic Moisture Content Data'].iloc[:, 0], hydrometer_tables['Hygroscopic Moisture Content Data'].iloc[:, 1]))
sample_data = dict(zip(hydrometer_tables['Hydrometer Test Sample Data'].iloc[:, 0], hydrometer_tables['Hydrometer Test Sample Data'].iloc[:, 1]))

total_exp_mass = experimental_mass['Initial Total Weight [g]']
oven_dried_soil_mass = moisture_content_data['Mass of Oven Dried Soil [g]']
air_dried_soil_mass = moisture_content_data['Mass of Air Dried Soil [g]']
hygroscopic_correction_factor = oven_dried_soil_mass / air_dried_soil_mass

hy_coarse = sa_sieve.process_coarse(tables['Sieve Analysis Before Hydrometer Testing'], total_exp_mass)
percent_passing_2mm = hy_coarse.loc[hy_coarse['Sieve Size [mm]'] == 2, '% Passing'].values[0]
tested_mass = (hygroscopic_correction_factor * sample_data['Total Sample Mass']) / percent_passing_2mm * 100
hy_fine  = sa_sieve.process_fine(tables['Sieve Analysis After Hydrometer Testing'], hy_coarse, tested_mass)

specific_gravity = sample_data['Specific Gravity']
percent_passing_75um = hy_fine.loc[hy_fine['Sieve Size [µm]'] == 75, '% Passing'].values[0]

# run analysis
hydrometer_test_data = sa_hydrometer.process(
    test_data            = hydrometer_tables['Hydrometer Test Data'],
    sample_data          = sample_data,
    percent_passing_75um = percent_passing_75um
)

hy_full_data = sa_sieve.combine_data(coarse, fine)

# gradation
hy_D10 = sa.get_D_value(hy_full_data, 10)
hy_D30 = sa.get_D_value(hy_full_data, 30)
hy_D60 = sa.get_D_value(hy_full_data, 60)

hy_Cu = hy_D60 / hy_D10
hy_Cc = (hy_D30**2) / (hy_D10 * hy_D60)

# soil properties
hy_properties = sp.compute_properties(hy_sample_data)

# read atterberg limits analysis data
atterberg_tables = dr.read_tables(
    file, 'Atterberg Limits Analysis',
    ['Liquid Limit', 'Plastic Limit'],
    has_header=[True, True]
)

# run analysis
ll_data, pl_data, ll, pl, pi = sa_atterberg.process(
    atterberg_tables['Liquid Limit'],
    atterberg_tables['Plastic Limit']
)