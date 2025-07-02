from datetime import datetime

from exts import db

class PatientModel(db.Model):
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(11), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    update_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

class DoctorModel(db.Model):
    __tablename__ = 'doctor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(11), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    update_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

# 患者信息表
class PatientInfoModel(db.Model):
    __tablename__ = 'patient_info'
    id = db.Column(db.Integer, db.ForeignKey('patient.id'), primary_key=True)
    phone = db.Column(db.String(11), nullable=False,unique=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.Enum('male', 'female'), nullable=True)
    # 家庭地址
    address = db.Column(db.String(255),nullable=True)
    # 头像
    avatar_url = db.Column(db.String(255),nullable=True)
    # 出生日期
    birth_date = db.Column(db.Date,nullable=True)
    # 既往病史
    medical_history = db.Column(db.Text,nullable=True)

# 医生信息表
class DoctorInfoModel(db.Model):
    __tablename__ = 'doctor_info'
    id = db.Column(db.Integer, db.ForeignKey('doctor.id'),primary_key=True)

    phone = db.Column(db.String(11), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.Enum('male', 'female'), nullable=True)

    # 医生属于医院，关联医院表
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=True)
    hospital = db.relationship('HospitalModel', backref='doctors')
    # 院内工号（同一医院内唯一）
    internal_id = db.Column(db.String(8), nullable=True)
    __table_args__ = (
        db.UniqueConstraint('hospital_id', 'internal_id', name='uix_hospital_employee'),
    )

    # 医生属于科室，关联科室表
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))

    # 职称等级
    position_rank = db.Column(db.Enum(
        'resident',  # 住院医师
        'attending',  # 主治医师
        'associate_chief',  # 副主任医师
        'chief'  # 主任医师
    ), nullable=True)
    # 擅长方向
    specialty = db.Column(db.Text)
    # 出生日期
    birth_date = db.Column(db.Date)  # 存储"YYYY-MM-DD"格式
    # 头像
    avatar_url = db.Column(db.String(255))
    # 出诊时间安排，一般医生周一到周五至少出诊两天
    schedule = db.Column(db.JSON, nullable=True, default=lambda: {
        "monday": {"morning": False, "afternoon": False},
        "tuesday": {"morning": False, "afternoon": False},
        "wednesday": {"morning": False, "afternoon": False},
        "thursday": {"morning": False, "afternoon": False},
        "friday": {"morning": False, "afternoon": False}
    })

    def to_dict(self):
        return {
            "id": self.id,
            "phone": self.phone,
            "name": self.name,
            "gender": self.gender,
            "hospital_id": self.hospital_id,
            "hospital_name": self.hospital.name if self.hospital else None,
            "department_id": self.department_id,
            "department_name": self.department.name if self.department else None,
            "position_rank": self.position_rank,
            "specialty": self.specialty,
            "avatar_url": self.avatar_url,
            "schedule": self.schedule,
        }


# 科室表
class DepartmentModel(db.Model):
    __tablename__ = 'department'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    # 科室所属医院
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=True)
    # 科室的医生集合
    doctors = db.relationship('DoctorInfoModel', backref='department', lazy='dynamic')
    # 同一医院内科室名称唯一
    __table_args__ = (
        db.UniqueConstraint('hospital_id', 'name', name='uix_hospital_department'),
    )

# 医院表
class HospitalModel(db.Model):
    __tablename__ = 'hospital'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    # 医院的科室集合
    departments = db.relationship('DepartmentModel', backref='hospital', lazy='dynamic')

class MessageModel(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    from_user = db.Column(db.String(50), nullable=False)
    from_user_avatar = db.Column(db.String(255), nullable=True)
    to_user = db.Column(db.String(50), nullable=False)
    to_user_avatar = db.Column(db.String(255), nullable=True)
    content = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    read = db.Column(db.Integer, nullable=False, default=False)
    type = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "from_user": self.from_user,
            "from_user_avatar": self.from_user_avatar,
            "to_user": self.to_user,
            "to_user_avatar": self.to_user_avatar,
            "content": self.content,
            "time": self.time.isoformat(),  # 时间转字符串
            "read": bool(self.read),  # 布尔值转换
            "type": self.type
        }

class RoomModel(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    doctor = db.relationship('DoctorModel', backref='rooms')

    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    patient = db.relationship('PatientModel', backref='rooms')


    def to_dict(self):
        return {
            "doctor_id": self.doctor_id,
            "doctor_name": self.doctor_name,
            "patient_id": self.patient_id,
            "patient_name": self.patient_name
        }

class RegistrationModel(db.Model):
    __tablename__ = 'registration'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_info.id'), nullable=False)
    patient = db.relationship('PatientInfoModel', backref='registrations')

    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_info.id'), nullable=False)
    doctor = db.relationship('DoctorInfoModel', backref='registrations')

    date = db.Column(db.Date, nullable=False, default=datetime.now)
    time_slot = db.Column(db.String(50), nullable=False)  # 时间段，例如 "morning", "afternoon"

    def to_dict(self):
        return {
            "id": self.id,
            "patient": self.patient.name,
            "phone": self.patient.phone,
            "doctor": self.doctor.name,
            "hospital": self.doctor.hospital.name if self.doctor.hospital else None,
            "department": self.doctor.department.name if self.doctor.department else None,
            "date": self.date.isoformat(),
            "time_slot": self.time_slot
        }