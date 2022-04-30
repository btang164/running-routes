from abc import ABC, abstractmethod

import networkx as nx

from running_routes.network import NetworkFactory

from typing import List, Optional


class LocalSearchFactory(ABC):
    @abstractmethod
    def __init__(self, **parameters):
        pass

    @abstractmethod
    def iterate(
            self, tours: List[List], distance: int, network: NetworkFactory
    ) -> List[List]:
        """Takes a set of routes and reoptimises them"""


class BacktrackEliminationLocalSearch(LocalSearchFactory):
    """Backtracking is a symmetric walk that is a subset of the tour
    The physical analogy is to run down a street, turn around and run back the way you came from

    Example
    The tour [start_node, ..., x, A, B, C, B, A, y, ..., start_node] contains backtracking along
    the nodes [A, B, C]. The local search will remove the backtracking and return
    [start_node, ..., x, y, ..., start_node]
    """
    def __init__(self, **parameters):
        self.parameters = parameters

    def iterate(
            self, tours: List[List], distance: int, network: NetworkFactory) -> List[List]:
        output_tours = []
        for tour in tours:
            G = nx.Graph()
            G.add_edges_from([(x, y) for x, y in zip(tour, tour[1:])])
            node_degrees = {node: degree for (node, degree) in G.degree()}
            single_degree_nodes = [
                node for node, degree in node_degrees.items() if degree == 1 and node != tour[0]]
            three_or_more_degree_nodes = [
                node for node, degree in node_degrees.items() if degree > 2]
            
            if not len(three_or_more_degree_nodes):
                output_tours.append(tour)
            else:
                for single_degree in single_degree_nodes:
                    shortest_paths = nx.single_source_shortest_path(G, single_degree)
                    candidate_paths = [shortest_paths[node] for node in three_or_more_degree_nodes]
                    backtrack_path = sorted(candidate_paths, key=len)[0]
                    G.remove_nodes_from(backtrack_path[:-1])
                output_tour = [tour[0]]
                for node in tour[1:]:
                    if node in G and G.degree[node] > 0 and node != output_tour[-1]:
                        output_tour.append(node)
                output_tours.append(output_tour)
        return output_tours