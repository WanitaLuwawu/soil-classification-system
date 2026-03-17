def compute_properties(data):
    water_density = 1000
    g = 9.81

    total_mass = data['Total Mass [kg]']
    oven_dried_mass = data['Oven Dried Mass [kg]']
    total_volume = data['Total Volume [m^3]']
    specific_gravity = data['Specific Gravity [-]']

    bulk_density = total_mass / total_volume
    unit_weight = bulk_density * g
    moisture_content = (total_mass - oven_dried_mass) / oven_dried_mass
    void_ratio = ((specific_gravity * (1 + moisture_content) * water_density) / bulk_density) - 1
    porosity = void_ratio / (1 + void_ratio)

    return {
        "bulk_density": bulk_density,
        "unit_weight": unit_weight,
        "moisture_content": moisture_content,
        "void_ratio": void_ratio,
        "porosity": porosity
    }