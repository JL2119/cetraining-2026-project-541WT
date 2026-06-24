"""
学生成绩管理系统 — 主程序
交互式命令行菜单，连接所有功能模块。

学习要点：
  - 全局变量 vs 函数参数：数据怎么在各个函数之间共享
  - 菜单驱动架构：while True + 字典映射的模式
  - 用户输入处理：校验、错误提示、安全返回
  - try/except：捕获异常而不是让程序崩溃
  - 模块导入：from-import 语句的用法

运行方法：
  cd grades_system/
  python main.py
"""

import os
import sys
from typing import List

from models import Student
from manager import (
    add_student, delete_student, update_student,
    search_student, search_by_name,
    add_grade, remove_grade,
    format_student_table, format_grades_detail,
    rank_students, subject_stats, overall_stats,
    get_all_subjects, class_stats,
)
from storage import save_data, load_data, export_csv


# ==================== 全局状态 ====================

# students 是全局变量，存储所有学生数据
# 所有菜单函数都直接读取和修改这个列表
# 这是"全局可变状态"模式，适合单线程小程序的简单方案
students: List[Student] = []  # 当前内存中的所有学生
DATA_FILE = "students.json"   # 数据文件名


# ==================== 工具函数 ====================

def clear_screen():
    """
    清屏函数，兼容 Windows 和 Linux/Mac。

    os.name 判断操作系统：
      'nt' = Windows → 用 cls 命令
      'posix' = Linux/Mac → 用 clear 命令
    """
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    """
    暂停等待用户按键。

    每个菜单操作完成后调用，让用户有时间看完结果，
    按 Enter 后再返回主菜单。这是一个简单的用户体验设计。
    """
    input("\n按 Enter 键返回主菜单...")


def safe_input(prompt: str) -> str:
    """
    安全的输入函数，支持随时退出。

    如果用户输入 'q'（大小写均可），返回 None。
    调用方检查返回值是否为 None 来决定是否返回上级菜单。

    这是贯穿整个系统的重要设计：任何时候输入 q 都可以安全退出当前操作。
    """
    value = input(prompt).strip()  # strip() 去除首尾空格
    if value.lower() == "q":      # lower() 转小写，不区分 Q 和 q
        return None
    return value


def get_float_input(prompt: str) -> float | None:
    """
    获取浮点数输入，带校验。

    float | None 是 Python 3.10+ 的联合类型写法（等价于 Optional[float]）。

    校验逻辑：
      1. 输入 q → 返回 None（退出当前操作）
      2. 输入不是数字 → 提示错误，返回 None
      3. 数字不在 0-100 范围 → 提示错误，返回 None
      4. 合法数字 → 返回浮点数值
    """
    raw = safe_input(prompt)
    if raw is None:
        return None

    try:
        val = float(raw)  # 字符串转浮点数，非数字会抛出 ValueError
        if 0 <= val <= 100:
            return val
        else:
            print("[警告]  分数必须在 0-100 之间！")
            return None
    except ValueError:
        # 用户输入了非数字内容（如 "abc"）
        print("[警告]  请输入有效的数字！")
        return None


# ==================== 各菜单功能 ====================
# 每个菜单函数对应主菜单的一个选项
# 函数名约定：menu_ + 功能描述
# 每个函数都是独立的"页面"，包含完整的交互流程


def menu_add_student():
    """菜单 1：添加学生"""
    clear_screen()
    print("=" * 50)
    print("  添加学生  (输入 q 可随时返回)")
    print("=" * 50)

    # 三步获取用户输入
    sid = safe_input("请输入学号: ")
    if sid is None:       # 用户输入了 q
        return

    name = safe_input("请输入姓名: ")
    if name is None:
        return

    class_name = safe_input("请输入班级: ")
    if class_name is None:
        return

    # try/except 捕获可能的异常（学号重复等）
    try:
        add_student(students, sid, name, class_name)
        print(f"\n[成功] 学生 '{name}'（学号: {sid}）添加成功！")
    except ValueError as e:
        # e 是异常对象，str(e) 就是错误消息
        print(f"\n[错误] 添加失败: {e}")
    pause()


def menu_view_all():
    """菜单 2：查看所有学生（表格形式）"""
    clear_screen()
    print("=" * 50)
    print(f"  所有学生列表（共 {len(students)} 人）")
    print("=" * 50)
    print()
    # format_student_table() 返回格式化的表格字符串，直接打印
    print(format_student_table(students))
    pause()


