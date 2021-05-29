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
PR_STATES = ['open']
# PR_STATES = ['open', 'closed']


@app.route("/healthz", methods=['GET'])
def healthz():
    return 'OK'


@app.route("/get_repos_list", methods=['GET'])
def get_repos_list():
    content = request.args
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(f'{OWNER}/{REPO}')
    all_prs_object = {}
    for pr_state in PR_STATES:
        pull_requests = repo.get_pulls(state=pr_state)
        print(f'There are {pull_requests.totalCount} {pr_state} pull requests')
        for pr in pull_requests:
            all_prs_object[pr.title] = {}
            pr_head_commit_has = pr.head.sha
            check_runs_url = f"{GITHUB_BASE_URL}/repos/{OWNER}/{REPO}/commits/{pr_head_commit_has}/check-runs"
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}
            r = requests.request(url=check_runs_url, method=GET, headers=headers)
            check_runs = loads(r.content)['check_runs']
            changed_files_url = f"{GITHUB_BASE_URL}/repos/{OWNER}/{REPO}/pulls/{pr.raw_data['number']}/files"
            r = requests.request(url=changed_files_url, method=GET, headers=headers)
            changed_files = loads(r.content)
            for changed_file in changed_files:
                changed_file_filename = [changed_file['filename']]
                if 'changed_filename' in all_prs_object[pr.title]:
                    all_prs_object[pr.title]['changed_filenames'].append(changed_file_filename[0])
                else:
                    all_prs_object[pr.title]['changed_filenames'] = changed_file_filename
            all_prs_object[pr.title]['check_runs'] = check_runs
    print(all_prs_object)
    return Response(json.dumps(all_prs_object), status=200, mimetype='application/json')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8081))
    app.run(debug=True, host='0.0.0.0', use_reloader=True, port=port)
