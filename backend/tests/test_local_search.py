import pytest

from running_routes.local_search import BacktrackEliminationLocalSearch
from running_routes.network import OSMNetwork

@pytest.fixture
def distance():
    return 100
@pytest.fixture
def network():
    return OSMNetwork()

@pytest.fixture
def local_search():
    return BacktrackEliminationLocalSearch()

class TestBacktrackEliminationLocalSearch:
    def test_iterate(self, local_search, distance, network):
        # Full circle
        assert local_search.iterate([[1, 2, 3, 4, 1]], distance, network) == [[1, 2, 3, 4, 1]]

        # Backtrack on nodes 10 and 11
        assert local_search.iterate([[1, 2, 10, 11, 10, 2, 3, 1]], distance, network) == [[1, 2, 3, 1]]

        # Entire tour is a backtrack
        assert local_search.iterate([[1, 2, 3, 2, 1]], distance, network) == [[1, 2, 3, 2, 1]]