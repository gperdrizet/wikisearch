'''Functions to parse data read from dumps and related helper functions'''

import multiprocessing
import mwparserfromhell # type: ignore

def parse_cirrussearch_article(
    input_queue: multiprocessing.Queue,
    output_queue: multiprocessing.Queue,
    index_name: str
) -> None:

    '''Parses JSON lines data read from a CirrusSearch dump.'''

    while True:

        # Get the header and the content source from the article queue
        header, content, article_num=input_queue.get()

        # Make some updates to the header to make it compatible with OpenSearch
        header=update_cs_index(header, index_name, article_num)

        # Alter the content format for upserting
        upsert_content={}
        upsert_content['doc']=content
        upsert_content['doc_as_upsert']='true'

        # Put the result into the output queue
        output_queue.put((header, upsert_content))

def update_cs_index(
    line: dict,
    index_name: str,
    id_num: int
) -> dict:

    '''Make some changes to index lines from CirrusSearch
    dump to make it compatible with OpenSearch'''

    # Remove unsupported '_type'
    line['index'].pop('_type', None)

    # Add index name
    line['index']['_index']=index_name

    # Replace the id with a sequential number
    line['index']['_id']=id_num

    # Change index key to update for upserting
    line['update']=line.pop('index')

    return line

def parse_xml_article(
    input_queue: multiprocessing.Queue,
    output_queue: multiprocessing.Queue,
    index_name: str
) -> None:

    '''Parses Wikicode page source recovered from XML dump.'''

    while True:

        # Get the page title and the content source from the article queue
        page_title, source, article_num=input_queue.get()

        # Convert source string to wikicode
        wikicode=mwparserfromhell.parse(source)

        # Strip garbage out of wikicode source
        source_string=wikicode.strip_code(
            normalize=True,
            collapse=True,
            keep_template_params=False
        )

        # Before we do anything else, check to see if this is a redirect
        # page. If so, we can just skip it.
        if 'REDIRECT' not in source_string.split('\n')[0].upper():

            # Remove extra sections from the end of the document
            source_string=remove_extra_sections(source_string)

            # Do some string replacements
            source_string=fix_bad_symbols(source_string)

            # Clean up newlines
            source_string=clean_newlines(source_string)

            # Get rid of image thumbnail lines and leading spaces
            source_string=remove_thumbnails(source_string)

            # Create formatted dicts for the request and the
            # content to send to open search
            request_header={
                'update': {
                    '_index': index_name, 
                    '_id': article_num
                }
            }

            formatted_article={
                'doc': {
                    'title': page_title, 
                    'text': source_string
                },
                'doc_as_upsert': 'true'
            }

            # Put the result into the output queue
            output_queue.put((request_header, formatted_article))


def fix_bad_symbols(source_string: str) -> str:
    '''Fixes some weird punctuation and symbols left over after
    code is stripped by mwparserfromhell'''

    source_string=source_string.replace('–', '-')
    source_string=source_string.replace('(/', '(')
    source_string=source_string.replace('/)', ')')
    source_string=source_string.replace('(, ', '(')
    source_string=source_string.replace('( , ; ', '(')
    source_string=source_string.replace(' ', ' ')
    source_string=source_string.replace('′', '`')
    source_string=source_string.replace('(: ', '(')
    source_string=source_string.replace('(; ', '(')
    source_string=source_string.replace('( ', '(')
    source_string=source_string.replace(' )', ')')
    source_string=source_string.replace('皖', '')
    source_string=source_string.replace('()', '')
    source_string=source_string.replace('(;)', '')
    source_string=source_string.replace(' ; ', '; ')
    source_string=source_string.replace('(,', '(')
    source_string=source_string.replace(',)', ')')
    source_string=source_string.replace(',),', ',')
    source_string=source_string.replace(',“', ', "')
    source_string=source_string.replace('( ;)', '')
    source_string=source_string.replace('(;', '(')
    source_string=source_string.replace(' .', '.')
    source_string=source_string.replace(';;', ';')
    source_string=source_string.replace(';\n', '\n')
    source_string=source_string.replace(' ,', ',')
    source_string=source_string.replace(',,', ',')
    source_string=source_string.replace('−', '-')
    source_string=source_string.replace('۝ ', '')
    source_string=source_string.replace('۝', '')


    # Need to do this one last, some of the above
    # replace-with-nothings leave double spaces
    source_string=source_string.replace('  ', ' ')

    return source_string

def clean_newlines(source_string: str) -> str:
    '''Fixes up some issues with multiple newlines'''

    source_string=source_string.replace(' \n', '\n')
    source_string=source_string.replace('\n\n\n\n\n\n', '\n\n')
    source_string=source_string.replace('\n\n\n\n\n', '\n\n')
    source_string=source_string.replace('\n\n\n\n', '\n\n')
    source_string=source_string.replace('\n\n\n', '\n\n')
    source_string=source_string.replace('\n\n\n', '\n')
    source_string=source_string.replace('\n\n\n', '\n\n')

    return source_string

def remove_thumbnails(source_string: str) -> str:
    '''Removes thumbnail descriptor lines and cleans up any
    lines with leading spaces'''

    # Empty list for cleaned lines
    cleaned_source_array=[]

    # Split the source string on newlines
    source_array=source_string.split('\n')

    # Loop on the line array
    for line in source_array:

        # Only take lines that don't contain leftover HTML stuff
        if 'thumb|' in line:
            pass

        elif 'scope="' in line:
            pass

        elif 'rowspan="' in line:
            pass

        elif 'style="' in line:
            pass

        # If we don't find any of the above, process the line
        else:

            # Check for lines that are not blank but start with space
            # or other garbage
            if len(line) > 1:

                if line[0] == ' ':
                    line=line[1:]

                if line[:2] == '| ':
                    line=line[2:]

                if line[:2] == '! ':
                    line=line[2:]

                if line[:2] == '! ':
                    line=line[2:]

                if line[:2] == '|-':
                    line=line[2:]

                if line[:2] == '|}':
                    line=line[2:]

            # Add the cleaned line to the result
            cleaned_source_array.append(line)

    # Join the cleaned lines back to a string
    source_string='\n'.join(cleaned_source_array)

    return source_string

def remove_extra_sections(source_string: str) -> str:
    '''Remove extra sections from the end of the document by splitting 
    on common headings only keeping the stuff before the split point'''

    source_string=source_string.split('See also')[0]
    source_string=source_string.split('References')[0]
    source_string=source_string.split('External links')[0]
    source_string=source_string.split('Notes')[0]

    return source_string
