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


def get_me(access_token):
    """Get your LinkedIn posts"""
    url = "https://api.linkedin.com/v2/me"

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(
            response.status_code,
            response.text,
        )
    return response.json()  # This JSON contains your posts


def get_id(access_token):
    """Get your LinkedIn posts"""
    # url = "https://api.linkedin.com/v2/posts"
    url = "https://api.linkedin.com/v2/userinfo"
    author = "urn:li:person:4497731a"
    author = "urn:li:company:2414183"
    body = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": "Hello World! This is my first Share on LinkedIn!"
                },
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers, json=body)
    if response.status_code != 200:
        raise Exception(
            response.status_code,
            response.text,
        )
    return response.json()  # This JSON contains your posts


def get_my_posts(access_token):
    """Get your LinkedIn posts"""
    # url = "https://api.linkedin.com/v2/posts"
    url = "https://api.linkedin.com/v2/ugcPosts"
    author = "urn:li:person:4497731a"
    author = "urn:li:company:2414183"
    body = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": "Hello World! This is my first Share on LinkedIn!"
                },
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(url, headers=headers, json=body)
    if response.status_code != 200:
        raise Exception(
            response.status_code,
            response.text,
        )
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
    redirect_uri = "https://www.linkedin.com/developers/tools/oauth/redirect"
    access_token = os.environ["LINKEDIN_TOKEN"]

    # access_token = get_access_token(client_id, client_secret, redirect_uri, auth_code)
    print(access_token)
    # me = get_me(access_token)
    userinfo = get_id(access_token)
    posts = get_my_posts(access_token)

    for post in posts["elements"]:
        post_id = post["id"]
        comments = get_comments_for_post(access_token, post_id)
        print(comments)


if __name__ == "__main__":
    main()
