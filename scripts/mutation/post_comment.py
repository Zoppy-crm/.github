import argparse
import json
import os
import re
import urllib.request

MARKER = '<!-- mutation-check -->'
API = 'https://api.github.com'
NEXT_RE = re.compile(r'<([^>]+)>;\s*rel="next"')


def github(method, url, token, data=None):
    request = urllib.request.Request(
        url,
        method=method,
        data=json.dumps(data).encode() if data is not None else None,
        headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        },
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read() or b'null'), response.headers.get('Link', '')


def next_page(link_header):
    match = NEXT_RE.search(link_header or '')
    return match.group(1) if match else None


def find_existing(repo, number, token):
    url = f'{API}/repos/{repo}/issues/{number}/comments?per_page=100'
    while url:
        comments, link = github('GET', url, token)
        for comment in comments:
            if MARKER in (comment.get('body') or ''):
                return comment
        url = next_page(link)
    return None


def publish(repo, number, token, body):
    if MARKER not in body:
        body = f'{MARKER}\n{body}'
    existing = find_existing(repo, number, token)
    if existing:
        github('PATCH', f'{API}/repos/{repo}/issues/comments/{existing["id"]}', token, {'body': body})
        return 'atualizado', existing['id']
    created, _ = github('POST', f'{API}/repos/{repo}/issues/{number}/comments', token, {'body': body})
    return 'criado', created['id']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    parser.add_argument('--repo', default=os.environ.get('GITHUB_REPOSITORY'))
    parser.add_argument('--pr', default=os.environ.get('PR_NUMBER'))
    args = parser.parse_args()
    if not args.repo or not args.pr:
        parser.error('--repo e --pr (ou GITHUB_REPOSITORY e PR_NUMBER) são obrigatórios')
    with open(args.file) as handle:
        body = handle.read()
    action, comment_id = publish(args.repo, args.pr, os.environ['GITHUB_TOKEN'], body)
    print(f'comentário {action}: {comment_id}')


if __name__ == '__main__':
    main()
