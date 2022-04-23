import networkx as nx
import pytest

from running_routes.network import OSMNetwork

@pytest.fixture
def start_coordinate():
    return {"lat": -37.8102361, "lng": 144.9627652}

class TestOSMNetwork:
    def test_init(self):
        network = OSMNetwork()
        assert network.graph == None

    def test_create(self, start_coordinate):
        """Download the network around Melbourne Central"""
        network = OSMNetwork()

        # No nodes in the requested polygon
        with pytest.raises(ValueError):
            network.create(start_coordinate, distance=20, network_type="walk")

        # Four nodes in the bbox around the location
        # - Three in the bbox and radius: 2384426953, 6806666960, 6806666961, 6806666963
        # - One in the bbox and not in the radius: 176693380
        network.create(start_coordinate, distance=100, network_type="walk")
        nodes_in = [2384426953, 6806666960, 6806666961, 6806666963]
        assert nodes_in == sorted(network.nodes.keys())
        assert 176693380 not in network.nodes.keys()

    def test_path(self, start_coordinate):
        distance = 100
        network = OSMNetwork()

        # Need to call `create`
        with pytest.raises(Exception):
            network.path(2384426953, 6806666960)

        # Check for invalid arguments
        network.create(start_coordinate, distance)
        with pytest.raises(nx.NodeNotFound):
            network.path("invalid", 2384426953)
        with pytest.raises(nx.NodeNotFound):
            network.path(2384426953, "invalid")

        # Validate correctness
        assert [2384426953, 6806666960] == network.path(2384426953, 6806666960)

    def test_distance(self, start_coordinate):
        distance = 100
        network = OSMNetwork()

        # Need to call `create`
        with pytest.raises(Exception):
            network.length(2384426953, 6806666960)

        # Check for invalid arguments
        network.create(start_coordinate, distance)
        with pytest.raises(nx.NodeNotFound):
            network.length("invalid", 2384426953)
        with pytest.raises(nx.NodeNotFound):
            network.length(2384426953, "invalid")

        # Validate correctness
        # ~31.264m
        assert 31 <= network.length(2384426953, 6806666960) <= 32

    def test_nodes(self, start_coordinate):
        # Nodes can only be called if the network is created
        with pytest.raises(Exception):
            network = OSMNetwork()
            network.nodes
        
        # The longatidue and latitude is accessible from nodes
        network = OSMNetwork()
        network.create(start_coordinate, 100)
        for _, data in network.nodes.items():
            assert "x" in data and "y" in data

    def test_nearest_nodes(self, start_coordinate):
        distance = 100

        network = OSMNetwork()
        network.create(start_coordinate, distance)
        assert network.nearest_nodes([start_coordinate]) == [6806666961]
