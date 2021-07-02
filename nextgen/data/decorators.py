import re


def custom_collection_name(cls):
    """Pluralize MongoDB collection name."""

    def wrap(cls):
        new_collection_name = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower() + "s"

        # It seems like mongoengine has an some issue with settings 'meta.collection' inside child class so modify '_meta' attribute directly.
        getattr(cls, "_meta")["collection"] = new_collection_name
        return cls

    return wrap(cls)
