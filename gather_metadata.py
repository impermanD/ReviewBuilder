from db.data import PaperStore, Paper

from search import enrichAndUpdateMetadata, SearchResult
from argparse import ArgumentParser
from db.bibtex import write_bibtex, read_bibtex_file

import re


def getSearchResultsFromBib(bib_entries, max_results):
    results = []
    for index, bib in enumerate(bib_entries[:max_results]):
        res = SearchResult(index, bib, 'bibfile', {})
        if bib.get('note'):
            match = re.search('(\d+)\scites:\s.+?scholar\?cites\=(\d+)', bib['note'])
            if match:
                res.source = 'scholar'
                res.extra_data['scholarid'] = match.group(2)
                res.extra_data['citedby'] = match.group(1)
        results.append(res)

    return results


def main(conf):
    if conf.cache:
        paperstore = PaperStore()
    else:
        paperstore = None

    bib_entries = read_bibtex_file(conf.input)
    results = getSearchResultsFromBib(bib_entries, conf.max)

    found, missing = paperstore.matchResultsWithPapers(results)

    papers_to_add = [Paper(res.bib, res.extra_data) for res in missing]
    successful, unsuccessful = enrichAndUpdateMetadata(papers_to_add, paperstore, conf.email)

    papers_existing = [res.paper for res in found]

    if conf.force:
        enrichAndUpdateMetadata(papers_existing, paperstore, conf.email)

    all_papers = papers_to_add + papers_existing
    write_bibtex(all_papers, conf.output)


if __name__ == '__main__':
    parser = ArgumentParser(
        description='Gathers metadata, including the abstract, on a list of search results by searching on Crossref, PubMed, arXiv, Semantic Scholar and Unpaywall')

    parser.add_argument('-i', '--input', type=str,
                        help='Input Bibtex file with the previously cached search results')
    parser.add_argument('-o', '--output', type=str,
                        help='Output Bbibex file into which to update the new, augmented results')
    parser.add_argument('-m', '--max', type=int, default=100,
                        help='Maximum number of results to process')
    parser.add_argument('-em', '--email', type=str,
                        help='Email to serve as identity to API endpoints')
    parser.add_argument('-c', '--cache', type=bool, default=True,
                        help='Use local cache for results')
    parser.add_argument('-f', '--force', type=bool, default=False,
                        help='Force updating metadata for cached results')

    conf = parser.parse_args()

    main(conf)
