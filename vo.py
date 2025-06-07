# view object

class LoginVO:
    def __init__(self, id, name, role, token, avatar_url):
        self.id = id
        self.name = name
        self.role = role
        self.token = token
        self.avatar_url = avatar_url
    def to_dict(self):
        return {"id": self.id, "name": self.name, "role": self.role, "avatar_url": self.avatar_url, "token": self.token}

class PatientInfoVO:
    def __init__(self, phone, name, gender, address, birth_date, avatar_url, medical_history):
        self.phone = phone
        self.name = name
        self.gender = gender
        self.address = address
        self.avatar_url = avatar_url
        self.birth_date = birth_date
        self.medical_history = medical_history
    def to_dict(self):
        return {"phone": self.phone,
                "name": self.name,
                "gender": self.gender,
                "address": self.address,
                "avatar_url": self.avatar_url,
                "birth_date": self.birth_date,
                "medical_history": self.medical_history}

class DoctorInfoVO:
    def __init__(self, phone, name, gender, hospital, department, internal_id,position_rank, specialty, birth_date, avatar_url):
        self.phone = phone
        self.name = name
        self.gender = gender
        self.hospital = hospital
        self.internal_id = internal_id
        self.department = department
        self.position_rank = position_rank
        self.specialty = specialty
        self.birth_date = birth_date
        self.avatar_url = avatar_url
    def to_dict(self):
        return {"phone": self.phone,
                "name": self.name,
                "gender": self.gender,
                "hospital_id": self.hospital,
                "department_id": self.department,
                "internal_id": self.internal_id,
                "position_rank": self.position_rank,
                "specialty": self.specialty,
                "birth_date": self.birth_date,
                "avatar_url": self.avatar_url}