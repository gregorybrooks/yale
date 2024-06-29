import json
import subprocess
import sys
import xml.etree.ElementTree
import entrezpy.conduit
import entrezpy.base.result
import entrezpy.base.analyzer

email = 'gregorybrooks@gmail.com'


class PubmedRecord:
    """Simple data class to store individual Pubmed records. Individual authors will
    be stored as dict('lname':last_name, 'fname': first_name) in authors.
    Citations as string elements in the list citations. """

    def __init__(self):
        self.pmid = None
        self.title = ''
        self.abstract = ''
        self.authors = []
        self.references = []
        self.doc_url = ''
        self.authorstring = ''


class PubmedResult(entrezpy.base.result.EutilsResult):
    """Derive class entrezpy.base.result.EutilsResult to store Pubmed queries.
    Individual Pubmed records are implemented in :class:`PubmedRecord` and
    stored in :ivar:`pubmed_records`.

    :param response: inspected response from :class:`PubmedAnalyzer`
    :param request: the request for the current response
    :ivar dict pubmed_records: storing PubmedRecord instances"""

    def __init__(self, response, request):
        super().__init__(request.eutil, request.query_id, request.db)
        self.pubmed_records = {}

    def size(self):
        """Implement virtual method :meth:`entrezpy.base.result.EutilsResult.size`
        returning the number of stored data records."""
        return len(self.pubmed_records)

    def isEmpty(self):
        """Implement virtual method :meth:`entrezpy.base.result.EutilsResult.isEmpty`
        to query if any records have been stored at all."""
        if not self.pubmed_records:
            return True
        return False

    def get_link_parameter(self, reqnum=0):
        """Implement virtual method :meth:`entrezpy.base.result.EutilsResult.get_link_parameter`.
        Fetching a pubmed record has no intrinsic elink capabilities and therefore
        should inform users about this."""
        print("{} has no elink capability".format(self))
        return {}

    def dump(self):
        """Implement virtual method :meth:`entrezpy.base.result.EutilsResult.dump`.

        :return: instance attributes
        :rtype: dict
        """
        return {self: {'dump': {'pubmed_records': [x for x in self.pubmed_records],
                                'query_id': self.query_id, 'db': self.db,
                                'eutil': self.function}}}

    def add_pubmed_record(self, pubmed_record):
        """The only non-virtual and therefore PubmedResult-specific method to handle
        adding new data records"""
        self.pubmed_records[pubmed_record.pmid] = pubmed_record


class PubmedAnalyzer(entrezpy.base.analyzer.EutilsAnalyzer):
    """Derived class of :class:`entrezpy.base.analyzer.EutilsAnalyzer` to analyze and
    parse PubMed responses and requests."""

    def __init__(self):
        super().__init__()

    def init_result(self, response, request):
        """Implemented virtual method :meth:`entrezpy.base.analyzer.init_result`.
        This method initiate a result instance when analyzing the first response"""
        if self.result is None:
            self.result = PubmedResult(response, request)

    def analyze_error(self, response, request):
        """Implement virtual method :meth:`entrezpy.base.analyzer.analyze_error`. Since
        we expect XML errors, just print the error to STDOUT for
        logging/debugging."""
        print(json.dumps({__name__: {'Response': {'dump': request.dump(),
                                                  'error': response.getvalue()}}}))

    def analyze_result(self, response, request):
        """Implement virtual method :meth:`entrezpy.base.analyzer.analyze_result`.
        Parse PubMed  XML line by line to extract authors and citations.
        xml.etree.ElementTree.iterparse
        (https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.iterparse)
        reads the XML file incrementally. Each  <PubmedArticle> is cleared after processing.

        ..note::  Adjust this method to include more/different tags to extract.
                  Remember to adjust :class:`.PubmedRecord` as well."""
        self.init_result(response, request)
        isAuthorList = False
        isAuthor = False
        isRefList = False
        isRef = False
        isArticle = False
        medrec = None
        for event, elem in xml.etree.ElementTree.iterparse(response, events=["start", "end"]):
            if event == 'start':
                if elem.tag == 'PubmedArticle':
                    medrec = PubmedRecord()
                if elem.tag == 'AuthorList':
                    isAuthorList = True
                if isAuthorList and elem.tag == 'Author':
                    isAuthor = True
                    medrec.authors.append({'fname': '', 'lname': ''})
                if elem.tag == 'ReferenceList':
                    isRefList = True
                if isRefList and elem.tag == 'Reference':
                    isRef = True
                if elem.tag == 'Article':
                    isArticle = True
            else:
                if elem.tag == 'PubmedArticle':
                    medrec.authorstring = '; '.join(str(x['lname'] + "," + x['fname'].replace(' ', '')) for x in medrec.authors)
                    self.result.add_pubmed_record(medrec)
                    elem.clear()
                if elem.tag == 'AuthorList':
                    isAuthorList = False
                if isAuthorList and elem.tag == 'Author':
                    isAuthor = False
                if elem.tag == 'ReferenceList':
                    isRefList = False
                if elem.tag == 'Reference':
                    isRef = False
                if elem.tag == 'Article':
                    isArticle = False
                if elem.tag == 'PMID':
                    medrec.pmid = elem.text.strip()
                    medrec.doc_url = f'https://pubmed.ncbi.nlm.nih.gov/{medrec.pmid}/'
                if isAuthor and elem.tag == 'LastName':
                    medrec.authors[-1]['lname'] = elem.text.strip()
                if isAuthor and elem.tag == 'ForeName':
                    medrec.authors[-1]['fname'] = elem.text.strip()
                if isRef and elem.tag == 'Citation':
                    medrec.references.append(elem.text.strip())
                if isArticle and elem.tag == 'AbstractText':
                    if not medrec.abstract:
                        if elem is not None and elem.text is not None:
                            medrec.abstract = elem.text.strip()
                    else:
                        if elem is not None and elem.text is not None:
                            medrec.abstract += elem.text.strip()
                if isArticle and elem.tag == 'ArticleTitle':
                    if elem is not None and elem.text is not None:
                        medrec.title = elem.text.strip()


