from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_production_qdrant_is_not_published_on_the_host():
    services = yaml.safe_load((ROOT / "docker-compose.prod.yml").read_text())["services"]
    # Qdrant contains document excerpts and is reachable only over the Compose network.
    assert not services["qdrant"].get("ports")
    assert services["api"]["environment"]["QDRANT_URL"] == "http://qdrant:6333"


def test_demo_services_are_bound_to_loopback():
    services = yaml.safe_load((ROOT / "docker-compose.dev.yml").read_text())["services"]
    assert not services["qdrant"].get("ports")
    assert all(port.startswith("127.0.0.1:") for port in services["api"]["ports"])
