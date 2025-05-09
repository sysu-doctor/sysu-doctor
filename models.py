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