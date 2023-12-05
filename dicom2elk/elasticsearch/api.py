# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Module that provides functions to interact with Elasticsearch using the Python API."""


from dicom2elk.config import get_config
from dicom2elk.logging import create_logger


from elasticsearch import Elasticsearch, helpers


def send_bulk_to_elasticsearch(
    dcm_tags_list: list, config: str, logger=create_logger("INFO")
):
    """Send list of dictionary representation of the DICOM files to Elasticsearch.

    Args:
        dcm_tags_list (list): List of dictionary representation of the DICOM files.
        config (str): Path to config file in JSON format which defines all variables
                      related to Elasticsearch instance (url, port, index, user, pwd).
        logger (logging.Logger): Logger instance.

    Note:
        The dictionary representation of the DICOM files must contain a "filepath" key.
        This key is used to identify the file in Elasticsearch.
    """
    # Load config file
    config = get_config(config)

    # Connect to Elasticsearch instance
    es = Elasticsearch(
        [config["url"]],
        http_auth=(config["user"], config["pwd"]),
        scheme="https",
        port=config["port"],
    )

    # Create index
    if es.indices.exists(config["index"]):
        logger.warning(f"Index {config['index']} already exists")
    else:
        es.indices.create(config["index"])

    # Bulk upload to Elasticsearch
    actions = [
        {
            "_index": config["index"],
            "_type": "_doc",
            "_id": i,
            "_source": dcm_tags,
        }
        for i, dcm_tags in enumerate(dcm_tags_list)
    ]
    helpers.bulk(es, actions)
