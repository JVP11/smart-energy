"""
KSEB (Kerala State Electricity Board) tariff rules and calculator.
Based on KSERC Tariff Order 2023-24. Domestic LT-1A consumers.
"""

# Telescopic slabs (bi-monthly, up to 250 units) - ₹/unit
KSEB_TELESCOPIC_SLABS = [
    (0, 50, 3.25),
    (51, 100, 4.05),
    (101, 150, 5.10),
    (151, 200, 6.95),
    (201, 250, 8.20),
]

# Non-telescopic (above 250 units) - flat rate ₹/unit
KSEB_NON_TELESCOPIC_RATE = 7.50

# Fixed charges (₹/month) by consumption slab - Single Phase LT-1A
KSEB_FIXED_CHARGES = [
    (0, 50, 25),
    (51, 100, 40),
    (101, 150, 50),
    (151, 200, 60),
    (201, 250, 70),
    (251, 9999, 90),
]

# Fuel surcharge ₹/unit
KSEB_FUEL_SURCHARGE = 0.10

# Electricity duty % on (energy + fuel surcharge)
KSEB_ELECTRICITY_DUTY_PCT = 10


def kseb_energy_charge(units):
    """Calculate energy charge using KSEB telescopic/non-telescopic rules."""
    if units <= 0:
        return 0.0
    if units <= 250:
        total = 0.0
        remaining = units
        for low, high, rate in KSEB_TELESCOPIC_SLABS:
            slab_units = min(remaining, high - low + 1)
            total += slab_units * rate
            remaining -= slab_units
            if remaining <= 0:
                break
        return round(total, 2)
    return round(units * KSEB_NON_TELESCOPIC_RATE, 2)


def kseb_fixed_charge(units):
    """Get fixed charge for given consumption slab."""
    for low, high, charge in KSEB_FIXED_CHARGES:
        if low <= units <= high:
            return charge
    return 90


def kseb_calculate_bill(units, is_bimonthly=True):
    """
    Calculate total KSEB bill for given units.
    units: consumption in kWh
    is_bimonthly: if True, fixed charge is doubled (2 months)
    """
    energy = kseb_energy_charge(units)
    fixed = kseb_fixed_charge(units) * (2 if is_bimonthly else 1)
    fuel = round(units * KSEB_FUEL_SURCHARGE, 2)
    subtotal = energy + fuel
    duty = round(subtotal * (KSEB_ELECTRICITY_DUTY_PCT / 100), 2)
    total = round(energy + fixed + fuel + duty, 2)
    return {
        "energy_charge": energy,
        "fixed_charge": fixed,
        "fuel_surcharge": fuel,
        "electricity_duty": duty,
        "total": total,
        "units": units,
        "slab_used": "Non-Telescopic" if units > 250 else "Telescopic",
    }


def kseb_effective_rate(units):
    """Average ₹/unit for given consumption (for display)."""
    bill = kseb_calculate_bill(units)
    return round(bill["total"] / units, 2) if units > 0 else 0


# Rules summary for display
KSEB_RULES = [
    "Telescopic billing applies only up to 250 units (bi-monthly).",
    "Above 250 units, entire consumption charged at higher non-telescopic rate.",
    "Fixed charges vary by consumption slab (₹25–90/month).",
    "Fuel surcharge: ₹0.10 per unit.",
    "Electricity duty: 10% on energy + fuel surcharge.",
    "Billing cycle: Bi-monthly (60 days) for domestic consumers.",
    "Stay under 250 units to avoid steep bill increase.",
]
