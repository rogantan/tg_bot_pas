import psycopg2
import os


def connection_to_db():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="yfhmzy03",
        dbname="access_bars"
    )
    return conn

# def connection_to_db():
#     conn = psycopg2.connect(
#         host=os.getenv("DB_HOST"),
#         port=os.getenv("DB_PORT"),
#         user=os.getenv("DB_USER"),
#         password=os.getenv("DB_PASSWORD"),
#         dbname=os.getenv("DB_NAME")
#     )
#     return conn
def create_tables() -> None:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id VARCHAR(50) PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            first_name VARCHAR(50) NOT NULL
        );""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins(
            user_id VARCHAR(50) PRIMARY KEY,
            username VARCHAR(50)
        );""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS newsletters(
            id BIGSERIAL PRIMARY KEY,
            text TEXT,
            publish_date TIMESTAMP WITHOUT TIME ZONE,
            admin_id VARCHAR(50),
            FOREIGN KEY (admin_id) REFERENCES admins (user_id)
        );""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id BIGSERIAL PRIMARY KEY,
            question_text TEXT,
            publish_date TIMESTAMP WITHOUT TIME ZONE,
            admin_id TEXT,
            FOREIGN KEY (admin_id) REFERENCES admins (user_id)
        );""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS choices (
            id BIGSERIAL PRIMARY KEY,
            text TEXT,
            votes INT,
            question_id BIGINT,
            FOREIGN KEY (question_id) REFERENCES questions (id)
        );""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS total_statistic (
            id BIGSERIAL PRIMARY KEY,
            user_id VARCHAR(50),
            question_id BIGINT,
            choice_id BIGINT,
            answer_date TIMESTAMP WITHOUT TIME ZONE,
            FOREIGN KEY (question_id) REFERENCES questions (id),
            FOREIGN KEY (choice_id) REFERENCES choices (id),
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        );""")
    conn.commit()
    conn.close()


def add_user(user_id: str, username: str, first_name: str) -> None:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO users (user_id, username, first_name) "
                       "VALUES (%s, %s, %s)", (user_id, username, first_name))
    conn.commit()
    conn.close()


def select_users_id() -> list:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT user_id, username FROM users")
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result


def select_admin_id() -> tuple:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT user_id FROM admins "
                       "ORDER BY user_id DESC")
        result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result


def select_admins_id(user_id: str) -> tuple:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM admins WHERE user_id = %s", (user_id, ))
        result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result


def select_user(user_id: str) -> tuple:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id, ))
        result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result


def add_newsletter(text: str, date, admin_id: str) -> None:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO newsletters (text, publish_date, admin_id) "
                       "VALUES (%s, %s, %s)", (text, date, admin_id))
    conn.commit()
    conn.close()


def select_newsletters() -> list:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM newsletters")
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result


def save_question(question_text: str, admin_id: str, date) -> None:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO questions (question_text, admin_id, publish_date) "
                       "VALUES ((%s), (%s), (%s));", (question_text, admin_id, date))
    conn.commit()
    conn.close()


def save_variants(choice_text: str, admin_id: str) -> None:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT max(id) from questions WHERE admin_id = (%s);", (admin_id, ))
        result = cursor.fetchone()
    question_id = result[0]
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO choices (text, votes, question_id) "
                       "VALUES ((%s), (%s), (%s))", (choice_text, 0, question_id))
    conn.commit()
    conn.close()


def select_questions() -> list:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM questions")
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result


def get_question(num: int) -> tuple:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT question_text FROM questions WHERE id = %s", (num, ))
        result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result


def get_variants(num: int) -> list:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT text, id FROM choices WHERE question_id = %s", (num, ))
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result


def update_statistic(choice_id, user_id, date) -> None:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT question_id FROM choices WHERE id = (%s)", (choice_id, ))
        question_id = cursor.fetchone()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO total_statistic (user_id, question_id, choice_id, answer_date) "
                       "VALUES ((%s), (%s), (%s), (%s))", (user_id, question_id[0], choice_id, date))
    conn.commit()
    conn.close()


def select_total_statistic(user_id: str) -> list:
    conn = connection_to_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT username, question_text, text, answer_date FROM total_statistic "
                       "JOIN users ON users.user_id = total_statistic.user_id "
                       "JOIN questions ON question_id = questions.id "
                       "JOIN choices ON choice_id = choices.id "
                       "WHERE username = %s", (user_id, ))
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result