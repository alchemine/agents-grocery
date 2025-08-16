"""Clean Elasticsearch indices, templates, and policies."""

from pathlib import Path

from config import CFG, ROOT_DIR
from src.common.loader import load_yaml
from src.common.logger import log_info, log_warning, log_error, log_success
from src.initialize import es_request, wait_for_elasticsearch


MAPPINGS_DIR = ROOT_DIR / "mappings"


def delete_ilm_policy(policy_name: str) -> None:
    """Delete ILM policy or skip if not found."""
    try:
        response = es_request(
            "DELETE", f"/_ilm/policy/{policy_name}", acceptable_status=[200, 400, 404]
        )

        if response.status_code == 400:
            # NOTE: policy is in use by one or more indices
            log_warning(response.json(), dump=True)
        elif response.status_code == 404:
            # NOTE: Lifecycle policy not found
            log_info(f"Lifecycle policy not found: {policy_name}")
        else:
            log_success(f"Deleted ILM policy '{policy_name}'")
    except Exception:
        log_error(f"Failed to delete ILM policy '{policy_name}'")


def clean_ilm_policies(root: Path) -> None:
    """Clean ILM policies from directory."""
    try:
        ilm_policies = load_yaml(root / "ilm_policy.yaml")
        for policy_name in ilm_policies:
            delete_ilm_policy(policy_name)
    except Exception:
        log_error("Failed to clean ILM policies")
        raise


def clean_indices(root: Path) -> None:
    """Clean indices from directory."""
    for path in root.glob("index/*.yaml"):
        if Path(path).stem.endswith("template"):
            for dataset in CFG.elasticsearch.dataset:
                config = load_yaml(path, dataset=dataset)
                delete_index_with_template(config)
        else:
            config = load_yaml(path)
            delete_index_with_template(config)


def delete_index_with_template(config: dict) -> None:
    """Delete index with template."""
    delete_index_with_patterns(config.index_template.body.index_patterns)
    delete_index_template(config.index_template.name)


def delete_index_with_patterns(index_patterns: list[str]) -> None:
    """Clean index, template, and alias from config."""
    for pattern in index_patterns:
        for idx in list_indices_by_pattern(pattern):
            delete_index(idx)


def list_indices_by_pattern(pattern: str) -> list[str]:
    """list indices matching the given pattern."""
    resp = es_request(
        "GET", f"/_cat/indices/{pattern}?format=json", acceptable_status=[200, 404]
    )
    if resp.status_code == 404:
        return []
    try:
        items = resp.json()
        return [item.get("index") for item in items if item.get("index")]
    except Exception:
        return []


def delete_index(index_name: str) -> None:
    """Delete index or skip if not found."""
    resp = es_request("DELETE", f"/{index_name}", acceptable_status=[200, 202, 404])
    if resp.status_code in (200, 202):
        log_success(f"Deleted index '{index_name}'")
    else:
        log_info(f"Index '{index_name}' not found; skip")


def delete_index_template(template_name: str) -> None:
    """Delete index template or skip if not found."""
    resp = es_request(
        "DELETE", f"/_index_template/{template_name}", acceptable_status=[200, 404]
    )
    if resp.status_code == 200:
        log_success(f"Deleted index template '{template_name}'")
    else:
        log_info(f"Index template '{template_name}' not found; skip")


def main() -> None:
    """Main function for Elasticsearch cleanup."""
    try:
        log_info("Elasticsearch clean started")

        wait_for_elasticsearch()
        clean_indices(MAPPINGS_DIR)
        clean_ilm_policies(MAPPINGS_DIR)

        log_success("Elasticsearch clean completed")
    except Exception:
        log_error("Elasticsearch clean failed")
        raise


if __name__ == "__main__":
    main()
