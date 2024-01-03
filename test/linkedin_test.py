import requests
import os


def get_access_token(client_id, client_secret, redirect_uri, auth_code):
    """Exchange the authorization code for an access token"""
    url = "https://www.linkedin.com/oauth/v2/accessToken"
    payload = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json().get("access_token")


def get_my_posts(access_token):
    """Get your LinkedIn posts"""
    url = "https://api.linkedin.com/v2/posts"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()  # This JSON contains your posts


def get_comments_for_post(access_token, post_id):
    """Get comments for a specific post"""
    url = f"https://api.linkedin.com/v2/posts/{post_id}/comments"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()  # This JSON contains comments for the post


def main():
    # Example usage
    client_id = os.environ["LINKEDIN_CLIENT_ID"]
    client_secret = os.environ["LINKEDIN_CLIENT_SECRET"]
    redirect_uri = ""
    auth_code = ""

    access_token = get_access_token(client_id, client_secret, redirect_uri, auth_code)
    posts = get_my_posts(access_token)

    for post in posts["elements"]:
        post_id = post["id"]
        comments = get_comments_for_post(access_token, post_id)
        print(comments)


if __name__ == "__main__":
    main()
