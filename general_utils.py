from db.bibtex import readBibtexFile
from db.data import PaperStore, Paper
from export_to_ris import conf
from search import getSearchResultsFromBib


def loadEntriesAndSetUp(input, use_cache, max_results):
    if conf.cache:
        paperstore = PaperStore()
    else:
        paperstore = None

    bib_entries = readBibtexFile(input)
    results = getSearchResultsFromBib(bib_entries, max_results)

    if paperstore:
        found, missing = paperstore.matchResultsWithPapers(results)
    else:
        found = []
        missing = results

    papers_to_add = [Paper(res.bib, res.extra_data) for res in missing]
    papers_existing = [res.paper for res in found]

    all_papers = papers_to_add + papers_existing

    return paperstore, papers_to_add, papers_existing, all_papers