def menu_search():
    """菜单 3：搜索学生（支持学号精确搜索和姓名模糊搜索）"""
    clear_screen()
    print("=" * 50)
    print("  搜索学生  (输入 q 可随时返回)")
    print("=" * 50)
    print("  1. 按学号精确搜索")
    print("  2. 按姓名模糊搜索")
    print("-" * 50)

    choice = safe_input("请选择 (1/2): ")
    if choice is None:
        return

    if choice == "1":
        # 精确搜索：输入完整学号
        sid = safe_input("请输入学号: ")
        if sid is None:
            return
        student = search_student(students, sid)
        if student:
            # 找到 → 显示详细成绩单
            print(format_grades_detail(student))
        else:
            print(f"\n[错误] 未找到学号为 '{sid}' 的学生！")

    elif choice == "2":
        # 模糊搜索：输入姓名关键字
        keyword = safe_input("请输入姓名关键字: ")
        if keyword is None:
            return
        results = search_by_name(students, keyword)
        if results:
            print(f"\n[搜索] 找到 {len(results)} 个匹配的学生:\n")
            print(format_student_table(results))
        else:
            print(f"\n[错误] 未找到姓名包含 '{keyword}' 的学生！")
    else:
        print("[警告]  无效选择！")
    pause()


def menu_update_student():
    """菜单 4：修改学生信息"""
    clear_screen()
    print("=" * 50)
    print("  修改学生信息  (输入 q 可随时返回)")
    print("=" * 50)

    sid = safe_input("请输入要修改的学生学号: ")
    if sid is None:
        return

    student = search_student(students, sid)
    if not student:
        print(f"\n[错误] 未找到学号为 '{sid}' 的学生！")
        pause()
        return

    # 显示当前信息，方便用户决定改什么
    print(f"\n当前信息: {student}")
    print("（直接按 Enter 保留原值，输入 q 返回）")

    name = safe_input(f"新姓名 [{student.name}]: ")
    if name is None:
        return
    class_name = safe_input(f"新班级 [{student.class_name}]: ")
    if class_name is None:
        return

    try:
        # name or None：空字符串也视为 None（保留原值）
        update_student(students, sid, name or None, class_name or None)
        print(f"\n[成功] 学生信息更新成功！")
    except ValueError as e:
        print(f"\n[错误] 更新失败: {e}")
    pause()


def menu_delete_student():
    """菜单 5：删除学生（带二次确认）"""
    clear_screen()
    print("=" * 50)
    print("  删除学生  (输入 q 可随时返回)")
    print("=" * 50)

    sid = safe_input("请输入要删除的学生学号: ")
    if sid is None:
        return

    student = search_student(students, sid)
    if not student:
        print(f"\n[错误] 未找到学号为 '{sid}' 的学生！")
        pause()
        return

    # 二次确认：防止误删
    print(f"\n[警告]  即将删除以下学生:\n  {student}")
    confirm = safe_input("\n确认删除？(输入 yes 确认): ")
    if confirm and confirm.lower() == "yes":
        try:
            removed = delete_student(students, sid)
            print(f"\n[成功] 学生 '{removed.name}' 已删除！")
        except ValueError as e:
            print(f"\n[错误] 删除失败: {e}")
    else:
        print("\n已取消删除。")
    pause()


def menu_add_grade():
    """菜单 6：录入成绩（支持连续录入多科）"""
    clear_screen()
    print("=" * 50)
    print("  录入成绩  (输入 q 可随时返回)")
    print("=" * 50)

    sid = safe_input("请输入学生学号: ")
    if sid is None:
        return

    student = search_student(students, sid)
    if not student:
        print(f"\n[错误] 未找到学号为 '{sid}' 的学生！")
        pause()
        return

    # 显示已有科目，方便老师知道该录哪些
    print(f"\n学生: {student.name} | 已有科目: "
          f"{', '.join(sorted(student.grades.keys())) if student.grades else '无'}")
    print()

    # while True 循环：支持连续录入多科成绩
    while True:
        subject = safe_input("请输入科目名称 (输入 q 结束录入): ")
        if subject is None:
            break  # 退出循环，结束录入

        score = get_float_input(f"请输入 {subject} 成绩 (0-100): ")
        if score is None:
            continue  # 输入无效，继续下一轮

        try:
            add_grade(students, sid, subject, score)
            # 根据分数显示等级（三元表达式链式写法）
            grade_level = ("优秀" if score >= 90 else
                          "良好" if score >= 80 else
                          "中等" if score >= 70 else
                          "及格" if score >= 60 else
                          "不及格")
            print(f"[成功] {subject}: {score} 分 ({grade_level}) — 录入成功！\n")
        except ValueError as e:
            print(f"[错误] {e}\n")

    # 录入结束后显示最终成绩单
    print(f"\n[详情] {student.name} 的最终成绩单:")
    print(format_grades_detail(student))
    pause()


