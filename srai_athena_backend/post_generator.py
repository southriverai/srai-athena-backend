from openai import OpenAI
import json

import os


class PostGenerator:
    def __init__(self):
        self.client_openai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def generate(self, dict_post_template: dict) -> dict:
        # dict_post_template_short = {"goal": dict_post_template["goal"]}
        # dict_post_template_short["list_data_source"] = []
        # for data_source in dict_post_template["list_data_source"]:
        #     data_source_short = data_source.copy()
        #     data_source_text = data_source["text"]
        #     system_message = {
        #         "role": "system",
        #         "content": """
        #         You are a asssitent for shortening summaries of articles
        #         """,
        #     }
        #     promt_message = {
        #         "role": "user",
        #         "content": f"Shorten the following summary{data_source_text} to about 500words",
        #     }
        #     list_message = []
        #     list_message.append(system_message)
        #     list_message.append(promt_message)
        #     response = self.client_openai.chat.completions.create(
        #         model="gpt-3.5-turbo-16k",
        #         messages=list_message,
        #         temperature=1,
        #     )
        #     data_source_short_text = response.choices[0].message.content

        #     data_source_short["text"] = data_source_short_text

        #     dict_post_template_short["list_data_source"].append(data_source_short)
        #     # TODO

        """
        generate post
        """
        promt = json.dumps(dict_post_template)
        system_message = {
            "role": "system",
            "content": """
            You are a asssitent for writing blog posts for linkedin.
            Post should be about 3 paragraphs long and should be about 500 words.
            Post are based on a json template.
            Post should follow the goal of the template.
            Post should incorperate the datasources in the template.
            """,
        }
        promt_message = {
            "role": "user",
            "content": promt,
        }
        list_message = []
        list_message.append(system_message)
        list_message.append(promt_message)
        response = self.client_openai.chat.completions.create(
            model="gpt-4",
            messages=list_message,
            temperature=1,
        )

        suffix = """
        Generation Code Repo
        https://lnkd.in/eTXDGWxY
        Content repo
        https://lnkd.in/e9ZhJeQZ
        """
        dict_post = {
            "title": "title_0",
            "text generated": response.choices[0].message.content,
            "suffix": suffix,
        }
        return dict_post
