'''Default configuration. Parameters here can be overridden via
command line arguments. This file exists to collect defaults
in one, easy-to-read place.'''

# Number of workers to start for parsing documents
XML_PARSE_WORKERS=15
CS_PARSE_WORKERS=1

# Number of workers to start for outputting parsed
# documents to file or OpenSearch index
XML_OUTPUT_WORKERS=1
CS_OUTPUT_WORKERS=4

# Number of documents to index via bulk call to OpenSearch
BULK_BATCH_SIZE=100

# Dump data files
XML_INPUT_FILE='wikisearch/data/enwiki-20240320-pages-articles-multistream.xml.bz2'
CS_INPUT_FILE='wikisearch/data/enwiki-20240401-cirrussearch-content.json.gz'

# OpenSearch index names
XML_INDEX='enwiki-xml'
CS_INDEX='enwiki-cs'

# Index to use for search test
TEST_SEARCH_INDEX='enwiki-xml'
