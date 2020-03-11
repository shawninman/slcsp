import csv
import collections
import sys

ZipCode = collections.namedtuple('ZipCode', 'zip state county name area')
Plan = collections.namedtuple('Plan', 'id state metal rate area')

def build_zip_area_map(reader):
    """
    Given a csv reader for the zips file, produces a dictionary where the keys represent the zip code and the values are the
    associated rate area i.e. NY1, GA7

    ex:
    {
        '36749': 'AL11',
        '36507': 'AL13',
    }
    """

    zip_area_map = dict()
    ambiguous_zips = set()

    _ = next(reader)

    for zip_code in map(ZipCode._make, reader):
        area = f'{zip_code.state}{zip_code.area}'

        # if this zip already has a rate area associated, flag it for removal later
        existing_area = zip_area_map.get(zip_code.zip)
        if existing_area and existing_area != area:
            ambiguous_zips.add(zip_code.zip)

        zip_area_map[zip_code.zip] = area

    # remove any entries from the table where a zip code involves multiple rate areas
    for zip_code in ambiguous_zips:
        _ = zip_area_map.pop(zip_code)

    return zip_area_map

def build_plan_rate_lookup(reader, min_rates_per_area=0):
    """
    Given a csv reader, produces a dictionary where the keys represent the rate area, i.e.
    NY1, GA7 and the values are lists of the rates for Silver health plans, sorted ascending

    ex:
    {
        'NY1':[155.11, 198.66, 203.42],
        'GA7':[44.66, 99.10],
    }
    """

    rates_by_area = dict()

    _ = next(reader)

    # iterate over the rates in the file
    for plan in map(Plan._make, reader):
        plan_area = f'{plan.state}{plan.area}'

        if plan.metal != 'Silver':
            continue

        rates = rates_by_area.get(plan_area)
        if not rates:
            rates = list()

        rates.append(f'{float(plan.rate):.2f}')
        rates.sort()
        rates_by_area[plan_area] = rates

    # if we require a minimum number of rates per area and this area doesn't meet the criteria, pop that record
    if min_rates_per_area:
        editable_rates_map = rates_by_area.copy()
        for area, rates in rates_by_area.items():
            if len(rates) < min_rates_per_area:
                editable_rates_map.pop(area)

        rates_by_area = editable_rates_map

    return rates_by_area


if __name__ == '__main__':
    """main entry point"""
    with open('input/zips.csv', 'r') as zips_file:
        zips_reader = csv.reader(zips_file)
        zip_area_map = build_zip_area_map(zips_reader)

    with open('input/plans.csv') as rates_file:
        rates_reader = csv.reader(rates_file)
        rates_by_area = build_plan_rate_lookup(rates_reader, min_rates_per_area=2)

    with open('input/slcsp.csv', 'r') as source:
        slcsp_reader = csv.reader(source)
        header = next(slcsp_reader)
        sys.stdout.write(','.join(header))
        sys.stdout.write('\n')

        for zip_code, _  in slcsp_reader:
            area = zip_area_map.get(zip_code)
            rates = rates_by_area.get(area)

            rate = '' if not rates else rates[1]

            sys.stdout.write(f'{zip_code},{rate}\n')
