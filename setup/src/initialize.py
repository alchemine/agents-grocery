"""Initialize Elasticsearch."""

from pathlib import Path
from typing import Any, Optional

import requests

from config import (
    ELASTICSEARCH_URL,
    ELASTICSEARCH_USER,
    ELASTICSEARCH_PASSWORD,
    ROOT_DIR,
)
from src.common.logger import log_info, log_warning, log_error, log_success
from src.common.loader import load_yaml


MAPPINGS_DIR = ROOT_DIR / "mappings"


def es_request(
    method: str,
    path: str,
    json_body: Optional[dict[str, Any]] = None,
    acceptable_status: Optional[list[int]] = None,
) -> requests.Response:
    """Send HTTP request to Elasticsearch and return response."""
    resp = requests.request(
        method,
        f"{ELASTICSEARCH_URL}{path}",
        headers={"Content-Type": "application/json"},
        auth=(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD),
        json=json_body,
        timeout=30,
    )
    if acceptable_status is None:
        acceptable_status = [200]
    if resp.status_code not in acceptable_status:
        raise RuntimeError(f"ES {method} {path} failed: {resp.status_code} {resp.text}")
    return resp


def wait_for_elasticsearch() -> None:
    """Wait for Elasticsearch to be available."""
    resp = es_request("GET", "/_cluster/health", acceptable_status=[200])
    cluster_status = resp.json().get("status", "unknown")
    log_success(f"ES cluster health: {cluster_status}")


def create_ilm_policies(root: Path) -> None:
    """Create ILM policies from directory."""
    ilm_policies = load_yaml(root / "ilm_policy.yaml")
    for policy_name, policy_body in ilm_policies.items():
        put_ilm(policy_name, policy_body)


def put_ilm(policy_name: str, policy_body: dict[str, Any]) -> None:
    """Create ILM policy or skip if already exists."""
    # Check if ILM policy exists
    resp = es_request(
        "GET", f"/_ilm/policy/{policy_name}", acceptable_status=[200, 404]
    )
    if resp.status_code == 200:
        log_info(f"ILM policy '{policy_name}' already exists; skip")
        return

    es_request(
        "PUT",
        f"/_ilm/policy/{policy_name}",
        json_body=policy_body,
        acceptable_status=[200],
    )
    log_success(f"Created ILM policy '{policy_name}'")


def create_indices(root: Path) -> None:
    """Create indices from directory."""
    for path in root.glob("index/*.yaml"):
        config = load_yaml(path)
        put_index_template(config.index_template.name, config.index_template.body)
        create_index(config.index.name, config.index.body)


def put_index_template(template_name: str, template_body: dict[str, Any]) -> None:
    """Create index template or skip if already exists."""
    # Check if template exists
    resp = es_request(
        "GET", f"/_index_template/{template_name}", acceptable_status=[200, 404]
    )
    if resp.status_code == 200:
        log_info(f"Index template '{template_name}' already exists; skip")
        return

    es_request(
        "PUT",
        f"/_index_template/{template_name}",
        json_body=template_body,
        acceptable_status=[200],
    )
    log_success(f"Created index template '{template_name}'")


def create_index(index_name: str, body: dict[str, Any]) -> None:
    """Create index or skip if already exists."""
    # Check if index exists
    resp = es_request("HEAD", f"/{index_name}", acceptable_status=[200, 404])
    # 200: index found, 404: index not found
    if resp.status_code == 200:
        log_info(f"Index '{index_name}' already exists; skip")
        return

    es_request("PUT", f"/{index_name}", json_body=body, acceptable_status=[200, 400])
    if resp.status_code == 400:
        # Alias already exists
        log_warning(resp.json())
    else:
        log_success(f"Created index '{index_name}'")


def main() -> None:
    """Main function for Elasticsearch initialization."""
    try:
        log_info("Elasticsearch init started")

        wait_for_elasticsearch()
        create_ilm_policies(MAPPINGS_DIR)
        create_indices(MAPPINGS_DIR)

        log_success("Elasticsearch init completed")
    except Exception:
        log_error("Elasticsearch init failed")
        raise


if __name__ == "__main__":
    main()
