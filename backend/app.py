import os
from pathlib import Path
import toml

from flask import Flask, request
from flask_cors import CORS

from running_routes.assembler import RestAPIAssembler
from running_routes.local_search import BacktrackEliminationLocalSearch
from running_routes.model import VRPModel
from running_routes.network import OSMNetwork
from running_routes.pipeline import pipeline

BACKEND_ROOT = Path(__file__).parent
PYPROJECT_FILE = BACKEND_ROOT / "pyproject.toml"
with PYPROJECT_FILE.open() as f:
    project_data = toml.load(f)

app = Flask(__name__)
CORS(app)

network = OSMNetwork()
model = VRPModel()
local_searches = [BacktrackEliminationLocalSearch()]
assembler = RestAPIAssembler()

@app.route("/about")
def about():
    return {
        "Running-Routes": {
            "Description": project_data["tool"]["poetry"]["description"],
            "Version": project_data["tool"]["poetry"]["version"],
            "Authors": project_data["tool"]["poetry"]["authors"],
            "License": project_data["tool"]["poetry"]["license"],
        }
    }

@app.route("/pipeline/")
def rest_pipeline():
    arguments = request.args.to_dict()
    n = int(arguments["n"])
    start_coordinate = {"lat": float(arguments["lat"]), "lng": float(arguments["lng"])}
    distance = int(arguments["distance"])
    return pipeline(
        n=n, start_coordinate=start_coordinate, distance=distance, 
        network=network, model=model, local_searches=local_searches, assembler=assembler
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))