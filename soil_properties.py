def compute_properties(data) -> dict:
    """
    Computes geotechnical properties of a soil sample from basic measurements.

    Args:
        data: A dict-like object containing the following keys:
            - 'Total Mass [kg]': Total mass of the soil sample including water.
            - 'Oven Dried Mass [kg]': Mass of the sample after drying (solids only).
            - 'Total Volume [m^3]': Total volume of the sample.
            - 'Specific Gravity [-]': Specific gravity of the soil solids.

    Returns:
        A dict with the following computed properties:
            - 'Bulk Density [kg]': Mass per unit total volume (kg/m^3).
            - 'Unit Weight [kN/m^3]': Bulk density scaled by gravity, in kilonewtons.
            - 'Moisture Content [%]': Ratio of water mass to dry mass, as a percentage.
            - 'Void Ratio [-]': Ratio of void volume to solid volume.
            - 'Porosity [-]': Ratio of void volume to total volume.
    """
    # Physical constants
    water_density = 1000   # Density of water [kg/m^3]
    g = 9.81               # Gravitational acceleration [m/s^2]

    # Unpack input measurements from the data dict
    total_mass = data['Total Mass [kg]']
    oven_dried_mass = data['Oven Dried Mass [kg]']
    total_volume = data['Total Volume [m^3]']
    specific_gravity = data['Specific Gravity [-]']

    # Bulk density: total mass divided by total volume [kg/m^3]
    bulk_density = total_mass / total_volume

    # Unit weight: bulk density scaled by gravity, converted to kN/m^3
    unit_weight = bulk_density * g

    # Moisture content: mass of water (total minus dry) as a fraction of dry mass
    moisture_content = (total_mass - oven_dried_mass) / oven_dried_mass

    # Void ratio: derived from the phase relationship between solids, water, and voids;
    # rearranged from Gs * (1 + w) = (bulk_density / water_density) * (1 + e)
    void_ratio = ((specific_gravity * (1 + moisture_content) * water_density) / bulk_density) - 1

    # Porosity: fraction of total volume occupied by voids, derived from void ratio
    porosity = void_ratio / (1 + void_ratio)

    return {
        "Bulk Density [kg]": bulk_density,
        "Unit Weight [kN/m^3]": unit_weight / 1000,  # Convert N to kN
        "Moisture Content [%]": moisture_content * 100,  # Convert fraction to percentage
        "Void Ratio [-]": void_ratio,
        "Porosity [-]": porosity
    }