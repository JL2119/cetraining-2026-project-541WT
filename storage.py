"""
学生成绩管理系统 — 数据存储模块
负责 JSON 文件的读写以及 CSV 报表导出。

学习要点：
  - json.dump() / json.load()：Python 对象 ↔ JSON 文件
  - csv.writer：写入 CSV 文件，Excel 可直接打开
  - utf-8-sig 编码：带 BOM 的 UTF-8，确保 Excel 打开不乱码
  - os.makedirs(exist_ok=True)：目录不存在就创建，存在也不报错
"""

import json
import csv
import os
from typing import List
from models import Student


# ==================== 工具函数 ====================

def get_data_dir() -> str:
    """
    获取 data 目录的绝对路径。

    为什么要用绝对路径？
      如果用户在别的目录运行程序（如 cd C:\ 然后 python main.py），
      相对路径 "data/" 就找不到了。用 __file__ 获取本文件路径再推算，永远正确。

    __file__ 是当前文件的路径（storage.py）
    os.path.abspath() 转为绝对路径
    os.path.dirname() 取其所在目录（即 grades_system/）
    os.path.join() 拼接出 grades_system/data/
    """
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


# ==================== JSON 读写 ====================

def save_data(students: List[Student], filename: str = "students.json") -> str:
    """
    将所有学生数据保存到 JSON 文件。

    流程：
      1. 确保 data/ 目录存在（不存在就创建）
      2. 把每个 Student 对象转为字典（to_dict）
      3. 用 json.dump() 写入文件

    Args:
        students: 学生对象列表
        filename: 文件名，默认 "students.json"

    Returns:
        保存的文件完整路径（方便打印告知用户）

    关键参数：
        ensure_ascii=False — 不转义中文，否则 "张三" 变成 "张三"
        indent=2 — 缩进 2 格，JSON 文件内容整齐可读
    """
    data_dir = get_data_dir()
    os.makedirs(data_dir, exist_ok=True)  # exist_ok=True: 目录已存在不报错
    filepath = os.path.join(data_dir, filename)

    # 列表推导式：把每个 Student 对象变成字典
    data = [s.to_dict() for s in students]

    # 写入 JSON
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filepath


def load_data(filename: str = "students.json") -> List[Student]:
    """
    从 JSON 文件加载学生数据。

    流程：
      1. 检查文件是否存在（不存在就返回空列表，首次运行不报错）
      2. 用 json.load() 读取文件 → 得到字典列表
      3. 把每个字典还原为 Student 对象（from_dict）

    Args:
        filename: 文件名，默认 "students.json"

    Returns:
        Student 对象列表，文件不存在时返回空列表 []
    """
    filepath = os.path.join(get_data_dir(), filename)

    # 文件不存在的处理：首次运行还没有保存过数据，返回空列表
    if not os.path.exists(filepath):
        return []

    # 读取 JSON 文件
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)  # data 是字典列表: [{"student_id": "001", ...}, ...]

    # 列表推导式：每个字典还原为 Student 对象
    return [Student.from_dict(item) for item in data]


# ==================== CSV 导出 ====================

def export_csv(students: List[Student], filename: str = "grades_report.csv") -> str:
    """
    将所有学生成绩导出为 CSV 文件（Excel 可直接双击打开）。

    流程：
      1. 收集所有出现过的科目名（因为不同学生选的课可能不同）
      2. 构建表头：学号、姓名、班级、平均分、是否全部及格 + 各科目
      3. 逐行写入学生数据

    CSV 格式示例：
      学号,姓名,班级,平均分,是否全部及格,数学,英语,语文
      001,张三,一班,88.5,是,85,92,
      002,李四,二班,72.0,否,58,,73

    编码说明：
      utf-8-sig 比 utf-8 多一个 BOM（字节顺序标记），
      这样 Excel 打开时能自动识别 UTF-8，中文不会乱码。

    newline=""：
      防止 Windows 上 csv.writer 每行之间多一个空行。
    """
    data_dir = get_data_dir()
    os.makedirs(data_dir, exist_ok=True)
    filepath = os.path.join(data_dir, filename)

    # 第一步：收集所有出现过的科目名称（用 set 去重）
    all_subjects = set()
    for s in students:
        all_subjects.update(s.grades.keys())  # set.update() 批量添加
    subjects = sorted(all_subjects)  # 排序，让列顺序固定

    # 第二步：构建表头
    # 基础列 + 各科名列
    headers = ["学号", "姓名", "班级", "平均分", "是否全部及格"] + subjects

    # 第三步：写入 CSV
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)  # 写表头行

        # 逐行写入每个学生的数据
        for s in students:
            avg = s.get_average()
            passing = "是" if s.is_passing() else "否"

            # 基础数据
            row = [s.student_id, s.name, s.class_name, f"{avg:.1f}", passing]

            # 各科成绩：用 .get(subj, "") 取分数，没这科的留空
            for subj in subjects:
                row.append(s.grades.get(subj, ""))

            writer.writerow(row)

    return filepath