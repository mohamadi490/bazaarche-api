import re

class utils:
    def is_email(self, username: str):
        checking = re.search(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', username)
        return checking is not None
    

    def is_phone_number(self, username: str):
        checking = re.search(r'(98|0|98|0098)?([ ]|-|[()]){0,2}9[0-9]([ ]|-|[()]){0,2}(?:[0-9]([ ]|-|[()]){0,2}){8}', username)
        return checking is not None
    
    def get_username_type(self, username: str):
        return 'email' if self.is_email(username) else 'phone_number' if self.is_phone_number(username) else None

utils = utils()