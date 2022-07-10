import pytest

from running_routes.assembler import TourAssembler
from running_routes.local_search import BacktrackEliminationLocalSearch
from running_routes.model import CPModel
from running_routes.network import OSMNetwork
from running_routes.pipeline import pipeline


@pytest.fixture
def n():
    return 1


@pytest.fixture
def start_coordinate():
    return {"lat": -37.8102361, "lng": 144.9627652}


@pytest.fixture
def distance():
    return 200


@pytest.fixture
def network():
    return OSMNetwork()


@pytest.fixture
def model():
    return CPModel()


@pytest.fixture
def local_searches():
    return [BacktrackEliminationLocalSearch()]


@pytest.fixture
def assembler():
    return TourAssembler()


def test_pipeline(n, start_coordinate, distance, network, model, assembler, local_searches):
    pipeline(
        n, start_coordinate, distance,
        network=network, model=model, local_searches=local_searches, assembler=assembler)
