import itertools
import pytest

from running_routes.local_search import BacktrackEliminationLocalSearch
from running_routes.network import OSMNetwork

@pytest.fixture
def start_coordinate():
    return {"lat": -37.8102361, "lng": 144.9627652}


@pytest.fixture
def sample_percent():
    return 1


@pytest.fixture
def distance():
    return 200


@pytest.fixture
def network(start_coordinate, distance):
    network_instance = OSMNetwork()
    network_instance.create(start_coordinate, distance)
    return network_instance


@pytest.fixture
def local_search():
    return BacktrackEliminationLocalSearch()

# class TestBacktrackEliminationLocalSearch:
#     def test_iterate(self, local_search, distance, network):
#         sample_nodes = list(network.graph.nodes.keys())
#         for node1, node2, node3 in itertools.product(sample_nodes, sample_nodes, sample_nodes):
#             out_path = network.path(node1, node2)
#             in_path = network.path(node2, node3)
#             if len(in_path) > 2 and len(out_path) > 2 and in_path[1] != out_path[-2]:
#                 print(out_path)
#                 print(in_path)
#                 break

#         #     if len(path) > 3 and path[1] != 6806666957:
#         #         print(path)
#         # sample_nodes = list(network.graph.nodes.keys())
#         # for sample_node in sample_nodes:
#         #     path = network.path(176693522, sample_node)
#         #     if len(path) > 3 and path[1] != 2384426953:
#         #         print(path)
#         # assert sample_nodes == []

#         # No backtracking
#         # input_tours = [[6806666961, 176693522, 176699680]]
#         # output_tours = [[6806666961, 176693522, 176699680]]
#         # assert output_tours == local_search.iterate(input_tours, distance, network)

#         # Remove backtracking - 176693522 is removed entirely
#         # input_tours = [[6806666961, 176693522, 176693430]]
#         # output_tours = [[6806666961, 176699680]]
#         # assert output_tours == local_search.iterate(input_tours, distance, network)

#         # Remove backtracking - small backtrack
#         input_tours = [[176693380, 176693430, 176699680]]
#         output_tours = [[176693380, 6725404975, 176699680]]
#         assert output_tours == local_search.iterate(input_tours, distance, network)
#         # # Full circle
#         # assert local_search.iterate([[1, 2, 3, 4, 1]], distance, network) == [[1, 2, 3, 4, 1]]

#         # # Backtrack on nodes 10 and 11
#         # assert local_search.iterate([[1, 2, 10, 11, 10, 2, 3, 1]], distance, network) == [[1, 2, 3, 1]]

#         # # Entire tour is a backtrack
#         # assert local_search.iterate([[1, 2, 3, 2, 1]], distance, network) == [[1, 2, 3, 2, 1]]