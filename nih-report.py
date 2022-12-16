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
reporting_period_start = datetime.date.fromisoformat('2021-09-01')
#reporting_period_end = datetime.date.fromisoformat('2022-08-31')
reporting_period_end = datetime.date.fromisoformat('2022-12-12')

# Grant ID to report
grant_id = 'NIH R01 GM121505' # kinase grant

################################################################################
# Helper functions to act as filters
################################################################################

def funded_by_grant(paper, grant_id):
    """
    Determine whether the paper was funded by the specified grant,
    and if specified, the rationale behind how the paper aligns with the grant.

    Parameters
    ----------
    paper : dict
        The 'paper' entry from the papers.yaml database.
    grant_id : str
        The grant id from grants.yaml to query for

    Returns
    -------
    rationale : bool or str
        If a rationale is provided, a str containing the rationale of how the paper aligns with the grant is provided.
        If no rationale is provided, True is returned if the paper contains the grant_id as a funding source, False otherwise.

    """
    try:
        # get list of grants
        for grant in paper['funding']:
            # key: value entries may have a rationale
            if type(grant) is dict:
                if grant['id'] == grant_id:
                    if 'rationale' in grant:
                        # Return rationale if provided
                        return grant['rationale']
                    else:
                        return True
            # If we haven't specified a dict, there can be no rationale
            elif type(grant) is str:
                if grant == grant_id:
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

def show_paper(paper, show_links=False, grant_id=None):
    """Render the paper as Markdown

    Parameters
    ----------
    paper : dict
        The 'paper' entry from the papers.yaml database.
    show_links : bool, optional, default=False
        If True, will display links associated with the paper.
    grant_id : str, optional, default=None
        If specified, print the rationale for how the paper aligns with this grant.

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
        if ('links' in paper) and show_links:
            for link in paper['links']:
                print(f"**{link['action']}:** {link['url']}")

        # Description
        if 'description' in paper:
            print(f"*{paper['description'].rstrip()}*")

        if grant_id is not None:
            rationale = funded_by_grant(paper, grant_id)
            if type(rationale) is str:
                print(f"{rationale.rstrip()}")


    except Exception as e:
        # Give up on rendering if we get stuck
        print(e)
        pass

def show_resources(paper):
    """Show all resources (links) associated with a given paper.
    """
    if ('links' in paper):
        for link in paper['links']:
            if 'description' in link:
                print(f"**{link['description']}:**")
            print(f"*{link['short']}:* {link['url']}")
            print('')

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
        # Use a precendence scheme where we prefer published papers to accepted papers to preprints.
        if published_during_reporting_period(paper):
            papers_to_report['papers were published'].append(paper)
        elif accepted_during_reporting_period(paper):
            papers_to_report['manuscripts were accepted'].append(paper)
        elif preprinted_during_reporting_period(paper):
            papers_to_report['preprints were posted'].append(paper)


    # count papers
    for category in ['papers were published', 'manuscripts were accepted', 'preprints were posted']:
        if (category in papers_to_report) and (len(papers_to_report[category]) > 0):
            n_papers = sum([1 for _ in papers_to_report[category]])
            print(f'{category:30} : {n_papers:4} papers')

    # report papers
    for category in ['papers were published', 'manuscripts were accepted', 'preprints were posted']:
        if (category in papers_to_report) and (len(papers_to_report[category]) > 0):
            print(f'Since the last reporting period, the following {category}, funded by this grant in part or whole:')
            for paper in papers_to_report[category]:
                print('')
                show_paper(paper, grant_id=grant_id)

            print('')


    # Report all resources generated in the last reporting period
    print('------')
    print('')
    print('The following resources corresponding to papers that were published, accepted, or preprinted were generated in the reporting period:')
    print('')

    for category in ['papers were published', 'manuscripts were accepted', 'preprints were posted']:
        if (category in papers_to_report) and (len(papers_to_report[category]) > 0):
            for paper in papers_to_report[category]:
                show_resources(paper)
                show_paper(paper, grant_id=None)

