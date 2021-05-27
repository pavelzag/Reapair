import json
import os
from json import loads, dumps
from flask import Flask, Response, request
from github import Github

import requests

app = Flask(__name__)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GET = "GET"
POST = "POST"
PUT = "PUT"
GITHUB_BASE_URL = "https://api.github.com"
OWNER = "pytest-dev"
REPO = "pytest"


@app.route("/get_repos_list", methods=['GET'])
def get_repos_list():
    content = request.args
    pr_state = content['state']
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(f'{OWNER}/{REPO}')
    pull_requests = repo.get_pulls(state=pr_state)
    print(f'There are {pull_requests.totalCount} {pr_state} pull requests')
    all_test_runs = []
    for pr in pull_requests:
        print(pr)
        pr_head_commit_has = pr.head.sha
        check_runs_url = f"{GITHUB_BASE_URL}/repos/{OWNER}/{REPO}/commits/{pr_head_commit_has}/check-runs"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r = requests.request(url=check_runs_url, method=GET, headers=headers)
        check_runs = loads(r.content)['check_runs']
        all_test_runs.append(check_runs)
    print(all_test_runs)
    return Response(json.dumps(all_test_runs), status=200, mimetype='application/json')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8081))
    app.run(debug=True, host='0.0.0.0', use_reloader=True, port=port)
