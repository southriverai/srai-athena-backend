from typing import List


def get_post_plan() -> List[dict]:
    pass


def get_list_post_sceduled() -> List[dict]:
    pass


def generate_post(post_plan: dict) -> dict:
    for data_source in post_plan["list_data_source"]:
        pass
    promt = post_plan["promt"]


def main() -> None:
    list_post_sceduled = get_list_post_sceduled()
    print(list_post_sceduled)


# main gaurd
if __name__ == "__main__":
    main()
