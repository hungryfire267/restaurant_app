import psycopg2
import datetime
import re

DB_HOST = "localhost"
DB_NAME = "reviews_db"
DB_USER = "postgres"
DB_PASSWORD = "0414798688aB"
DB_PORT = "5432"

# Verifies if a restaurant exists
def restaurant_verifier(name, address):
    conn = None
    result = None
    query = """
        select *
        from restaurant r
        where r.name = %s and r.address = %s
    """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [name, address])
        fetch_list = cursor.fetchall()
        print(fetch_list)
        if (len(fetch_list) > 0): 
            result = fetch_list[0][0]
        else: 
            result = None
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close()
    return result

# Get a list of restaurant applications
def restaurant_app_list(user_id, application_id): 
    conn = None
    query = f"""
        select *
        from restaurant_user r
            left join restaurant_user_comments c on (r.id = c.restaurantuser_id)
        where user_id = {user_id} {application_id}
        order by r.date_posted desc
    """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [user_id])
        fetch_list = cursor.fetchall()
        outer_list = []  
        for element in fetch_list: 
            indexes = [2, 3, 4, 5, 6, 7, 10, 11]
            inner_list = []
            for index in indexes: 
                if (element[index] is None):
                    continue
                if (index == 10): 
                    result = re.search('approved', element[index])
                    if result: 
                        inner_list.append('APPROVED')
                    else: 
                        inner_list.append('DECLINED')
                if (isinstance(element[index], datetime)): 
                    inner_list.append(element[index])
                else: 
                    inner_list.append(element[index].strip())
            outer_list.append(inner_list)
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close()
    return outer_list