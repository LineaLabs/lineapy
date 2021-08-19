from typing import List
from lineapy.data.types import DataSourceNode, Node
from lineapy.data.graph import Graph
from lineapy.graph_reader.base import GraphReader


class MetadataExtractor(GraphReader):
    """
    This is a pretty light-weight SINGLE graph metadata extractor
    LineaDB (/db/db.py) contains the the APIs that are called over ALL the data.
    """

    def __init__(self):
        pass

    def identify_data_source(
        self, program: Graph, artifact_node: Node
    ) -> List[DataSourceNode]:
        # there may be more than one source data
        pass

    def score_graph_similarity(self, program_one: Graph, program_two: Graph):
        """
        Note: this is just a stub; do not implement yet.
        We should probably have another function that projects the graph down into some values that we can do similarity score on more easily.
        """

        pass
