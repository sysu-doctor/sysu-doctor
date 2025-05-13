-- 第一步：禁用外键检查（避免约束冲突）
SET FOREIGN_KEY_CHECKS = 0;

-- 第二步：清空表数据（保留表结构）
TRUNCATE TABLE department;
TRUNCATE TABLE hospital;

-- 第三步：重新启用外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- 第四步：插入医院数据（使用INSERT IGNORE避免潜在冲突）
INSERT IGNORE INTO hospital (name) VALUES
('中山大学附属第一医院'),
('中山大学孙逸仙纪念医院'),
('北京协和医院');

-- 第五步：插入科室数据（使用变量提高可读性）
SET @hospital1 = (SELECT id FROM hospital WHERE name = '中山大学附属第一医院');
SET @hospital2 = (SELECT id FROM hospital WHERE name = '中山大学孙逸仙纪念医院');
SET @hospital3 = (SELECT id FROM hospital WHERE name = '北京协和医院');

-- 中山大学附属第一医院的科室
INSERT INTO department (name, hospital_id, description) VALUES
('心血管内科', @hospital1, '治疗心脏和血管疾病'),
('神经外科', @hospital1, '治疗神经系统疾病'),
('消化内科', @hospital1, '治疗消化系统疾病'),
('呼吸内科', @hospital1, '治疗呼吸系统疾病'),
('骨科', @hospital1, '治疗骨骼肌肉系统疾病');

-- 中山大学孙逸仙纪念医院的科室
INSERT INTO department (name, hospital_id, description) VALUES
('儿科', @hospital2, '儿童疾病治疗'),
('妇产科', @hospital2, '妇科和产科服务'),
('眼科', @hospital2, '眼部疾病治疗'),
('耳鼻喉科', @hospital2, '耳鼻喉疾病治疗'),
('皮肤科', @hospital2, '皮肤疾病治疗');

-- 北京协和医院的科室
INSERT INTO department (name, hospital_id, description) VALUES
('内分泌科', @hospital3, '内分泌系统疾病治疗'),
('肾内科', @hospital3, '肾脏疾病治疗'),
('血液科', @hospital3, '血液系统疾病治疗'),
('风湿免疫科', @hospital3, '风湿免疫疾病治疗'),
('呼吸内科', @hospital3, '治疗呼吸系统疾病');

-- 第六步：验证数据
SELECT h.name AS hospital, COUNT(d.id) AS department_count
FROM hospital h
LEFT JOIN department d ON h.id = d.hospital_id
GROUP BY h.name;