# view object

class LoginVO:
    def __init__(self, id, name, role, token):
        self.id = id
        self.name = name
        self.role = role
        self.token = token
    def to_dict(self):
        return {"id": self.id, "name": self.name, "role": self.role, "token": self.token}