def menu_ranking():
    """菜单 7：成绩排名"""
    clear_screen()
    print("=" * 50)
    print("  成绩排名（按平均分降序）")
    print("=" * 50)

    if not students:
        print("\n暂无学生数据。")
        pause()
        return

    # 调用 manager.rank_students() 获取排名结果
    ranked = rank_students(students)

    # 排名表头
    print(f"\n{'排名':<6} {'学号':<12} {'姓名':<8} {'班级':<10} {'平均分':<8} {'科目数'}")
    print("-" * 60)

    for rank, student, avg in ranked:
        avg_str = f"{avg:.1f}" if student.grades else "N/A"
        # 前三名显示特殊标记
        medal = "第1名" if rank == 1 else "第2名" if rank == 2 else "第3名" if rank == 3 else f"{rank:>2}"
        print(f"{medal:<6} {student.student_id:<12} {student.name:<8} "
              f"{student.class_name:<10} {avg_str:<8} {len(student.grades)}")
    pause()


def menu_subject_stats():
    """菜单 8：科目统计分析"""
    clear_screen()

    all_subs = get_all_subjects(students)
    if not all_subs:
        print("=" * 50)
        print("  暂无任何科目成绩数据！")
        print("=" * 50)
        pause()
        return

    print("=" * 50)
    print("  科目统计分析")
    print("=" * 50)
    print(f"\n已有科目: {', '.join(all_subs)}")
    print()

    subject = safe_input("请输入要统计的科目名称: ")
    if subject is None:
        return

    stats = subject_stats(students, subject)
    if "message" in stats:
        print(f"\n[警告]  {stats['message']}")
        pause()
        return

    # 显示科目统计结果
    print(f"\n[统计] {subject} 科目统计:")
    print("-" * 40)
    print(f"  参考人数:    {stats['count']} 人")
    print(f"  平均分:      {stats['average']:.1f} 分")
    print(f"  最高分:      {stats['highest']} 分  "
          f"({'、'.join(stats['highest_students'])})")
    # '、'.join() 用顿号连接多人名字，如 "张三、李四"
    print(f"  最低分:      {stats['lowest']} 分  "
          f"({'、'.join(stats['lowest_students'])})")
    print(f"  及格率:      {stats['pass_rate']:.1f}%")
    pause()


def menu_overall_stats():
    """菜单 9：整体统计概览（全校 + 各班级）"""
    clear_screen()
    print("=" * 50)
    print("  整体统计概览")
    print("=" * 50)

    stats = overall_stats(students)
    if "message" in stats:
        print(f"\n[警告]  {stats['message']}")
        pause()
        return

    # 全校统计
    print(f"\n[统计] 全校统计:")
    print("-" * 40)
    print(f"  学生总数:      {stats['total_students']} 人")
    print(f"  已录入成绩:    {stats['students_with_grades']} 人")
    print(f"  成绩记录总数:  {stats['total_scores_count']} 条")
    print(f"  全校平均分:    {stats['overall_average']:.1f} 分")
    print(f"  全部及格人数:  {stats['passing_students']} 人")
    print(f"  全部及格率:    {stats['pass_rate']:.1f}%")
    print(f"  涵盖科目:      {', '.join(stats['all_subjects']) if stats['all_subjects'] else '无'}")

    # 各班级统计
    # set 推导式收集所有班级名（去重）
    classes_set = set(s.class_name for s in students)
    if classes_set:
        print(f"\n[详情] 各班级统计:")
        print("-" * 40)
        print(f"{'班级':<12} {'人数':<6} {'有成绩':<8} {'平均分':<8} {'及格率'}")
        print("-" * 40)
        for cls in sorted(classes_set):
            cs = class_stats(students, cls)
            if cs.get("student_count", 0) > 0:
                avg_str = f"{cs['average']:.1f}" if cs.get('with_grades_count', 0) > 0 else "N/A"
                pass_str = f"{cs['pass_rate']:.1f}%" if cs.get('with_grades_count', 0) > 0 else "N/A"
                print(f"{cs['class_name']:<12} {cs['student_count']:<6} "
                      f"{cs['with_grades_count']:<8} {avg_str:<8} {pass_str}")
    pause()


