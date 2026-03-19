import sqlite3

dbConn = None


def dbConnection():
    global dbConn
    if dbConn is None:
        dbConn = sqlite3.connect("demo01.db")


def createTable():
    if dbConn is None:
        dbConnection()

    dbCursor = dbConn.cursor()
    sqlStr = """SELECT count(name)
FROM sqlite_master
WHERE type='table' AND name='Students';
"""
    dbCursor.execute(sqlStr)

    if dbCursor.fetchone()[0] == 1:
        print("Table 'Students' already exists.")
    else:
        sqlStr = """CREATE TABLE Students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    gender TEXT NOT NULL,
    department TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    address TEXT
);"""
        dbCursor.execute(sqlStr)
        dbConn.commit()
        print("Table 'Students' created.")


def getStudentTableColumns():
    if dbConn is None:
        dbConnection()

    dbCursor = dbConn.cursor()
    dbCursor.execute("PRAGMA table_info('Students')")
    columns = dbCursor.fetchall()

    print("\n=== Students 資料表欄位 ===")
    for col in columns:
        print(col)


def input_required(msg, field_name):
    value = input(msg).strip()
    while value == "":
        print(f"{field_name}不可空白，請重新輸入。")
        value = input(msg).strip()
    return value


def insert_student(name, gender, department, email, phone, address):
    if dbConn is None:
        dbConnection()

    name = name.strip()
    gender = gender.strip()
    department = department.strip()
    email = email.strip()
    phone = phone.strip()
    address = address.strip()

    if name == "":
        print("姓名不可空白")
        return

    if gender == "":
        print("性別不可空白")
        return

    if department == "":
        print("系所不可空白")
        return

    if email == "":
        print("Email 不可空白")
        return

    if phone == "":
        print("電話不可空白")
        return

    dbCursor = dbConn.cursor()

    dbCursor.execute("SELECT * FROM Students WHERE email = ?", (email,))
    student = dbCursor.fetchone()

    if student is None:
        dbCursor.execute(
            """INSERT INTO Students (name, gender, department, email, phone, address)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, gender, department, email, phone, address),
        )
        dbConn.commit()
        print(f"Student {name} inserted successfully.")
    else:
        print("此 email 已存在，無法重複新增。")


def print_student_table(students):
    if not students:
        print("目前沒有任何資料。")
        return

    print(f"{'ID':<4} {'Name':<10} {'Gender':<8} {'Dept':<8} {'Email'}")
    print("-" * 50)

    for student in students:
        print(
            f"{student[0]:<4} {student[1]:<10} {student[2]:<8} {student[3]:<8} {student[4]}"
        )


def list_all_students():
    if dbConn is None:
        dbConnection()

    dbCursor = dbConn.cursor()
    dbCursor.execute("SELECT * FROM Students")
    students = dbCursor.fetchall()

    print("\n=== 所有學生資料 ===")
    print_student_table(students)


def find_student_by_id(student_id):
    if dbConn is None:
        dbConnection()

    dbCursor = dbConn.cursor()
    dbCursor.execute("SELECT * FROM Students WHERE id = ?", (student_id,))
    return dbCursor.fetchone()


def find_student(name, email):
    if dbConn is None:
        dbConnection()

    dbCursor = dbConn.cursor()
    dbCursor.execute(
        "SELECT * FROM Students WHERE name = ? AND email = ?", (name, email)
    )
    return dbCursor.fetchone()


def query_student():
    student_id = input("請輸入要查詢的學生 ID：").strip()
    student = find_student_by_id(student_id)

    if student:
        print("\n=== 查詢結果 ===")
        print_student_table([student])
    else:
        print("查無此學生資料。")


def update_student():
    if dbConn is None:
        dbConnection()

    id = input("請輸入要修改的學生 ID：").strip()
    student = find_student_by_id(id)

    if student is None:
        print("查無此學生，無法修改。")
        return

    print("\n=== 原始資料 ===")
    print(f"1. Name      : {student[1]}")
    print(f"2. Gender    : {student[2]}")
    print(f"3. Department: {student[3]}")
    print(f"4. Email     : {student[4]}")
    print(f"5. Phone     : {student[5]}")
    print(f"6. Address   : {student[7]}")

    print("\n若不想修改某欄，直接按 Enter 保持原值。")

    new_name = input(f"請輸入新姓名 [{student[1]}]：").strip()
    new_gender = input(f"請輸入新性別 [{student[2]}]：").strip()
    new_department = input(f"請輸入新系所 [{student[3]}]：").strip()
    new_email = input(f"請輸入新 Email [{student[4]}]：").strip()
    new_phone = input(f"請輸入新電話 [{student[5]}]：").strip()
    new_address = input(f"請輸入新地址 [{student[7]}]：").strip()

    if new_name == "":
        new_name = student[1]
    if new_gender == "":
        new_gender = student[2]
    if new_department == "":
        new_department = student[3]
    if new_email == "":
        new_email = student[4]
    if new_phone == "":
        new_phone = student[5]
    if new_address == "":
        new_address = student[7]

    dbCursor = dbConn.cursor()
    dbCursor.execute(
        """UPDATE Students
           SET name = ?, gender = ?, department = ?, email = ?, phone = ?, address = ?
           WHERE id = ?""",
        (
            new_name,
            new_gender,
            new_department,
            new_email,
            new_phone,
            new_address,
            student[0],
        ),
    )
    dbConn.commit()
    print("學生資料修改成功。")


def delete_student():
    if dbConn is None:
        dbConnection()

    student_id = input("請輸入要刪除的學生 ID：").strip()
    student = find_student_by_id(student_id)

    if student is None:
        print("查無此學生，無法刪除。")
        return

    print("\n=== 即將刪除的資料 ===")
    print(f"ID   : {student[0]}")
    print(f"Name : {student[1]}")
    print(f"Email: {student[4]}")

    confirm = input("確定要刪除嗎？(y/n)：").lower()

    if confirm == "y":
        dbCursor = dbConn.cursor()
        dbCursor.execute("DELETE FROM Students WHERE id = ?", (student[0],))
        dbConn.commit()
        print("學生資料已刪除。")
    else:
        print("已取消刪除。")


def department_student_count():
    if dbConn is None:
        dbConnection()

    dbCursor = dbConn.cursor()
    dbCursor.execute("SELECT department, COUNT(*) FROM Students GROUP BY department")
    stats = dbCursor.fetchall()

    if stats:
        print("\n=== 系所人數統計 ===")
        for dept, count in stats:
            print(f"{dept}: {count} 人")
    else:
        print("目前沒有學生資料，無法統計。")


def search_student_by_keyword():
    if dbConn is None:
        dbConnection()

    keyword = input("請輸入搜尋關鍵字（姓名或地址）：").strip()
    if keyword == "":
        print("關鍵字不可空白。")
        return

    dbCursor = dbConn.cursor()
    dbCursor.execute(
        "SELECT * FROM Students WHERE name LIKE ? OR address LIKE ?",
        (f"%{keyword}%", f"%{keyword}%"),
    )
    results = dbCursor.fetchall()

    if results:
        print("\n=== 搜尋結果 ===")
        print_student_table(results)
    else:
        print("查無符合的學生資料。")


def menu():
    while True:
        print("""
======== 學生資料管理系統 ========
1. 新增
2. 列表
3. 修改
4. 刪除
5. 系所人數統計
6. 關鍵字模糊搜尋
7. 單筆查詢
0. 離開
================================
""")
        choice = input("請輸入選項：").strip()

        if choice == "1":
            name = input_required("請輸入姓名：", "姓名")
            gender = input_required("請輸入性別：", "性別")
            department = input_required("請輸入系所：", "系所")
            email = input_required("請輸入 Email：", "Email")
            phone = input_required("請輸入電話：", "電話")
            address = input("請輸入地址：").strip()
            insert_student(name, gender, department, email, phone, address)

        elif choice == "3":
            update_student()

        elif choice == "7":
            query_student()

        elif choice == "2":
            list_all_students()

        elif choice == "4":
            delete_student()

        elif choice == "5":
            department_student_count()

        elif choice == "6":
            search_student_by_keyword()

        elif choice == "0":
            print("系統已結束。")
            break

        else:
            print("輸入錯誤，請重新選擇。")


def main():
    dbConnection()
    createTable()
    getStudentTableColumns()
    menu()

    if dbConn is not None:
        dbConn.close()


if __name__ == "__main__":
    main()
