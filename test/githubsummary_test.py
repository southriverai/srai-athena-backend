from github import Github
import os
from github import Auth
from github.Commit import Commit
from github.Repository import Repository
import requests
import json
from bs4 import BeautifulSoup

from openai import OpenAI


def get_commits_within_dates(repository: Repository, start_date, end_date):
    return list(repository.get_commits(since=start_date, until=end_date))


def print_commit_info(list_commit: list[Commit]):
    for commit in list_commit:
        print(f"Commit: {commit.sha}")
        print(f"Author: {commit.author.login if commit.author else 'N/A'}")
        print(f"Date: {commit.commit.author.date}")
        print(f"Message: {commit.commit.message}\n")


def get_diff_between_commits(
    repository: Repository,
    commit_0: Commit,
    commit_1: Commit,
):
    # Get the diff as a string
    diff_url = repository.compare(commit_0.sha, commit_1.sha).diff_url
    print(diff_url)
    return diff_url


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
        print(change)
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        promt = """
        Given the following html of a git diff, descrbe in natural language what the change in the code might do. Limit your response to 100 words.
        """
        promt += change["changes"]
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


def generate_post(dict_description: dict) -> dict:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    dict_description["goal"] = "Write a blog post about the changes in the code base"

    promt = json.dumps(dict_description)

    system_message = {
        "role": "system",
        "content": "You are a asssitent for writing blog posts",
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
    dict_post = {
        "title": "title_0",
        "text generated": response.choices[0].message.content,
    }
    return dict_post


def main() -> None:
    # using an access token
    auth = Auth.Token(os.environ["GITHUB_TOKEN"])

    # First create a Github instance:
    g = Github(auth=auth)

    # Repositories and date range
    org = g.get_organization("southriverai")
    list_repository = []
    list_repository.append(org.get_repo("srai-core"))
    # for repository in list_repository:
    #     # start_date = datetime(2023, 8, 27)
    #     # end_date = datetime(2023, 12, 27)

    #     # # Fetch commits
    #     # list_commit = get_commits_within_dates(repository, start_date, end_date)

    #     # diff = get_diff_between_commits(repository, list_commit[0], list_commit[1])

    # cache_changes
    url = "https://github.com/southriverai/srai-core/diffs?bytes=11102&lines=350&sha1=133dca8c42e6fbca2206acb37b6b638616d77750&sha2=86026afac2d95973167649e9698784646c4951b4&start_entry=14&sticky=false&w=false"
    if os.path.exists("changes.json"):
        with open("changes.json", "r") as f:
            dict_changes = json.load(f)
    else:
        dict_changes = get_changes(url)
        with open("changes.json", "w") as f:
            json.dump(dict_changes, f)

    # cache change summery
    if os.path.exists("description.json"):
        with open("description.json", "r") as f:
            dict_description = json.load(f)
    else:
        dict_description = get_description(dict_changes)
        with open("description.json", "w") as f:
            json.dump(dict_description, f)

    # cache post
    post = generate_post(dict_description)
    print(post)


# main gaurd
if __name__ == "__main__":
    main()
