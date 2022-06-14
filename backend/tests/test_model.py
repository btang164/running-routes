import pytest

from running_routes.network import OSMNetwork
from running_routes.model import CPModel, SavingsModel

@pytest.fixture
def n():
    return 1

@pytest.fixture
def start_coordinate():
    return {"lat": -37.8102361, "lng": 144.9627652}


@pytest.fixture
def sample_percent():
    return 1


@pytest.fixture
def distance():
    return 100


@pytest.fixture
def network(start_coordinate, distance):
    network_instance = OSMNetwork()
    network_instance.create(start_coordinate, distance)
    return network_instance


@pytest.fixture
def cp_model(sample_percent):
    return CPModel(sample_percent=sample_percent, time_limit=2)


class TestCPModel:
    def test_solve(self, n, distance, cp_model, start_coordinate, network) -> None:
        test_results = [[6806666961, 7913378977, 6167279410, 7913378977, 6167279411, 7913378977, 6806666961]]
        results = cp_model.solve(n, distance, start_coordinate, network)
        assert results == test_results

    def test__downsample(self, model, network) -> None:
        # setting sample_percent to 1 will return all nodes in the network
        sample_percent = 1
        seed = 1234
        max_sample_percent = 100
        sample_coordinates = [
            {'lat': -37.8104663, 'lng': 144.962858},
            {'lat': -37.8100645, 'lng': 144.9626779},
            {'lat': -37.810335, 'lng': 144.9632837},
            {'lat': -37.8104393, 'lng': 144.9629538},
        ]
        assert model._downsample(network, sample_percent, max_sample_percent, seed) == sample_coordinates

    def test__find_sample_nodes(self, model, start_coordinate, network) -> None:
        sample_nodes= [6806666961, 6806666963, 2384426953, 6806666960]
        sample_coordinates = [
            {'lat': -37.8104663, 'lng': 144.962858},
            {'lat': -37.8100645, 'lng': 144.9626779},
            {'lat': -37.810335, 'lng': 144.9632837},
            {'lat': -37.8104393, 'lng': 144.9629538},
        ]
        assert model._find_sample_nodes(
            start_coordinate, sample_coordinates, network) == sample_nodes

    def test__construct_distance_matrix(self, model, network) -> None:
        sample_nodes= [6806666961, 6806666963, 2384426953, 6806666960]
        distance_matrix = [
            [0, 47.397, 87.596, 56.332],
            [47.397, 0, 40.199000000000005, 8.935],
            [87.596, 40.199000000000005, 0, 31.264000000000003],
            [56.332, 8.935, 31.264000000000003, 0]
        ]
        assert model._construct_distance_matrix(
            sample_nodes, network) == distance_matrix
