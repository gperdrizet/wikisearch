'''Contains various functions for handling input.output of data
and related helper functions.'''

from __future__ import annotations
import time
from opensearchpy import OpenSearch


def write_file(
    output_queue: multiprocessing.Queue, # type: ignore
    article_source: str
) -> None:

    '''Takes documents from parser's output queue, writes to file.'''

    # Loop forever
    while True:

        # Get article from queue
        output=output_queue.get()

        # Extract title and text
        title=output[1]['doc']['title']
        content=str(output[0]) + '\n' + str(output[1])

        # Format page title for use as a filename
        file_name=title.replace(' ', '_')
        file_name=file_name.replace('/', '-')

        # Construct output path
        output = f'wikisearch/data/articles/{article_source}/{file_name}'

        # Save article to a file
        with open(output, 'w', encoding="utf-8") as text_file:
            text_file.write(f'{title}\n{content}')


def display_status(
    input_queue: multiprocessing.Queue, # type: ignore
    output_queue: multiprocessing.Queue, # type: ignore
    reader_instance: CirrusSearchReader, # type: ignore
) -> None:

    '''Prints queue sizes and articles read every second'''

    print('\n\n\n')

    while True:
        print('\033[F\033[F\033[F', end='')
        print(f'Input queue size: {input_queue.qsize()}')
        print(f'Output queue size: {output_queue.qsize()}')
        print(f'Reader count: {reader_instance.status_count}')
        time.sleep(1)

def start_client() -> OpenSearch:

    '''Fires up the OpenSearch client'''

    # Set host and port
    host='localhost'
    port=9200

    # Create the client with SSL/TLS and hostname verification disabled.
    client=OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_compress=False,
        timeout=30,
        use_ssl=False,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False
    )

    return client

def initialize_index(index_name: str) -> None:

    '''Set-up OpenSearch index. Deletes index if it already exists
    at run start. Creates new index for run.'''

    client=start_client()

    # Delete the index we are trying to create if it exists
    if client.indices.exists(index=index_name):
        _=client.indices.delete(index=index_name)

    # Create the target index if it does not exist
    if client.indices.exists(index=index_name) is False:

        # Create index
        index_body={
            'settings': {
                'index': {
                    'number_of_shards': 3 # Generic advice is 10-50 GB of data per shard
                }
            }
        }

        _=client.indices.create(index_name, body=index_body)

    # Close client
    client.close()
