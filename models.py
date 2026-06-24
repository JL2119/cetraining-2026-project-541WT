"""
学生成绩管理系统 — 数据模型
定义了 Student 类，包含学号、姓名、班级和成绩信息。

学习要点：
  - @dataclass 装饰器：自动生成 __init__、__repr__ 等方法，减少样板代码
  - 类型注解 (Dict[str, float])：声明泛型类型，提高代码可读性
  - field(default_factory=dict)：为可变默认值（如字典）创建新的空字典
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Student:
    """
    学生数据类

    属性:
        student_id (str): 学号，唯一标识一个学生
        name (str): 学生姓名
        class_name (str): 所在班级
        grades (Dict[str, float]): 成绩字典，键是科目名，值是分数（0-100）
    """
    student_id: str          # 学号，例如 "2024001"
    name: str                # 姓名，例如 "张三"
    class_name: str          # 班级，例如 "高一(1)班"
    grades: Dict[str, float] = field(default_factory=dict)  # 成绩字典，默认为空
    # 注意：为什么用 field(default_factory=dict) 而不是直接 = {}？
    # 因为 Python 中可变默认参数会被所有实例共享，field(default_factory=dict)
    # 确保每个 Student 对象都有自己独立的 grades 字典。

    def add_grade(self, subject: str, score: float) -> None:
        """
        添加或更新某科目的成绩。

        会自动校验分数范围（0-100），超出范围抛出异常。
        如果科目已存在，会覆盖旧成绩。
        """
        # 校验分数合法性
        if not (0 <= score <= 100):
            raise ValueError(f"成绩必须在 0-100 之间，收到: {score}")
        # 字典赋值：键=科目名，值=分数
        self.grades[subject] = score

    def get_average(self) -> float:
        """
        计算该学生的平均分（所有科目的算术平均）。
        如果没有录入任何成绩，返回 0.0。
        """
        # 空字典判断：如果还没录入成绩，直接返回 0
        if not self.grades:
            return 0.0
        # sum() 求和所有分数 / len() 科目数量 = 平均分
        return sum(self.grades.values()) / len(self.grades)

    def is_passing(self, pass_score: float = 60.0) -> bool:
        """
        判断该学生是否所有科目都及格。

        Args:
            pass_score: 及格线，默认 60 分

        Returns:
            True 表示所有科目分数 >= 及格线，False 表示至少有一门不及格
        """
        # 没有成绩也算"不及格"
        if not self.grades:
            return False
        # all() 函数：所有元素为 True 才返回 True
        # 这里检查每门课是否 >= 及格线
        return all(score >= pass_score for score in self.grades.values())

    def to_dict(self) -> dict:
        """
        将 Student 对象转为普通字典，方便 JSON 序列化。

        Python 对象不能直接存入 JSON 文件，
        需要先转成字典（dict），再由 json.dump() 写入。
        """
        return {
            "student_id": self.student_id,
            "name": self.name,
            "class_name": self.class_name,
            "grades": self.grades
        }

    @classmethod  # 类方法：第一个参数是类本身（cls），不是实例（self）
    def from_dict(cls, data: dict) -> "Student":
        """
        从字典创建 Student 对象（to_dict 的逆操作）。

        从 JSON 文件加载数据后，用这个函数把字典还原为 Student 对象。
        加引号 "Student" 是因为类还没定义完，不能直接引用 — 这叫"前向引用"。
        """
        return cls(
            student_id=data["student_id"],
            name=data["name"],
            class_name=data["class_name"],
            grades=data.get("grades", {})  # .get() 带默认值：没有 "grades" 键时返回 {}
        )

    def __str__(self) -> str:
        """
        定义对象的"字符串表示"。

        当 print(student) 或 f"{student}" 时，自动调用这个函数。
        """
        avg = self.get_average()
        grade_count = len(self.grades)
        return (f"学号: {self.student_id} | 姓名: {self.name} | "
                f"班级: {self.class_name} | 科目数: {grade_count} | "
                f"平均分: {avg:.1f}")  # :.1f 表示保留 1 位小数