def menu_export():
    """菜单 10：导出 CSV 报表"""
    clear_screen()
    print("=" * 50)
    print("  导出 CSV 报表")
    print("=" * 50)

    if not students:
        print("\n暂无学生数据可导出。")
        pause()
        return

    filename = safe_input("请输入导出文件名 (直接回车使用默认: grades_report.csv): ")
    if filename is None:
        return

    # 空输入用默认文件名
    filename = filename or "grades_report.csv"
    # 自动补 .csv 后缀
    if not filename.endswith(".csv"):
        filename += ".csv"

    try:
        filepath = export_csv(students, filename)
        print(f"\n[成功] 报表已成功导出到:\n   {filepath}")
    except Exception as e:
        print(f"\n[错误] 导出失败: {e}")
    pause()


def menu_save():
    """菜单 11：手动保存数据"""
    clear_screen()
    print("=" * 50)
    print("  保存数据")
    print("=" * 50)

    try:
        filepath = save_data(students, DATA_FILE)
        print(f"\n[成功] 数据已保存到: {filepath}")
        print(f"   共保存 {len(students)} 名学生的数据。")
    except Exception as e:
        print(f"\n[错误] 保存失败: {e}")
    pause()


# ==================== 主菜单 ====================

def show_menu():
    """
    显示主菜单界面。

    用 Unicode 框线字符绘制菜单边框：
      ╔ ═ ╗
      ║   ║
      ╠ ═ ╣
      ╚ ═ ╝

    菜单结构是典型的"数字选项 + 功能描述"模式。
    """
    clear_screen()
    print("╔" + "═" * 48 + "╗")
    print("║" + "  学生成绩管理系统（进阶版）  ".center(44) + "║")
    print("╠" + "═" * 48 + "╣")
    print(f"║  当前学生总数: {len(students):<4}                  ║")
    print("╠" + "═" * 48 + "╣")
    print("║  [1]  添加学生                              ║")
    print("║  [2]  查看所有学生                          ║")
    print("║  [3]  搜索学生                              ║")
    print("║  [4]  修改学生信息                          ║")
    print("║  [5]  删除学生                              ║")
    print("║  [6]  录入成绩                              ║")
    print("║  [7]  成绩排名                              ║")
    print("║  [8]  科目统计分析                          ║")
    print("║  [9]  整体统计概览                          ║")
    print("║  [10] 导出 CSV 报表                        ║")
    print("║  [11] 保存数据                             ║")
    print("║  [12] 退出系统                             ║")
    print("╚" + "═" * 48 + "╝")


def main():
    """
    主程序入口。

    程序流程：
      1. 启动时自动加载已有数据（load_data）
      2. 进入主循环：显示菜单 → 用户选择 → 执行功能 → 返回菜单
      3. 退出时自动保存数据

    字典映射模式（dispatch table）：
      menu_actions = {"1": 函数1, "2": 函数2, ...}
      这个模式比 if/elif 长链更优雅、易扩展。
      添加新功能只需在字典里加一行，不需要改主循环逻辑。
    """
    global students  # 声明使用全局变量

    # 启动时自动加载已有数据
    print("正在加载数据...")
    try:
        students = load_data(DATA_FILE)
        print(f"[成功] 已加载 {len(students)} 名学生的数据。")
    except Exception as e:
        print(f"[警告]  数据加载失败，从空数据开始: {e}")
        students = []

    # 字典映射：数字 → 菜单函数
    # 这是 "dispatch table" 模式，比 if/elif 链更优雅
    menu_actions = {
        "1": menu_add_student,
        "2": menu_view_all,
        "3": menu_search,
        "4": menu_update_student,
        "5": menu_delete_student,
        "6": menu_add_grade,
        "7": menu_ranking,
        "8": menu_subject_stats,
        "9": menu_overall_stats,
        "10": menu_export,
        "11": menu_save,
    }

    # 主循环：无限循环，直到用户选择退出
    while True:
        show_menu()
        choice = input("\n请选择操作 [1-12]: ").strip()

        if choice == "12":
            # 退出前自动保存（防止用户忘记手动保存）
            clear_screen()
            print("正在保存数据...")
            try:
                filepath = save_data(students, DATA_FILE)
                print(f"[成功] 已保存 {len(students)} 名学生的数据。")
            except Exception as e:
                print(f"[警告]  自动保存失败: {e}")
            print("\n感谢使用学生成绩管理系统，再见！\n")
            sys.exit(0)  # 正常退出程序，返回 0 表示成功

        # 从字典中取出对应的函数
        action = menu_actions.get(choice)
        if action:
            action()  # 执行菜单函数
        else:
            print("\n[警告]  无效选择，请输入 1-12 之间的数字！")
            pause()


# Python 的惯用写法：当直接运行本文件时才执行 main()
# 如果被其他文件 import，则不会自动执行
if __name__ == "__main__":
    main()