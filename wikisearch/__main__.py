'''Main function for starting wikisearch'''

from bz2 import BZ2File
from gzip import GzipFile

from wikisearch import process_dump
from wikisearch import test_search
from wikisearch import make_sample

from wikisearch.classes.xml_reader import XMLReader
from wikisearch.classes.cirrussearch_reader import CirrusSearchReader

import wikisearch.functions.argument_parser as arg_parser
import wikisearch.functions.file_stream_readers as stream_readers
import wikisearch.functions.parsing_functions as parse_funcs

if __name__ == '__main__':

    # Set and parse command line args
    args=arg_parser.parse_arguments()

    # Decide what to do and how to do it based on
    # user provided arguments

    # Parses xml dump. Can insert into OpenSearch or
    # write article text to files depending on value
    # of output argument
    if args.task == 'process_xml_dump':

        # Start the run
        process_dump.run(
            input_stream=BZ2File(args.dump),
            stream_reader=stream_readers.xml,
            reader_instance=XMLReader(),
            parser_function=parse_funcs.parse_xml_article,
            args=args
        )

    # Bulk inserts a CirrusSearch index directly
    # into OpenSearch
    elif args.task == 'process_cs_dump':

        # Start the run
        process_dump.run(
            input_stream=GzipFile(args.dump),
            stream_reader=stream_readers.json_lines,
            reader_instance=CirrusSearchReader(),
            parser_function=parse_funcs.parse_cirrussearch_article,
            args=args
        )

    # Runs interactive command line search utility
    elif args.task == 'test_search':
        test_search.run(args.index)

    # Takes a small (n=5000) sample of a dump file and saves it
    # for rapid prototyping/testing
    elif args.task == 'make_sample_data':
        make_sample.run(args.dump)


    # Planned - gets new xml dump
    elif args.task == 'update_xml_dump':
        pass

    else:
        print('Unrecognized task, exiting.')
