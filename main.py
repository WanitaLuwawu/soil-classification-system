import data_reader as dr
import sieve_analysis as sa_sieve
import soil_analysis as sa
import soil_properties as sp

file = 'Sample Soil Data.xlsx'

# read data
meta, coarse, fine = dr.read_sieve_data(file)
sample_data = dr.read_sample_data(file)

# extract values
initial_total_weight = meta['Initial Total Weight [g]']
fines_weight = meta['Fines Total Weight Before Wash [g]']

# process sieve
coarse = sa_sieve.process_coarse(coarse, initial_total_weight)
fine = sa_sieve.process_fine(fine, coarse, fines_weight)

full_data = sa_sieve.combine_data(coarse, fine)

# gradation
D10 = sa.get_D_value(full_data, 10)
D30 = sa.get_D_value(full_data, 30)
D60 = sa.get_D_value(full_data, 60)

Cu = D60 / D10
Cc = (D30**2) / (D10 * D60)

# soil properties
properties = sp.compute_properties(sample_data)

print("Cu:", Cu)
print("Cc:", Cc)
print(properties)