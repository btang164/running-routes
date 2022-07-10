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
        start_node = tours[0][0]
        for tour in tours:
            backtrack_elimination_tour = []
            piecewise_paths = []
            for source, target in zip(tour, tour[1:]):
                piecewise_paths.append(network.path(source, target))
            
            for path1, path2 in zip(piecewise_paths, piecewise_paths[1:]):
                try:
                    first_divergence_index = next(
                        index 
                        for index, (node1, node2) in enumerate(zip(path1[::-1], path2))
                        if node1 != node2)
                except StopIteration:
                    first_divergence_index = 1
                backtrack_elimination_tour.append(path2[first_divergence_index-1])
            output_tours.append(backtrack_elimination_tour + [start_node]) 
        return output_tours