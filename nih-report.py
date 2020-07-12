#!/bin/env python

"""
Prepare an NIH report
"""

################################################################################
# Metadata for report
# TODO: Move this to a command-line arguments to specify grant id and autodetect reporting period
################################################################################

import datetime

# Start and end date for reporting period
reporting_period_end = datetime.date.fromisoformat('2020-08-31')
#reporting_period_start = datetime.date.fromisoformat('2019-09-01')
reporting_period_start = datetime.date.fromisoformat('2019-07-01')

# Grant ID to report
grant_id = 'NIH R01 GM121505' # The

################################################################################
# Helper functions to act as filters
################################################################################

def funded_by_grant(paper, grant_id):
    """Return True if the paper was funded by the specified grant.
    """
    try:
        if grant_id in paper['funding']:
            return True
    except Exception as e:
        pass

    return False

def published_during_reporting_period(paper):
    """Return True if paper was published during the grant reporting period.
    """
    try:
        if reporting_period_start <= paper['published']['dates']['published'] <= reporting_period_end:
            return True
    except Exception as e:
        pass
    return False

def accepted_during_reporting_period(paper):
    """Return True if paper was published during the grant reporting period.
    """
    try:
        if reporting_period_start <= paper['published']['dates']['accepted'] <= reporting_period_end:
            return True
    except Exception as e:
        pass
    return False

def preprinted_during_reporting_period(paper):
    """Return True if paper was published during the grant reporting period.
    """
    try:
        if reporting_period_start <= paper['preprint']['date'] <= reporting_period_end:
            return True
    except Exception as e:
        pass
    return False

################################################################################
# Load the databases
################################################################################

def load_databases():
    """
    Load all databases

    Returns
    -------
    db : dict
        db[dbname] is the database contents
        dbname is one of ['grants', 'papers']
    """
    # Load papers
    import yaml

    db = dict()
    for dbname in ['papers', 'grants']:
        with open(f'{dbname}.yaml') as infile:
            db[dbname] = yaml.load(infile, Loader=yaml.FullLoader)

    return db


if __name__ == '__main__':

    # Load the databases
    db = load_databases()

    # Extract all publications in the reporting period
    papers = db['papers']
    for paper in papers:
        # Identify those papers that were funded by the grant
        if not funded_by_grant(paper, grant_id):
            continue

        # Identify papers published in the reporting range
        if published_during_reporting_period(paper):
            print('PUBLISHED:')
            print(paper)
            print('')
        elif accepted_during_reporting_period(paper):
            print('ACCEPTED:')
            print(paper)
            print('')
        elif preprinted_during_reporting_period(paper):
            print('PREPRINT:')
            print(paper)
            print('')
