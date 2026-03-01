#!/usr/bin/env python3
"""
Validates that required fields (Priority, Size, Estimate) are filled
when an issue is closed (auto-close from Done column).

If any field is missing, reopens the issue and posts a comment.
"""

import os
import requests

GQL = "https://api.github.com/graphql"
REST = "https://api.github.com"
TOKEN = os.environ["GH_TOKEN"]
H_GQL = {"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"}
H_REST = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

PROJECT_NUMBER = 7
ORG = "Zoppy-crm"

REQUIRED_FIELDS = {"Priority", "Size", "Estimate"}


def graphql(query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    r = requests.post(GQL, headers=H_GQL, json=payload)
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        print(f"GraphQL errors: {data['errors']}")
    return data


def get_project_item_fields(issue_node_id):
    """Find the issue in the org project and return its field values."""
    query = """query($issueId: ID!) {
      node(id: $issueId) {
        ... on Issue {
          projectItems(first: 10) {
            nodes {
              id
              project { number }
              fieldValues(first: 30) {
                nodes {
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    field { ... on ProjectV2SingleSelectField { name } }
                    name
                  }
                  ... on ProjectV2ItemFieldNumberValue {
                    field { ... on ProjectV2Field { name } }
                    number
                  }
                }
              }
            }
          }
        }
      }
    }"""
    return graphql(query, {"issueId": issue_node_id})


def reopen_issue(repo, issue_number):
    requests.patch(
        f"{REST}/repos/{repo}/issues/{issue_number}",
        headers=H_REST,
        json={"state": "open"},
    )


def post_comment(repo, issue_number, missing_fields):
    fields_list = ", ".join(f"**{f}**" for f in missing_fields)
    body = (
        f":warning: Esta issue foi reaberta automaticamente porque os seguintes "
        f"campos obrigatorios nao estao preenchidos no projeto: {fields_list}.\n\n"
        f"Por favor, preencha {fields_list} no card do projeto antes de mover para **Done**."
    )
    requests.post(
        f"{REST}/repos/{repo}/issues/{issue_number}/comments",
        headers=H_REST,
        json={"body": body},
    )


def main():
    issue_node_id = os.environ.get("ISSUE_NODE_ID")
    issue_number = os.environ.get("ISSUE_NUMBER")
    repo = os.environ.get("ISSUE_REPO")

    if not all([issue_node_id, issue_number, repo]):
        print("Missing environment variables, skipping.")
        return

    issue_number = int(issue_number)
    print(f"Validating {repo}#{issue_number}...")

    result = get_project_item_fields(issue_node_id)
    node = result.get("data", {}).get("node", {})
    project_items = node.get("projectItems", {}).get("nodes", [])

    target_item = None
    for item in project_items:
        if item.get("project", {}).get("number") == PROJECT_NUMBER:
            target_item = item
            break

    if not target_item:
        print(f"Issue not found in project #{PROJECT_NUMBER}, skipping validation.")
        return

    filled = set()
    for fv in target_item.get("fieldValues", {}).get("nodes", []):
        field = fv.get("field", {})
        field_name = field.get("name", "")
        if field_name in REQUIRED_FIELDS:
            has_value = fv.get("name") is not None or fv.get("number") is not None
            if has_value:
                filled.add(field_name)

    missing = REQUIRED_FIELDS - filled

    if not missing:
        print("All required fields are filled. Issue stays closed.")
        return

    missing_sorted = sorted(missing)
    print(f"Missing fields: {missing_sorted}. Reopening issue...")

    reopen_issue(repo, issue_number)
    print("Issue reopened.")

    post_comment(repo, issue_number, missing_sorted)
    print("Comment posted.")


if __name__ == "__main__":
    main()
