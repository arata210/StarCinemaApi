from flask import Flask, redirect, url_for, request
import random
import mysql.connector
import string


app = Flask(__name__)


class MySQLConn:
    """
    MySQL操作, 连接/关闭/增/删/改/查
    """
    # 初始化 MySQL 连接
    def __init__(self, host='localhost', user='root', password='123456', database='starcinema'):
        # 初始化数据库连接
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        # 创建游标对象
        self.cursor = self.conn.cursor()

    def close_conn(self):
        # 关闭游标和连接
        self.cursor.close()
        self.conn.close()

    def execute_query(self, query, params=None):
        # 执行查询
        if params is not None:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        # 获取查询结果
        result = self.cursor.fetchall()
        # 结果为空返回None
        if len(result) == 0:
            return None
        # 返回查询结果
        return result

    def execute_insert(self, query, data):
        try:
            # 执行插入操作
            self.cursor.execute(query, data)
            # 提交事务
            self.conn.commit()
            # 返回插入的记录的ID
            return self.cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            # 发生错误时回滚事务
            self.conn.rollback()
            return None

    def execute_delete(self, query, data=None):
        try:
            # 执行删除操作
            self.cursor.execute(query, data)
            # 提交事务
            self.conn.commit()
            # 返回受影响的行数
            return self.cursor.rowcount
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            # 发生错误时回滚事务
            self.conn.rollback()
            return 0

    def execute_update(self, query, data):
        try:
            # 执行更新操作
            self.cursor.execute(query, data)
            # 提交事务
            self.conn.commit()
            # 返回受影响的行数
            return self.cursor.rowcount
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            # 发生错误时回滚事务
            self.conn.rollback()
            return 0


sqldb = MySQLConn()


@app.route('/')
def index():
    return 'Welcome to StarCinema!'


@app.route('/api/my/passcode')
def passcode():
    phone = request.args.get('phone')
    if phone is None:
        return 'Error' # 101 : No PhoneNum
    q1 = "select * from users where phone=%s"
    result = sqldb.execute_query(q1, (phone,))
    if result is None:
        q2 = "INSERT INTO users (name, phone, password, status) VALUES (%s, %s, %s, %s)"
        name = '用户' + phone[-4:]
        code = random.randint(100000, 999999)
        print(code)
        data = (name, phone, code, 0)
        print(sqldb.execute_insert(q2, data))
    else:
        q3 = "select password from users where phone=%s"
        code = sqldb.execute_query(q3, (phone,))[0][0]
    return str(code)


@app.route('/api/my/check')
def check():
    phone = request.args.get('phone')
    code = request.args.get('code')
    if phone is None or code is None:
        return 'Error'
    q1 = "select * from users where phone=%s"
    result = sqldb.execute_query(q1, (phone,))
    if result is None:
        return '0'
    else:
        q2 = "select password from users where phone=%s"
        code_check = sqldb.execute_query(q2, (phone,))[0][0]
        q4 = "select status from users where phone=%s"
        status_check = sqldb.execute_query(q4, (phone,))[0][0]
        if code_check == code:
            q3 = "UPDATE users SET status = %s WHERE phone = %s"
            print(sqldb.execute_update(q3, (1, phone)))
            return '1'
        else:
            return '0'



# @app.errorhandler(Exception)
# def handle_exception(e):
#     # 处理所有异常并重定向到主页
#     return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    # 如果页面未找到则重定向到主页
    return redirect(url_for('index'))


@app.errorhandler(500)
def internal_error(e):
    # 如果内部服务器错误则重定向到主页
    return redirect(url_for('index'))


@app.route('/favicon.ico')
def favicon():
    return '', 200  # No Content


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050, debug=True)
