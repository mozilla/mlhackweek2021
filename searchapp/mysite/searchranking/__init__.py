from glean import load_metrics, load_pings
from glean import Glean
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("glean").setLevel(logging.DEBUG)

metrics_file = Path(__file__).parent / "glean_config" / "metrics.yaml"
metrics = load_metrics(metrics_file)
pings_file = Path(__file__).parent / "glean_config" / "pings.yaml"
pings = load_pings(pings_file)

Glean.initialize(
    application_id="mlhackweek-search",
    application_version="0.1.0",
    upload_enabled=True,
    data_dir=Path(__file__).parent  # TODO GLE verify what this should be
)

domains_filename = Path(__file__).parent / "domains.txt"
domains_file = open(domains_filename, "r")
domains = domains_file.read().splitlines()
domains_file.close()
print(f"Using domains: {domains}")