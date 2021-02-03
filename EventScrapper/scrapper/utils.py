class ExtractEventManager(object):
    """
    Action event manager
    """

    def __init__(self, class_instance):
        self.class_instance = class_instance

    def __enter__(self):
        return self.class_instance

    def __exit__(self, *exc):
        self.class_instance.send_messages()
        self.class_instance.get_result()
        self.class_instance.log_response()


def run_extractor(class_instance, entry_function="run"):
    with ExtractEventManager(class_instance=class_instance):
        action = getattr(class_instance, entry_function)
        action()
    return class_instance


def build_request_response(status_code, status_details=None):
    """
    Build a response for a validation request.
    Arguments:
        status_code(int).
        status_lookup(dict): k-v pairs of code and description. 
        status_details(string): Optional details to add.
    Returns:
        dictionary.
    """
    response = {"status_code": status_code, "status_details": status_details}
    return response