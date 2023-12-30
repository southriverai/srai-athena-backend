from ayrshare import SocialPost
social = SocialPost('JZ0GK1Y-D74MAEM-MXZS85W-Q4HW669') # get an API Key at ayrshare.com

# Post to Platforms Twitter, Facebook, and LinkedIn
postResult = social.post({'post': 'Nice Posting 2', 'platforms': ['linkedin']})
print(postResult)

# Delete
deleteResult = social.delete({'id': postResult['id']})
print(deleteResult)

# History
print(social.history())