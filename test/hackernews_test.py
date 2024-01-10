from typing import Dict, List
from hackernews import HackerNews
from openai import OpenAI
import os
import json
import requests
from bs4 import BeautifulSoup
from srai_athena_backend.post_generator import PostGenerator


def main() -> None:
    path_dir_post = os.path.join("..", "srai-athena-content", "20240102")
    if not os.path.exists(path_dir_post):
        os.mkdir(path_dir_post)
    path_file_selection = os.path.join(path_dir_post, "selection.json")
    path_file_post_template = os.path.join(path_dir_post, "post_template.json")
    path_file_post = os.path.join(path_dir_post, "post.json")
    hn = HackerNews()

    list_story = hn.top_stories()
    dict_story = {}
    for story in list_story:
        dict_story[story.title] = story.item_id

    # cahce selection
    if not os.path.exists(path_file_selection):  # hacky cache
        list_selected_title = select_title(list(dict_story.keys()))
        with open(path_file_selection, "w") as f:
            json.dump(list_selected_title, f)
    else:
        with open(path_file_selection, "r") as f:
            list_selected_title = json.load(f)

    # cache stories
    if not os.path.exists(path_file_post_template):  # hacky cache
        post_template = build_template(dict_story, list_selected_title)
        with open(path_file_post_template, "w") as f:
            json.dump(post_template, f)
    else:
        with open(path_file_post_template, "r") as f:
            post_template = json.load(f)

    # cache post

    if not os.path.exists(path_file_post):  # hacky cache
        post = PostGenerator().generate(post_template)
        with open(path_file_post, "w") as f:
            json.dump(post, f)
    else:
        with open(path_file_post, "r") as f:
            post = json.load(f)


# promt openai
def select_title(list_title: List[str]) -> dict:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    promt = """
    Given the following list of blog post titles, select the three best ones for a blog on a for a socail media AI company:
    """
    promt += f"{list_title}"
    promt += """
    Do not include any explanations, only provide a RFC8259 compliant JSON response following this format without deviation.
    {
        "list_selection": [
            {
                "title": "title_0"
            }
        ]
    }
    """

    system_message = {
        "role": "system",
        "content": "You are a asssitent for selecting content for blog posts",
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
    return json.loads(response.choices[0].message.content)


def build_template(dict_story: Dict[str, str], list_selected_title: dict) -> dict:
    hn = HackerNews()
    dict_prompt = {}
    dict_prompt[
        "goal"
    ] = """
    Create a blog post that relates to the datasources for a socail media AI company of araound 500 words.
    The company is called South River AI they are developing Athena a social media interaction application.
    The application is designed to help users interact with social media in a more productive way.
    It systhesizes posts from a variety of sources and presents them to the user in a way that is more condusive to productivity.
    """
    dict_prompt["list_data_source"] = []
    for title in list_selected_title["list_selection"]:
        item = hn.get_item(dict_story[title["title"]], expand=True)
        print(item.title)
        print(item.url)
        print(item.text)
        if item.text is None:
            html_text = requests.get(item.url).content.decode("utf8")
            text = extract_text_from_html(html_text)
        else:
            text = item.text
        dict_prompt["list_data_source"].append(
            {"title": item.title, "url": item.url, "text": text}
        )
    return dict_prompt


# parse text
def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator="\n", strip=True)


# main gaurd
if __name__ == "__main__":
    main()
