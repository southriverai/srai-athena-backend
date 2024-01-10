from datetime import datetime

import json
import os
from srai_athena_backend.post_generator import PostGenerator


def build_dict_post_template(path_file_transcript: str) -> dict:
    """
    build post template
    """
    with open(path_file_transcript, "r") as f:
        transcrip_text = f.read()
    goal = """
    Given a transcript write a blog post about the content of the transcript.
    Write the blog in the frist person.
    Be consice and to the point. Dont use flowery language.
    """
    post_template = {
        "goal": goal,
        "list_datasource": [
            {"datasource_type": "transcript", "content": transcrip_text},
        ],
    }
    return post_template


def main() -> None:
    # get date
    generator = PostGenerator()
    date_str = datetime.now().strftime("%Y-%m-%d")
    path_dir_post = os.path.join("..", "srai-athena-content", date_str)
    path_file_transcript = os.path.join(path_dir_post, "transcript.txt")
    path_file_post_template = os.path.join(path_dir_post, "post_template.json")
    path_file_post = os.path.join(path_dir_post, "post.json")

    # cache stories
    if not os.path.exists(path_file_post_template):  # hacky cache
        post_template = build_dict_post_template(path_file_transcript)
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
