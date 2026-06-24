"""
学生成绩管理系统 — 业务逻辑模块
包含学生和成绩的增删改查，以及各类统计分析功能。

学习要点：
  - CRUD 模式：Create（增）/ Read（查）/ Update（改）/ Delete（删）
  - list 操作：遍历、过滤、排序、删除
  - 异常处理：raise ValueError 向调用方报告错误
  - 列表推导式：简洁高效的数据转换写法
  - lambda 表达式：匿名函数，用于 sort 的排序键
  - set（集合）：自动去重，用于收集所有科目名
"""

from typing import List, Optional, Tuple
from models import Student


# ==================== 基础 CRUD 操作 ====================
# CRUD = Create(增) + Read(查) + Update(改) + Delete(删)
# 这是任何数据管理系统的四个基本操作


def add_student(students: List[Student], student_id: str,
                name: str, class_name: str) -> Student:
    """
    添加一个新学生到列表中。

    流程：
      1. 校验输入（学号和姓名不能为空）
      2. 检查学号是否重复（学号必须唯一）
      3. 创建 Student 对象并添加到列表

    Args:
        students: 学生列表（传引用，直接修改，不需要返回）
        student_id: 学号
        name: 姓名
        class_name: 班级

    Returns:
        新创建的 Student 对象

    Raises:
        ValueError: 学号为空、姓名为空、或学号已存在
    """
    # strip() 去除首尾空格，防止用户不小心打了空格
    if not student_id.strip():
        raise ValueError("学号不能为空！")
    if not name.strip():
        raise ValueError("姓名不能为空！")

    # any() 函数：只要有一个满足条件就返回 True
    # 这里遍历所有学生，检查学号是否已被使用
    # 这是 O(n) 的线性查找，对于小规模数据足够快
    if any(s.student_id == student_id for s in students):
        raise ValueError(f"学号 '{student_id}' 已存在，请使用其他学号！")

    # 创建 Student 对象
    student = Student(student_id=student_id, name=name, class_name=class_name)
    # 添加到列表末尾
    students.append(student)
    return student


def delete_student(students: List[Student], student_id: str) -> Student:
    """
    删除指定学号的学生。

    流程：
      1. 遍历列表找到目标学生
      2. 用 pop(i) 按索引删除并返回被删除的对象

    为什么用 pop(i) 而不是 remove()？
      remove() 需要传入对象本身，而 pop(i) 只需要索引。
      我们先找到索引，然后直接 pop，更精确可控。

    Raises:
        ValueError: 找不到该学生
    """
    # enumerate() 同时获取索引 i 和元素 s
    for i, s in enumerate(students):
        if s.student_id == student_id:
            # pop(i) 删除索引 i 处的元素，并返回被删除的元素
            removed = students.pop(i)
            return removed

    # 循环结束都没找到，抛出异常
    raise ValueError(f"未找到学号为 '{student_id}' 的学生！")


def update_student(students: List[Student], student_id: str,
                   name: Optional[str] = None,
                   class_name: Optional[str] = None) -> Student:
    """
    修改学生信息。

    Optional[str] 表示参数可以是 str 或 None。
    None 的含义是"不修改这一项"，方便调用方只改想改的字段。

    例如 update_student(students, "001", name="新名字")
    只改姓名，班级保持不变。

    Raises:
        ValueError: 找不到该学生
    """
    student = search_student(students, student_id)
    if student is None:
        raise ValueError(f"未找到学号为 '{student_id}' 的学生！")

    # 只有传了非空值才修改（保留原值的逻辑）
    if name is not None and name.strip():
        student.name = name
    if class_name is not None and class_name.strip():
        student.class_name = class_name
    return student


def search_student(students: List[Student], student_id: str) -> Optional[Student]:
    """
    按学号精确搜索学生。

    如果找到返回 Student 对象，找不到返回 None。
    返回 None 而不是抛异常，是因为"找不到"在搜索场景
    是正常结果，不算错误。

    时间复杂度：O(n)，线性查找。
    对于学生成绩系统（通常几百个学生），性能足够。
    """
    for s in students:
        if s.student_id == student_id:
            return s
    return None


