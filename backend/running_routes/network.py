from abc import ABC, abstractmethod, abstractproperty

import networkx as nx
import osmnx

from typing import Dict, List


class NetworkFactory(ABC):
    @abstractmethod
    def create(self, start_coordinate: Dict, distance: int, network_type: str) -> None:
        """Create the network graph"""

    @abstractmethod
    def path(self, source: int, target: int) -> List:
        """Returns the path between source and target"""

    @abstractmethod
    def length(self, source: int, target: int, max_distance: int) -> float:
        """Returns the length between source and target"""

    @abstractproperty
    def nodes(self) -> Dict:
        """Returns node data"""


class OSMNetwork(NetworkFactory):
    """Create a network using OSMnx's api"""

    def __init__(self, **parameters) -> None:
        self.graph: nx.DiGraph = None
        self.parameters: Dict = parameters

        self._length: Dict = {}
        self._path: Dict = {}

    def create(self, start_coordinate: Dict, distance: int, network_type: str = "walk") -> None:
        """Downloads the graph and truncates any nodes outside `distance` radius

        Args:
            start_coordinate (Dict): contains the latitude and longitude
            distance (int): distance in meters
            network_type (str, optional): network type according to OSM. Defaults to "walk".
                https://osmnx.readthedocs.io/en/stable/osmnx.html#module-osmnx.graph    
        """
        radius = distance/2
        G = osmnx.graph_from_point(
            (start_coordinate["lat"], start_coordinate["lng"]),
            dist=radius,
            network_type=network_type,
        )
        nodes_outside_radius = [
            node
            for node, data in G.nodes.data()
            if osmnx.distance.great_circle_vec(
                start_coordinate["lat"], start_coordinate["lng"],
                data["y"], data["x"]
            ) > radius
        ]
        G.remove_nodes_from(nodes_outside_radius)
        G = osmnx.utils_graph.get_largest_component(G)
        self.graph = G

    def path(self, source, target) -> List:
        if not self.graph:
            raise Exception("Graph has not been created")
        if source not in self._path:
            self._calculate_dijkstras(source)
        if target not in self.graph:
            raise nx.NodeNotFound(f"{target}")

        return self._path[source][target]

    def length(self, source, target) -> float:
        if not self.graph:
            raise Exception("Graph has not been created")
        if source not in self._length:
            self._calculate_dijkstras(source)
        if target not in self.graph:
            raise nx.NodeNotFound(f"{target}")

        return self._length[source][target]

    def nearest_nodes(self, locations) -> List:
        osm_nodes = osmnx.distance.nearest_nodes(
            self.graph,
            [location["lng"] for location in locations],
            [location["lat"] for location in locations]
        )
        return osm_nodes

    @property
    def nodes(self):
        if not self.graph:
            raise Exception("Graph has not been created")
        return {node: data for node, data in self.graph.nodes(data=True)}

    def _calculate_dijkstras(self, source):
        length, path = nx.single_source_dijkstra(
            self.graph, source, weight="length")
        self._length[source] = length
        self._path[source] = path
