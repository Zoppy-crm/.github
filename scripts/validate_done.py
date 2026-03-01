#!/usr/bin/env python3
"""
Validates that required fields (Priority, Size, Estimate) are filled
before allowing an issue to move to Done in GitHub Projects.

If any field is missing, reverts the card to its previous status
and posts a comment on the issue explaining why.
"""

import os
import json
import requests

GQL = "https://api.github.com/graphql"
REST = "https://api.github.com"
TOKEN = os.environ["GH_TOKEN"]
H_GQL = {"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"}
H_REST = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

PROJECT_ID = "PVT_kwDOCAubUc4BQdrV"
STATUS_FIELD_ID = "PVTSSF_lADOCAubUc4BQdrVzg-k0-w"
DONE_OPTION_ID = "98236657"
TODO_OPTION_ID = "61e4505c"

REQUIRED_FIELDS = {
    "PVTSSF_lADOCAubUc4BQdrVzg-k1Ns": "Priority",
    "PVTSSF_lADOCAubUc4BQdrVzg-k1Nw": "Size",
    "PVTF_lADOCAubUc4BQdrVzg-k1N0": "Estimate",
}


def graphql(query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    r = requests.post(GQL, headers=H_GQL, json=payload)
    r.raise_for_status()
    return r.json()


def get_item_fields(item_node_id):
    query = """query($itemId: ID!) {
      node(id: $itemId) {
        ... on ProjectV2Item {
          id
          content {
            ... on Issue {
              number
              title
              repository { nameWithOwner }
            }
          }
          fieldValues(first: 30) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                field { ... on ProjectV2SingleSelectField { id name } }
                optionId
                name
              }
              ... on ProjectV2ItemFieldNumberValue {
                field { ... on ProjectV2Field { id name } }
                number
              }
            }
          }
        }
      }
    }"""
    return graphql(query, {"itemId": item_node_id})


def revert_status(item_node_id, option_id):
    mutation = """mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $projectId,
        itemId: $itemId,
        fieldId: $fieldId,
        value: { singleSelectOptionId: $optionId }
      }) { projectV2Item { id } }
    }"""
    graphql(mutation, {
        "projectId": PROJECT_ID,
        "itemId": item_node_id,
        "fieldId": STATUS_FIELD_ID,
        "optionId": option_id,
    })


def post_comment(repo, issue_number, missing_fields):
    fields_list = ", ".join(f"**{f}**" for f in missing_fields)
    body = (
        f":warning: Este card foi movido de volta porque os seguintes campos "
        f"obrigatorios nao estao preenchidos: {fields_list}.\n\n"
        f"Por favor, preencha {fields_list} antes de mover para **Done**."
    )
    requests.post(
        f"{REST}/repos/{repo}/issues/{issue_number}/comments",
        headers=H_REST,
        json={"body": body},
    )


def main():
    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    if not event_path:
        print("No GITHUB_EVENT_PATH, skipping.")
        return

    with open(event_path) as f:
        event = json.load(f)

    changes = event.get("changes", {}).get("field_value", {})
    item = event.get("projects_v2_item", {})
    item_node_id = item.get("node_id")

    if not item_node_id:
        print("No item node_id found, skipping.")
        return

    changed_field_id = changes.get("field_node_id")
    if changed_field_id != STATUS_FIELD_ID:
        print("Changed field is not Status, skipping.")
        return

    result = get_item_fields(item_node_id)
    node = result.get("data", {}).get("node", {})
    if not node:
        print("Could not fetch item details, skipping.")
        return

    field_values = node.get("fieldValues", {}).get("nodes", [])

    current_status_option = None
    filled_fields = set()
    for fv in field_values:
        field = fv.get("field", {})
        field_id = field.get("id", "")

        if field_id == STATUS_FIELD_ID:
            current_status_option = fv.get("optionId")

        if field_id in REQUIRED_FIELDS:
            if fv.get("optionId") or fv.get("number") is not None:
                filled_fields.add(field_id)

    if current_status_option != DONE_OPTION_ID:
        print(f"Item is not in Done (option: {current_status_option}), skipping.")
        return

    missing = [REQUIRED_FIELDS[fid] for fid in REQUIRED_FIELDS if fid not in filled_fields]

    if not missing:
        print("All required fields are filled. Card can stay in Done.")
        return

    print(f"Missing fields: {missing}. Reverting card...")

    previous_option = None
    from_val = changes.get("from")
    if isinstance(from_val, dict):
        previous_option = from_val.get("id")
    elif isinstance(from_val, str):
        previous_option = from_val

    if not previous_option:
        print("Could not determine previous status, falling back to 'To Do'.")
        previous_option = TODO_OPTION_ID

    revert_status(item_node_id, previous_option)
    print("Card reverted to previous status.")

    content = node.get("content", {})
    repo = content.get("repository", {}).get("nameWithOwner")
    issue_number = content.get("number")

    if repo and issue_number:
        post_comment(repo, issue_number, missing)
        print(f"Comment posted on {repo}#{issue_number}.")
    else:
        print("Could not find issue to comment on.")


if __name__ == "__main__":
    main()