def search_by_name(students: List[Student], keyword: str) -> List[Student]:
    """
    按姓名模糊搜索（不区分大小写）。

    只要姓名中包含关键字就匹配，返回所有匹配的学生列表。
    .lower() 转小写比较，实现不区分大小写的搜索。

    例如搜索 "张" 会匹配 "张三"、"张伟"、"小张" 等。

    列表推导式写法解析：
      [s for s in students if keyword in s.name.lower()]
      等价于：
        result = []
        for s in students:
            if keyword.lower() in s.name.lower():
                result.append(s)
    """
    keyword = keyword.lower()
    return [s for s in students if keyword in s.name.lower()]


# ==================== 成绩管理 ====================


def add_grade(students: List[Student], student_id: str,
              subject: str, score: float) -> None:
    """
    为指定学生录入或更新某科成绩。

    流程：
      1. 校验分数范围 (0-100)
      2. 查找学生是否存在
      3. 调用 Student.add_grade() 写入成绩

    如果该科目已存在成绩，会覆盖旧成绩（更新）。
    这是合理的设计，因为老师可能需要修正误录的分数。
    """
    # 分数范围校验：利用 Python 的链式比较 (0 <= score <= 100)
    if not (0 <= score <= 100):
        raise ValueError("成绩必须在 0-100 之间！")

    student = search_student(students, student_id)
    if student is None:
        raise ValueError(f"未找到学号为 '{student_id}' 的学生！")

    # 把实际添加逻辑委托给 Student 对象
    # 这是面向对象的"单一职责原则"：校验归 manager，存储归 Student
    student.add_grade(subject, score)


def remove_grade(students: List[Student], student_id: str,
                 subject: str) -> None:
    """
    删除指定学生的某科成绩。

    使用场景：老师录错了科目，需要删除后重新录入。
    """
    student = search_student(students, student_id)
    if student is None:
        raise ValueError(f"未找到学号为 '{student_id}' 的学生！")

    if subject in student.grades:
        # del 删除字典中的键值对
        del student.grades[subject]
    else:
        raise ValueError(f"该学生没有 '{subject}' 科目的成绩！")


# ==================== 显示与格式化 ====================


def format_student_table(students: List[Student]) -> str:
    """
    将学生列表格式化为对齐的表格字符串。

    格式化技巧：
      {变量:<12} 表示"左对齐，占 12 个字符宽度"
      {变量:^10} 表示"居中对齐，占 10 个字符"
      {变量:>8}  表示"右对齐，占 8 个字符"

    返回值是字符串（不是直接打印），这样调用方可以决定
    是 print() 输出还是存到文件。

    输出效果：
      学号         姓名     班级       科目数  平均分   全部及格
      ------------------------------------------------------------
      001          张三     一班       2      88.5    是
      002          李四     二班       3      72.0    否
    """
    if not students:
        return "暂无学生数据。"

    # 表头行：每个列标题按固定宽度对齐
    lines = [
        f"{'学号':<12} {'姓名':<8} {'班级':<10} {'科目数':<6} {'平均分':<8} {'全部及格'}",
        "-" * 60  # 分隔线，60 个横线字符
    ]

    for s in students:
        avg = s.get_average()
        passing = "是" if s.is_passing() else "否"
        # 三元表达式：值为真时取 if 前面的，为假时取 else 后面的
        avg_str = f"{avg:.1f}" if s.grades else "N/A"

        lines.append(
            f"{s.student_id:<12} {s.name:<8} {s.class_name:<10} "
            f"{len(s.grades):<6} {avg_str:<8} {passing}"
        )

    # "\n".join() 把多行字符串用换行符连接成一个字符串
    return "\n".join(lines)


