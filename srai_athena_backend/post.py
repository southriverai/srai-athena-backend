class PostVersion:
    def __init__(
        self,
        internal_post_id,
        state,
        channel_id,
        version_datetime,
        sceduled_datetime,
        content_dict,
    ):
        self.internal_post_id = internal_post_id
        self.state = state
        self.channel_id = channel_id
        self.version_datetime = version_datetime
        self.scheduled_datetime = sceduled_datetime
        self.content_dict = content_dict

    def to_dict(self):
        return {
            "internal_post_id": self.internal_post_id,
            "state": self.state,
            "channel_id": self.channel_id,
            "version_datetime": self.version_datetime,
            "scheduled_datetime": self.scheduled_datetime,
            "content_dict": self.content_dict,
        }

    @staticmethod
    def from_dict(post_dict):
        return PostVersion(
            post_dict["internal_post_id"],
            post_dict["state"],
            post_dict["channel_id"],
            post_dict["version_datetime"],
            post_dict["scheduled_datetime"],
            post_dict["content_dict"],
        )