def esearch(apikey, prompt):
    a = entrezpy.esearch.esearch_analyzer.EsearchAnalyzer()
    es = entrezpy.esearch.esearcher.Esearcher('esearcher', email, apikey, threads=None)
    a = es.inquire(prompt, analyzer=a)  # this calls e-utilities
    if not a.isSuccess():
        print("\tFailed: Response errors")
        return None
    # Return the list of uids that the search found
    return a.get_result().dump()['uid']


def fetch(idlist):
    c = entrezpy.conduit.Conduit(email)
    fetch_pubmed = c.new_pipeline()
    fetch_pubmed.add_fetch({'db': 'pubmed', 'id': idlist, 'retmode': 'xml'}, analyzer=PubmedAnalyzer())
    return c.run(fetch_pubmed).get_result()


def external_search(num_entries, terms):
    subprocess.run(["/home/greg/run_entrezpy.sh", str(num_entries), str(terms)])
    f = open('/home/greg/pubmed.json')
    data = json.load(f)
    return data


def search(num_entries, terms):
    apikey = None
    prompt = {'db': 'pubmed', 'term': terms, 'rettype': 'abstract', 'usehistory': True, 'retmax': num_entries}

    idlist = esearch(apikey, prompt)
    if idlist is None:
        return None

    res = fetch(idlist)

    num_entries = len(res.pubmed_records)
    current_entry = 0
    json_results = '['
#    print("PMID", "Title", "Abstract", "Authors", "RefCount", "References", "DocumentURL", sep='=')
    for i in res.pubmed_records:
        # print("{}={}={}={}={}={}={}".format(res.pubmed_records[i].pmid, res.pubmed_records[i].title,
        #                                     res.pubmed_records[i].abstract,
        #                                     ';'.join(str(x['lname'] + "," + x['fname'].replace(' ', '')) for x in
        #                                              res.pubmed_records[i].authors),
        #                                     len(res.pubmed_records[i].references),
        #                                     ';'.join(x for x in res.pubmed_records[i].references),
        #                                     res.pubmed_records[i].doc_url))
        current_entry += 1
        json_results += json.dumps(res.pubmed_records[i].__dict__)
        if current_entry < num_entries:
            json_results += ','

    json_results += ']'
    return json_results


if __name__ == '__main__':
    num_entries = sys.argv[1]
    terms = sys.argv[2]
    jstring = search(num_entries, terms)
    with open('/home/greg/pubmed.json', 'w', encoding='utf-8') as f:
        f.write(jstring)
