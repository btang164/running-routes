from abc import ABC, abstractmethod
import itertools

import networkx as nx
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from sklearn.cluster import KMeans

from running_routes.network import NetworkFactory

from typing import Dict, List, Tuple

VRP_DEFAULT_PARAMETERS = {
    "sample_percent": 0.2,
    "max_sample_size": 100,
    "seed": 1234,
    "time_limit": 10
}


class ModelFactory(ABC):
    """Factory that represents different model implementations"""
    @abstractmethod
    def __init__(self, **kwargs):
        """Load parameters"""

    @abstractmethod
    def solve(self, n: int, distance: int, start_coordinate: Dict, network: NetworkFactory) -> List[List]:
        """Creates and solves the model"""


class VRPModel(ModelFactory):
    """
    Implements a vehicle routing problem based model through
    constraint programming and OR-tools

    https://developers.google.com/optimization/routing/vrp
    https://developers.google.com/optimization/routing/penalties
    """

    def __init__(self, **parameters):
        self.parameters = parameters

        # Set default parameters
        for key, value in VRP_DEFAULT_PARAMETERS.items():
            if key not in self.parameters:
                self.parameters[key] = value

    def solve(self, n: int, distance: int, start_coordinate: Dict, network: NetworkFactory) -> List[List]:
        sample_coordinates = self._downsample(
            network, self.parameters["sample_percent"], self.parameters["max_sample_size"], self.parameters["seed"])
        sample_nodes = self._find_sample_nodes(start_coordinate, sample_coordinates, network)
        distance_matrix = self._construct_distance_matrix(sample_nodes, network)
        manager, routing = self._construct_cp_model(n, distance, distance_matrix)
        assignment = self._solve_cp_model(
            routing, self.parameters["time_limit"])
        results = self._generate_results(
            n, sample_nodes, network,
            routing, manager,
            assignment)
        return results

    def _downsample(self, network: NetworkFactory, sample_percent: float, max_sample_size: int, seed: int) -> List[Dict]:
        """Downsample using KMeans"""
        coordinates = [
            [data["y"], data["x"]]
            for _, data in network.nodes.items()
        ]
        percent_sample_size = int(len(coordinates)*sample_percent)
        sample_size = percent_sample_size if percent_sample_size < max_sample_size else max_sample_size
        kmeans = KMeans(n_clusters=sample_size,
                        random_state=seed).fit(coordinates)
        sample_coordinates = [
            {"lat": center[0], "lng": center[1]}
            for center in kmeans.cluster_centers_
        ]
        return sample_coordinates

    def _find_sample_nodes(
                self, start_coordinate: Dict, sample_coordinates: List[Dict],
                network: NetworkFactory) -> List:
        # `location` is the zeroth element by construction
        # Remove any duplicate nodes
        # https://stackoverflow.com/a/17016257
        model_coordinates = [start_coordinate] + sample_coordinates
        nearest_nodes = network.nearest_nodes(model_coordinates)
        sample_nodes = list(dict.fromkeys(nearest_nodes))
        return sample_nodes

    def _construct_distance_matrix(self, sample_nodes: List, network: NetworkFactory) -> List[List[float]]:
        # If there are no path between source and target, return `self.total_length`
        distance_matrix = []
        for source in sample_nodes:
            distance_from_source = []
            for target in sample_nodes:
                try:
                    length = network.length(source, target)
                except nx.NodeNotFound:
                    length = self.distance
                distance_from_source.append(length)
            distance_matrix.append(distance_from_source)

        return distance_matrix

    def _construct_cp_model(
            self, n: int, distance: int,
            distance_matrix: List[List],
    ) -> Tuple[pywrapcp.RoutingIndexManager, pywrapcp.RoutingModel]:
        """
        Follows the vrp model with drop penalties
        https://developers.google.com/optimization/routing/vrp
        """
        if not distance_matrix:
            raise Exception("Invalid distance_matrix")

        # The depot is the zeroth element by construction
        manager = pywrapcp.RoutingIndexManager(
            len(distance_matrix), n, 0)
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            """
            Create and register transit callback
            Returns the distance between the two nodes
            """
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return distance_matrix[from_node][to_node]
        transit_callback_index = routing.RegisterTransitCallback(
            distance_callback)

        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        dimension_name = "distance"
        routing.AddDimension(
            transit_callback_index, 0, distance, True, dimension_name)

        # Add the ability to drop nodes for a penalty
        drop_penalty = n*distance
        for node in range(1, len(distance_matrix)):
            routing.AddDisjunction([manager.NodeToIndex(node)], drop_penalty)

        return manager, routing

    def _solve_cp_model(
            self, routing: pywrapcp.RoutingIndexManager, time_limit: float
    ) -> pywrapcp.Assignment:
        # Use the suggested search strategy
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
        search_parameters.time_limit.seconds = time_limit

        assignment = routing.SolveWithParameters(search_parameters)
        return assignment

    def _generate_results(
            self,
            n: int,
            candidate_nodes: List,
            network: NetworkFactory,
            routing: pywrapcp.RoutingIndexManager,
            manager: pywrapcp.RoutingModel,
            assignment: pywrapcp.Assignment) -> List[List]:
        """Returns the paths in the context of network nodes"""
        results = []

        for route_id in range(n):
            index = routing.Start(route_id)
            candidate_tour = []
            single_route = []

            # Extract the tour from candidate nodes and cp model
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                candidate_tour.append(candidate_nodes[node_index])
                index = assignment.Value(routing.NextVar(index))
            node_index = manager.IndexToNode(index)
            candidate_tour.append(candidate_nodes[node_index])

            # Join the tour with the shortest paths
            for source, target in zip(candidate_tour, candidate_tour[1:]):
                single_route.extend(network.path(source, target))
            single_route += [single_route[0]]

            # Remove any duplicate nodes in the route
            dedup_nodes = [group[0] for group in itertools.groupby(single_route)]
            results.append(dedup_nodes)
        return results
