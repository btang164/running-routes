import click

from running_routes.assembler import TourAssembler, AssemblerFactory
from running_routes.local_search import LocalSearchFactory, BacktrackEliminationLocalSearch
from running_routes.model import ModelFactory, VRPModel
from running_routes.network import NetworkFactory, OSMNetwork

from typing import Dict, List, Optional

_HELP_COMMAND_STRING = """I want to run {distance}m, {n} times , around {lat, lng}.

Example

distance = 200, n = 5, lat = -37.8102361, lng = 144.9627652
-- Lat long coordinate corresponds to Melbourne Central, Melbourne, Victoria, Australia
"""


def pipeline(
        n: int, start_coordinate: Dict, distance: int,
        network: NetworkFactory, model: ModelFactory,
        assembler: AssemblerFactory,
        local_searches: Optional[List[LocalSearchFactory]] = None,
):
    network.create(start_coordinate, distance)
    tours = model.solve(n, distance, start_coordinate, network)
    for local_search in local_searches:
        tours = local_search.iterate(tours, distance, network)
    routes = assembler.generate_output(tours, distance, network)
    return routes


@click.command(context_settings=dict(max_content_width=600), help=_HELP_COMMAND_STRING)
@click.option("--distance", type=click.IntRange(500, 10000), required=True)
@click.option("--n", type=click.IntRange(1, 10), required=True)
@click.option("--lat", type=float, required=True)
@click.option("--lng", type=float, required=True)
def _cli(distance, n, lat, lng):
    network = OSMNetwork()
    model = VRPModel()
    local_searches = [BacktrackEliminationLocalSearch()]
    assembler = TourAssembler()

    routes = pipeline(
        n, {"lat": lat, "lng": lng}, distance,
        network=network, model=model, local_searches=local_searches,
        assembler=assembler)

    for route in routes:
        print(route)
        print("")
