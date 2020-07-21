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
# Rendering function
################################################################################

def show_paper(paper):
    """Render the paper as Markdown
    """
    try:
        # Title
        print(f"**{paper['title']}**")
        # Journal
        if 'published' in paper:
            published = paper['published']
            print("*{journal}* {volume}:{page}, {year}".format(**published))
            print(f"DOI: {published['doi']}")
        elif 'preprint' in paper:
            preprint = paper['preprint']
            print(f"Preprint: {preprint['url']}")

        # Authors
        for index, author in enumerate(paper['authors']):
            if index == 0:
                print(f"{author}", end='')
            if index == len(paper['authors']) - 1:
                print(f", and {author}")
            else:
                print(f", {author}", end='')

        # Links
        if 'links' in paper:
            for link in paper['links']:
                print(f"**{link['action']}:** {link['url']}")

        # Description
        if 'description' in paper:
            print(f"*{paper['description'].rstrip()}*")

    except Exception as e:
        # Give up on rendering if we get stuck
        print(e)
        pass


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
    from collections import defaultdict
    papers_to_report = defaultdict(list)

    papers = db['papers']
    for paper in papers:
        # Identify those papers that were funded by the grant
        if not funded_by_grant(paper, grant_id):
            continue

        # Identify papers published in the reporting range
        if published_during_reporting_period(paper):
            papers_to_report['papers were published'].append(paper)
        elif accepted_during_reporting_period(paper):
            papers_to_report['manuscripts were accepted'].append(paper)
        elif preprinted_during_reporting_period(paper):
            papers_to_report['preprints were posted'].append(paper)

    for category in ['papers were published', 'manuscripts were accepted', 'preprints were posted']:
        if (category in papers_to_report) and (len(papers_to_report[category]) > 0):
            print(f'Since the last reporting period, the following {category}, funded by this grant in part or whole:')
            for paper in papers_to_report[category]:
                print('')
                show_paper(paper)

            print('')
