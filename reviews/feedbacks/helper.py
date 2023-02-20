
import re, psycopg2

DB_HOST = "localhost"
DB_NAME = "reviews_db"
DB_USER = "postgres"
DB_PASSWORD = "0414798688aB"
DB_PORT = "5432"

# Returns a list of feedback posts and replies from the administrator if it exists
def feedback_list(user_id, id_string):
    conn = None
    query = f"""
        select f.title, f.category, f.content, f.solved, f.date_posted, string_agg(views.comment, ', ') as comments, 
        string_agg(cast(views.date_posted as text), ', ') as comments_date
        from (
            select * from feedback_comments c
            order by c.date_posted desc
        ) as views
            right join feedback f on (views.feedback_id = f.id)
        where f.user_id = {user_id} {id_string}
        group by f.title, f.category, f.content, f.solved, f.date_posted
        order by f.date_posted desc
    """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query)
        fetch_list = cursor.fetchall()
        print(fetch_list)
        outer_list = []
        comments = []
        for element in fetch_list:
            inner_list = [] 
            comment_list = []
            date_list = []
            i = 0
            while (i < len(element)):
                if (element[i] is None): 
                    i += 1
                    continue
                if (i == 5):
                    comment_list = re.split(r', ', element[i])
                elif (i == 6): 
                    date_list = re.split(r', ', element[i])
                else: 
                    inner_list.append(element[i])
                i += 1
            new_list = [[list(i) for i in list(zip(comment_list, date_list))]]
            inner_list_final = inner_list + new_list
            outer_list.append(inner_list_final)

    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close()
    return outer_list