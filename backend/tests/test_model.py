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
    return 200


@pytest.fixture
def network(start_coordinate, distance):
    network_instance = OSMNetwork()
    network_instance.create(start_coordinate, distance)
    return network_instance


@pytest.fixture
def cp_model(sample_percent):
    return CPModel(sample_percent=sample_percent, time_limit=2)

@pytest.fixture
def savings_model(sample_percent):
    return SavingsModel(sample_percent=sample_percent)

class TestCPModel:
    def test_solve(self, n, distance, cp_model, start_coordinate, network) -> None:
        test_results = [[6806666961, 7913378977, 6167279410, 7913378977, 6167279411, 7913378977, 6806666961]]
        results = cp_model.solve(n, distance, start_coordinate, network)
        assert results == test_results

    def test__downsample(self, cp_model, network) -> None:
        # setting sample_percent to 1 will return all nodes in the network
        sample_percent = 1
        seed = 1234
        max_sample_percent = 100
        sample_coordinates = [
            {'lat': -37.8108737, 'lng': 144.9631356},
            {'lat': -37.8102442, 'lng': 144.9621553},
            {'lat': -37.8101955, 'lng': 144.963686},
            {'lat': -37.8107574, 'lng': 144.9636583},
            {'lat': -37.8100645, 'lng': 144.9626779},
            {'lat': -37.810335, 'lng': 144.9632837},
            {'lat': -37.8104663, 'lng': 144.962858},
            {'lat': -37.8105339, 'lng': 144.9634555},
            {'lat': -37.8109981, 'lng': 144.9628452},
            {'lat': -37.8106851, 'lng': 144.9624361},
            {'lat': -37.8100454, 'lng': 144.9638521},
            {'lat': -37.8104393, 'lng': 144.9629538},
            {'lat': -37.8101553, 'lng': 144.9638469},
            {'lat': -37.8101334, 'lng': 144.9621113},
            {'lat': -37.8105126, 'lng': 144.9635476},
            {'lat': -37.8109074, 'lng': 144.9631515},
            {'lat': -37.8107249, 'lng': 144.9636447},
            {'lat': -37.8109391, 'lng': 144.9631663},
            {'lat': -37.8110299, 'lng': 144.9628595},
            {'lat': -37.810221, 'lng': 144.9621461}
        ]
        assert cp_model._downsample(network, sample_percent, max_sample_percent, seed) == sample_coordinates

    def test__find_sample_nodes(self, cp_model, start_coordinate, network) -> None:
        sample_nodes= [6806666961, 6806666963, 2384426953, 6806666960]
        sample_coordinates = [
            {'lat': -37.8104663, 'lng': 144.962858},
            {'lat': -37.8100645, 'lng': 144.9626779},
            {'lat': -37.810335, 'lng': 144.9632837},
            {'lat': -37.8104393, 'lng': 144.9629538},
        ]
        assert cp_model._find_sample_nodes(
            start_coordinate, sample_coordinates, network) == sample_nodes

    def test__construct_distance_matrix(self, cp_model, network) -> None:
        sample_nodes= [6806666961, 6806666963, 2384426953, 6806666960]
        distance_matrix = [
            [0, 47.397, 87.596, 56.332],
            [47.397, 0, 40.199000000000005, 8.935],
            [87.596, 40.199000000000005, 0, 31.264000000000003],
            [56.332, 8.935, 31.264000000000003, 0]
        ]
        assert cp_model._construct_distance_matrix(sample_nodes, network) == distance_matrix

