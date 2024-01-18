from github import Github
import os
from github import Auth
from github.Commit import Commit
from github.Repository import Repository
import requests
import json
from bs4 import BeautifulSoup
from srai_athena_backend.post_generator import PostGenerator
from datetime import datetime, timedelta
from openai import OpenAI
from typing import List


def get_commits_within_dates(repository: Repository, start_date, end_date):
    return list(repository.get_commits(since=start_date, until=end_date))


def print_commit_info(list_commit: list[Commit]):
    for commit in list_commit:
        print(f"Commit: {commit.sha}")
        print(f"Author: {commit.author.login if commit.author else 'N/A'}")
        print(f"Date: {commit.commit.author.date}")
        print(f"Message: {commit.commit.message}\n")


def get_changes_from_commits(
    list_commit: List[Commit],
) -> dict:
    list_chanches = []
    for commit in list_commit:
        for file in commit.files:
            list_chanches.append({"file_name": file.filename, "patch": file.patch})

    dict_changes = {}
    dict_changes["list_changes"] = list_chanches
    return dict_changes


def get_changes(diff_url: str):
    html_str = requests.get(diff_url).content.decode("utf8")

    bs = BeautifulSoup(html_str, "html.parser")
    list_div = bs.find_all("div", class_="file")
    dict_changes = {"list_changes": []}
    for file_dif in list_div:
        # print classs
        file_name = (
            file_dif.find_all("div", class_="file-header")[0]
            .find_all("a")[0]
            .get("title")
        )
        list_span = file_dif.find_all("div", class_="data")[0].find_all("span")

        # get inner html
        changes = ""
        for span in list_span:
            changes += span.text + "\n"
        dict_changes["list_changes"].append(
            {"file_name": file_name, "changes": changes}
        )
    return dict_changes


def get_description(dict_changes: dict):
    dict_description = {"list_description": []}

    for change in dict_changes["list_changes"]:
        print(change.keys())
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        promt = """
        Given the following text of a git patch, descrbe in natural language what the change in the code might do. Limit your response to 100 words.
        """
        if change["patch"] is None:
            continue
        promt += change["patch"]
        promt += """
        Do not include any explanations, only provide a RFC8259 compliant JSON response following this format without deviation.
        {
            "list_change": [
                {
                    "description": "title_0"
                }
            ]
        }
        """

        system_message = {
            "role": "system",
            "content": "You are a asssitent for describing changes based on git difs",
        }
        promt_message = {
            "role": "user",
            "content": promt,
        }
        list_message = []
        list_message.append(system_message)
        list_message.append(promt_message)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=list_message,
            temperature=1,
        )
        print(response.choices[0].message)
        dict_description["list_description"].append(
            {
                "file_name": change["file_name"],
                "description": response.choices[0].message.content,
            }
        )
    return dict_description


def main() -> None:
    # using an access token
    auth = Auth.Token(os.environ["GITHUB_TOKEN"])
    date_str = datetime.now().strftime("%Y-%m-%d")
    path_dir_post = os.path.join("..", "srai-athena-content", date_str)
    if not os.path.exists(path_dir_post):
        os.mkdir(path_dir_post)
    path_file_changes = os.path.join(path_dir_post, "changes.json")
    path_file_post_template = os.path.join(path_dir_post, "post_template.json")
    path_file_post = os.path.join(path_dir_post, "post.json")
    # First create a Github instance:
    g = Github(auth=auth)

    # Repositories and date range
    org = g.get_organization("southriverai")
    name_repo = "srai-athena-backend"
    list_repository = []
    list_repository.append(org.get_repo(name_repo))
    for repository in list_repository:
        end_date = datetime.now()
        # one week before
        start_date = end_date - timedelta(days=7)

        # Fetch commits
        list_commit = get_commits_within_dates(
            repository,
            start_date,
            end_date,
        )

        dict_changes = get_changes_from_commits(list_commit)

    # cache_changes
    if os.path.exists(path_file_changes):
        with open(path_file_changes, "r") as f:
            dict_changes = json.load(f)
    else:
        dict_changes = get_changes_from_commits(list_commit)
        with open(path_file_changes, "w") as f:
            json.dump(dict_changes, f)

    # cache change summery
    if os.path.exists(path_file_post_template):
        with open(path_file_post_template, "r") as f:
            post_template = json.load(f)
    else:
        post_template = get_description(dict_changes)
        with open(path_file_post_template, "w") as f:
            json.dump(post_template, f)

    post_template_new = {}
    post_template_new["list_datasource"] = []
    post_template_new[
        "goal"
    ] = """ Given a list of descriptions write a 300 word blog about the code changes that happend this week"""
    for description in post_template["list_description"]:
        post_template_new["list_datasource"].append({"text": description})

    # cache post
    if os.path.exists(path_file_post):
        with open(path_file_post, "r") as f:
            post_template = json.load(f)
    else:
        post = PostGenerator().generate(post_template)
        with open(path_file_post, "w") as f:
            json.dump(post, f)

    print(post)


# main gaurd
if __name__ == "__main__":
    main()
