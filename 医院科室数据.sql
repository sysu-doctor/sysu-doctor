
-- 插入三家医院数据
INSERT INTO hospital (name) VALUES ('中山大学附属第一医院'), ('中山大学孙逸仙纪念医院'), ('北京协和医院');

-- 插入科室数据（每家医院5个科室）
-- 中山大学附属第一医院的科室
INSERT INTO department (name, hospital_id, description) VALUES
('心血管内科', (SELECT id FROM hospital WHERE name = '中山大学附属第一医院'), '治疗心脏和血管疾病'),
('神经外科', (SELECT id FROM hospital WHERE name = '中山大学附属第一医院'), '治疗神经系统疾病'),
('消化内科', (SELECT id FROM hospital WHERE name = '中山大学附属第一医院'), '治疗消化系统疾病'),
('呼吸内科', (SELECT id FROM hospital WHERE name = '中山大学附属第一医院'), '治疗呼吸系统疾病'),
('骨科', (SELECT id FROM hospital WHERE name = '中山大学附属第一医院'), '治疗骨骼肌肉系统疾病');

-- 中山大学孙逸仙纪念医院的科室
INSERT INTO department (name, hospital_id, description) VALUES
('儿科', (SELECT id FROM hospital WHERE name = '中山大学孙逸仙纪念医院'), '儿童疾病治疗'),
('妇产科', (SELECT id FROM hospital WHERE name = '中山大学孙逸仙纪念医院'), '妇科和产科服务'),
('眼科', (SELECT id FROM hospital WHERE name = '中山大学孙逸仙纪念医院'), '眼部疾病治疗'),
('耳鼻喉科', (SELECT id FROM hospital WHERE name = '中山大学孙逸仙纪念医院'), '耳鼻喉疾病治疗'),
('皮肤科', (SELECT id FROM hospital WHERE name = '中山大学孙逸仙纪念医院'), '皮肤疾病治疗');

-- 北京协和医院的科室
INSERT INTO department (name, hospital_id, description) VALUES
('内分泌科', (SELECT id FROM hospital WHERE name = '北京协和医院'), '内分泌系统疾病治疗'),
('肾内科', (SELECT id FROM hospital WHERE name = '北京协和医院'), '肾脏疾病治疗'),
('血液科', (SELECT id FROM hospital WHERE name = '北京协和医院'), '血液系统疾病治疗'),
('风湿免疫科', (SELECT id FROM hospital WHERE name = '北京协和医院'), '风湿免疫疾病治疗'),
('急诊科', (SELECT id FROM hospital WHERE name = '北京协和医院'), '急诊医疗服务');