class TestSavingsModel:
    def test__calculate_savings(self, savings_model, network):
        # 6806666961 is the closest node to start_coordinate
        sample_nodes = [6806666961, 6806666963, 2384426953, 6806666960]
        rounded_savings = {
            (6806666963, 2384426953): 94,
            (6806666963, 6806666960): 94,
            (2384426953, 6806666960): 112, }

        for key, val in savings_model._calculate_savings(sample_nodes, network).items():
            assert rounded_savings[key] == int(val)
    
    def test__rotate_interior_route(self, savings_model):
        # Raise an Exception because "c" is not adjacent to "a"
        input_route = ["start_node", "a", "b", "c", "d", "e", "f", "start_node"]
        with pytest.raises(Exception):
            savings_model._rotate_interior_route(input_route, "c", "a") == output_route

        # Start the interior route around "c"
        input_route = ["start_node", "a", "b", "c", "d", "e", "f", "start_node"]
        output_route = ["c", "d", "e", "f", "a", "b"]
        assert output_route == savings_model._rotate_interior_route(input_route, "c")

        # Start the interior route around "c" and end with "b"
        input_route = ["start_node", "a", "b", "c", "d", "e", "f", "start_node"]
        output_route = ["c", "d", "e", "f", "a", "b"]
        assert output_route == savings_model._rotate_interior_route(input_route, "c", "b")

        # Start the interior route around "c" and end with "d"
        input_route = ["start_node", "a", "b", "c", "d", "e", "f", "start_node"]
        output_route = ["c", "b", "a", "f", "e", "d"]
        assert output_route == savings_model._rotate_interior_route(input_route, "c", "d") 

    def test__split_route(self, savings_model):
        # Raise an Exception because "c" is not adjacent to "a"
        input_route = ["start_node", "a", "b", "c", "d", "e", "f", "start_node"]
        with pytest.raises(Exception):
            savings_model._split_route(input_route, "c", "a")
            
        # Split route on "c", "d"
        input_route = ["start_node", "a", "b", "c", "d", "e", "f", "start_node"]
        first_split, second_split = ["start_node", "a", "b", "c"], ["d", "e", "f", "start_node"]
        assert first_split, second_split == savings_model._split_route(input_route, "c", "d" ) 

        # Split route on "d", "c"
        input_route = ["start_node", "a", "b", "c", "d", "e", "f", "start_node"]
        first_split, second_split = ["start_node", "f", "e", "d"], ["c", "b", "a", "start_node"]
        assert first_split, second_split == savings_model._split_route(input_route, "d", "c") 

    def test__merge_routes(self, savings_model, network, distance):
        # Do not merge routes if saving are in the same route
        saving = (6806666963, 2384426953)
        input_routes = [[6806666961, 6806666963, 2384426953, 6806666961], [6806666961, 6806666960, 6806666961]]
        output_routes = [[6806666961, 6806666963, 2384426953, 6806666961], [6806666961, 6806666960, 6806666961]]
        assert output_routes == savings_model._merge_routes(saving, input_routes, network, max_node=8, distance=distance)

        # Do not merge if the max node constraint is violated
        saving = (6806666963, 2384426953)
        input_routes = [[6806666961, 6806666963, 6806666961], [6806666961, 2384426953, 6806666961]]
        output_routes = [[6806666961, 6806666963, 6806666961], [6806666961, 2384426953, 6806666961]]
        assert output_routes == savings_model._merge_routes(saving, input_routes, network, max_node=3, distance=distance)

        # Do not merge if the distance constraint is violated
        saving = (6806666963, 2384426953)
        input_routes = [
            [6806666961, 6806666963, 6806666960, 6806666961],
            [6806666961, 2384426953, 6806666961],
            ]
        output_routes = [
            [6806666961, 6806666963, 6806666960, 6806666961],
            [6806666961, 2384426953, 6806666961],
            ]
        assert output_routes == savings_model._merge_routes(saving, input_routes, network, max_node=9, distance=10)

        # Merge two routes if saving contains two exterior nodes
        saving = (6806666963, 2384426953)
        input_routes = [
            [6806666961, 6806666963, 6806666960, 6806666961],
            [6806666961, 2384426953, 6806666961],
            ]
        output_routes = [[6806666961, 6806666960, 6806666963, 2384426953, 6806666961]]
        assert output_routes == savings_model._merge_routes(saving, input_routes, network, max_node=9, distance=1000)

        # Merge two routes if saving contains one exterior node
        saving = (6806666963, 2384426953)
        input_routes = [
            [6806666961, 176693380, 6806666963, 6806666960, 6806666961],
            [6806666961, 2384426953, 6806666961],
            ]
        output_routes = [[6806666961, 176693380, 6806666963, 2384426953, 6806666960, 6806666961]]
        assert output_routes == savings_model._merge_routes(saving, input_routes, network, max_node=9, distance=1000)

        # Merge two routes if saving contains no exterior nodes
        saving = (6806666963, 2384426953)
        input_routes = [
            [6806666961, 176693380, 6806666963, 6806666960, 6806666961],
            [6806666961, 6167279411, 2384426953, 6806666958, 6806666961],
            ]
        output_routes = [[
            6806666961, 6806666958, 2384426953, 6806666963,  
            176693380,  6806666960,  6167279411,  6806666961]]
        assert output_routes == savings_model._merge_routes(saving, input_routes, network, max_node=100, distance=10000)