def format_grades_detail(student: Student) -> str:
    """
    展示某个学生的详细成绩单。

    输出效果：
      ==================================================
      学号: 001  姓名: 张三  班级: 一班
      ==================================================
      科目         分数     等级
      ------------------------------
      数学         85      良好
      英语         92      优秀
      ------------------------------
      平均分: 88.5  |  全部及格
    """
    lines = [
        f"\n{'='*50}",
        f"学号: {student.student_id}  姓名: {student.name}  班级: {student.class_name}",
        f"{'='*50}",
    ]

    if not student.grades:
        lines.append("暂无成绩记录。")
    else:
        lines.append(f"{'科目':<12} {'分数':<8} {'等级'}")
        lines.append("-" * 30)

        # sorted() 按科目名字母/拼音顺序排列，输出整齐
        for subject, score in sorted(student.grades.items()):
            grade_level = _get_grade_level(score)
            lines.append(f"{subject:<12} {score:<8} {grade_level}")

        lines.append("-" * 30)
        lines.append(f"平均分: {student.get_average():.1f}  |  "
                     f"{'全部及格' if student.is_passing() else '有不及格科目'}")

    return "\n".join(lines)


def _get_grade_level(score: float) -> str:
    """
    根据分数返回对应的等级。

    函数名以 _ 开头（单下划线），表示这是模块"私有"函数，
    约定俗成不应被外部直接调用。在 Python 中没有真正的 private，
    更多是"请不要用"的暗示。

    等级划分：
      90-100 → 优秀
      80-89  → 良好
      70-79  → 中等
      60-69  → 及格
      0-59   → 不及格
    """
    if score >= 90:
        return "优秀"
    elif score >= 80:
        return "良好"
    elif score >= 70:
        return "中等"
    elif score >= 60:
        return "及格"
    else:
        return "不及格"


# ==================== 统计与排名 ====================


def rank_students(students: List[Student]) -> List[Tuple[int, Student, float]]:
    """
    按平均分降序排列学生。

    Tuple[int, Student, float] = (排名, 学生对象, 平均分)

    排序流程：
      1. 先给每个学生计算平均分，存为 (学生, 平均分) 元组
      2. 用 sort(key=lambda x: x[1]) 按元组第二个元素（平均分）排序
      3. reverse=True 表示从高到低（降序）
      4. 用 enumerate(scored, 1) 从 1 开始编号（排名）

    lambda x: x[1] 是什么？
      lambda 是匿名函数（没有名字的函数），x 是参数，x[1] 是返回值。
      等价于 def get_avg(pair): return pair[1]
    """
    # 列表推导式：创建 (学生, 平均分) 的配对列表
    scored = [(s, s.get_average()) for s in students]

    # sort 是原地排序（修改列表本身）
    # key=lambda x: x[1] 指定按元组的第二个元素（平均分）排序
    # reverse=True 指定降序（从高到低）
    scored.sort(key=lambda x: x[1], reverse=True)

    # enumerate(序列, 起始编号) 同时获取序号和值
    result = []
    for rank, (student, avg) in enumerate(scored, 1):  # 从 1 开始
        result.append((rank, student, avg))
    return result


