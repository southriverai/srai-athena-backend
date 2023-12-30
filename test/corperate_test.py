from datetime import datetime

import json
import os
from srai_athena_backend.post_generator import PostGenerator
import requests


def build_dict_post_template(path_file_post_template: str) -> dict:
    """
    build post template
    """
    project_plan_url = "https://raw.githubusercontent.com/southriverai/srai-athena-content/main/project_plan.md"
    project_plan_text = requests.get(project_plan_url).text
    post_template = {
        "goal": "goal_0",
        "list_datasource": [
            {"datasource_type": "document", "content": project_plan_text},
        ],
    }
    return post_template


def main() -> None:
    # get date
    generator = PostGenerator()
    date_str = datetime.now().strftime("%Y%m%d")
    path_file_post_template = "post_template.json"
    path_file_post = "post.json"

    # cache stories
    if not os.path.exists(path_file_post_template):  # hacky cache
        post_template = build_dict_post_template(path_file_post_template)
        with open(path_file_post_template, "w") as f:
            json.dump(post_template, f)
    else:
        with open(path_file_post_template, "r") as f:
            post_template = json.load(f)

    # cache post
    if not os.path.exists(path_file_post):  # hacky cache
        post = generator.generate(post_template)

        with open(path_file_post, "w") as f:
            json.dump(post, f)
    else:
        with open(path_file_post, "r") as f:
            post = json.load(f)


# main gaurd
if __name__ == "__main__":
    main()
