import csv
import pytest

from slcsp import build_zip_area_map, build_plan_rate_lookup

def test_duplicate_zips():
    """assert that known duplicate zip codes do not appear in the output"""
    with open('input/zips.csv', 'r') as zips_file:
        reader = csv.reader(zips_file)
        zip_map = build_zip_area_map(reader)

    # this zip code has multiple entries in the input with different rate areas
    assert '24121' not in list(zip_map.keys())
    # this zip code has multiple entries in the input, but map to the same rate area
    assert '54422' in list(zip_map.keys())
    # this zip code appears only once
    assert '61232' in list(zip_map.keys())

def test_plan_metal():
    """assert that only silver plans will be included in the output"""
    with open('input/plans.csv') as rates_file:
        rates_reader = csv.reader(rates_file)
        rates_by_area = build_plan_rate_lookup(rates_reader)

    # This rate is for a gold plan in this area and shouldn't appear in the output
    assert '361.69' not in rates_by_area.get('IL5')
    assert '298.62' in rates_by_area.get('GA7')

def test_rate_minimum():
    """assert that rate areas without the minimum number of results will be omitted"""
    with open('input/plans.csv') as rates_file:
        rates_reader = csv.reader(rates_file)
        rates_by_area = build_plan_rate_lookup(rates_reader, min_rates_per_area=2)

    # NJ1 doesn't have two silver plans
    assert not rates_by_area.get('NJ1')
    # GA7 has several plans, should be included
    assert rates_by_area.get('GA7')