def subject_stats(students: List[Student], subject: str) -> dict:
    """
    统计某科目的整体情况。

    返回一个字典，包含：
      - count: 参加该科目的学生人数
      - average: 平均分
      - highest: 最高分 + 对应的学生姓名
      - lowest: 最低分 + 对应的学生姓名
      - pass_rate: 及格率（百分比）

    sum() / max() / min() 是 Python 内置的统计函数，
    非常方便，不需要手动写循环。
    """
    # 第一步：筛选选了这门课的学生及其成绩
    scores = []
    for s in students:
        if subject in s.grades:
            scores.append((s, s.grades[subject]))  # 存 (学生, 该科分数) 元组

    # 空数据特殊处理
    if not scores:
        return {"subject": subject, "count": 0, "message": "暂无该科目的成绩数据"}

    # 第二步：纯分数列表，方便统计
    values = [v for _, v in scores]  # _ 是约定俗成的"不关心的变量"

    count = len(values)
    avg = sum(values) / count
    highest_score = max(values)  # 最大值
    lowest_score = min(values)   # 最小值

    # 及格人数：统计分数 >= 60 的个数
    pass_count = sum(1 for v in values if v >= 60)
    # 这个 sum(1 for ... if ...) 的技巧等价于：
    #   pass_count = len([v for v in values if v >= 60])

    # 第三步：找出拿了最高分和最低分的学生（可能有并列）
    highest_students = [s.name for s, v in scores if v == highest_score]
    lowest_students = [s.name for s, v in scores if v == lowest_score]

    return {
        "subject": subject,
        "count": count,
        "average": avg,
        "highest": highest_score,
        "lowest": lowest_score,
        "pass_rate": (pass_count / count * 100),  # 百分比
        "highest_students": highest_students,
        "lowest_students": lowest_students,
    }


def overall_stats(students: List[Student]) -> dict:
    """
    全校整体统计概览。

    汇总所有学生的所有成绩，计算：
      - 学生总数
      - 已录入成绩的人数
      - 成绩记录总数
      - 全校平均分
      - 全部及格人数和及格率
      - 涵盖的科目列表

    返回值是字典，方便 main.py 按需取用各个字段。
    """
    total = len(students)
    if total == 0:
        return {"total_students": 0, "message": "暂无学生数据"}

    # 只统计有成绩的学生（有人可能还没录入成绩）
    with_grades = [s for s in students if s.grades]

    all_scores = []      # 所有分数的列表
    all_subjects = set()  # set 自动去重，收集所有科目名

    for s in students:
        all_subjects.update(s.grades.keys())   # 收集科目
        all_scores.extend(s.grades.values())   # 收集分数
        # extend() vs append()：
        #   extend([85,92]) → 添加 85 和 92 两个元素
        #   append([85,92]) → 添加一个列表 [85,92] 作为单个元素

    # 全部及格的学生数
    passing_students = sum(1 for s in with_grades if s.is_passing())

    return {
        "total_students": total,
        "students_with_grades": len(with_grades),
        "overall_average": sum(all_scores) / len(all_scores) if all_scores else 0.0,
        "total_scores_count": len(all_scores),
        "all_subjects": sorted(all_subjects),
        "pass_rate": (passing_students / len(with_grades) * 100) if with_grades else 0.0,
        "passing_students": passing_students,
    }


def get_all_subjects(students: List[Student]) -> List[str]:
    """
    获取所有出现过的科目名称（排序好的列表）。

    set（集合）自动去重：
      如果三个学生的成绩分别是 {"数学":85}、{"数学":90}、{"英语":88}，
      则 subjects = {"数学", "英语"}

    排序后返回 ["数学", "英语"]，方便菜单显示和用户选择。
    """
    subjects = set()
    for s in students:
        subjects.update(s.grades.keys())
    return sorted(subjects)


def class_stats(students: List[Student], class_name: str) -> dict:
    """
    按班级统计成绩。

    流程：
      1. 筛选出指定班级的学生
      2. 汇总他们的所有成绩
      3. 计算平均分和及格率
    """
    # 列表推导式筛选同班学生
    class_students = [s for s in students if s.class_name == class_name]

    if not class_students:
        return {"class_name": class_name, "student_count": 0,
                "message": "该班级暂无学生"}

    # 收集该班所有成绩
    all_scores = []
    for s in class_students:
        all_scores.extend(s.grades.values())

    # 全部及格的学生数
    passing = sum(1 for s in class_students if s.is_passing())
    with_grades = [s for s in class_students if s.grades]

    return {
        "class_name": class_name,
        "student_count": len(class_students),
        "with_grades_count": len(with_grades),
        "average": sum(all_scores) / len(all_scores) if all_scores else 0.0,
        "pass_rate": (passing / len(with_grades) * 100) if with_grades else 0.0,
    }