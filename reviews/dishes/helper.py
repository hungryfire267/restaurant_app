import psycopg2
import os, re
from random import sample
DB_HOST = "localhost"
DB_NAME = "reviews_db"
DB_USER = "postgres"
DB_PASSWORD = "0414798688aB"
DB_PORT = "5432"

# Gets the top 3 dishes of the particular dish type 
def get_top_3_dishes(dish_type_id): 
    conn = None
    query = """
        select d.name, count(*), avg(p.dish_rating)
        from dish_type t 
            left join dish d on (t.id = d.dishtype_id)
            left join post p on (p.dish_id = d.id ) 
        where t.id = %s
        group by d.name
        order by count desc, avg desc, d.name
        limit 3
    """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [dish_type_id])
        fetch_list = cursor.fetchall()
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close()
    return fetch_list

# Get the three most popular restaurants of the dish type
def get_top_3_restaurants_dishes(dish_id): 
    conn = None
    query = """
        select r.name, count(t.type)
        from dish_type t
            left join dish d on (d.dishtype_id=t.id)
            left join post p on (p.dish_id=d.id)
            left join restaurant r on (r.id = p.restaurant_id)
        where t.id = %s
        group by r.name
        order by count desc
        limit 3
    """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [dish_id])
        fetch_list = cursor.fetchall()
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close()
    return fetch_list

# Gets average dish rating of the dish type
def get_avg_dish_rating(dish_type_id):
    conn = None
    query = """
        select avg(p.dish_rating)
        from dish_type t
            left join dish d on (t.id = d.dishtype_id)
            left join post p on (p.dish_id = d.id)
        where t.id = %s
    """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [dish_type_id])
        fetch_list = cursor.fetchall()
        avg = round(fetch_list[0][0], 2)
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close()
    return avg

# Gets the post id and dish name
def get_dish_images_sql(dish_id):
    conn = None 
    query = """ 
        select p.id, d.name
        from post p 
            left join dish d on (d.id = p.dish_id)
            left join dish_type t on (t.id = d.dishtype_id)
        where t.id = %s
        """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [dish_id])
        fetch_list = cursor.fetchall()
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close()
    return fetch_list

# Get posts including dishes
def get_dish_images(post_id_list): 
    dish_images = []
    for element in post_id_list:
        inner_list = [element[0], element[1], None, False]
        path = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/post/{element[0]}" 
        for files in os.listdir(path): 
            if re.match("dish", files): 
                print(inner_list)
                inner_list[2] = files
                dish_images.append(inner_list)
    if (len(dish_images) < 3):
        return dish_images
    else: 
        dish_images_indexes = [i for i in range(0, len(dish_images))]
        dish_images_indexes_sample = sample(dish_images_indexes, 3)
        for element in dish_images_indexes_sample: 
            dish_images[element][3] = True
    return dish_images

def get_dish_posts(dish_type_id, dish_name, restaurant_name, sort, order):
    conn = None
    query = f"""
        select t.type, d.name, p.title, p.restaurant_rating, p.dish_rating, p.cost, p.value, p.size, p.content, p.date_posted, r.name, p.id, u.id, r.id,
        c.comment, c.date_posted, p.upvotes
        from dish_type t
            left join dish d on (d.dishtype_id = t.id)
            left join post p on (p.dish_id = d.id)
            left join restaurant r on (r.id = p.restaurant_id)
            left join public.user u on (u.id = p.user_id)
            left join restaurant_comment c on (c.post_id=p.id)
        where t.id = {dish_type_id} and d.name ~* '{dish_name}' and r.name ~* '{restaurant_name}'
        order by {sort} {order} p.date_posted desc
    """ 
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query)
        fetch_list = cursor.fetchall()
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close()
    return fetch_list

def image_adder(lists, type, user_id): 
    outer_list = []
    for element in lists: 
        i = 0
        inner_list = []
        while (i < len(element)): 
            inner_list.append(element[i])
            i += 1
        if (type == 'restaurant'):
            post_id = element[11]
            user_id = element[12]
        elif (type == 'account'):
            post_id = element[9]
            user_id = user_id
            restaurant_id = element[0]
        elif (type == 'dish'):
            post_id = element[11]
            user_id = element[12]
            restaurant_id = element[13]
        elif (type == 'trending'):
            post_id = element[14]
            user_id = element[15]
            restaurant_id = element[16]
            print(restaurant_id)
        elif (type == 'my_post'): 
            post_id = element[0]
            user_id = user_id
            restaurant_id = element[12]
        i = 0
        while (i < 4): 
            inner_list.append(None)
            i += 1
        path_post = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/post/{post_id}" 
        for files in os.listdir(path_post): 
            if re.match("restaurant", files): 
                inner_list[-2] = files
            elif re.match("dish", files): 
                inner_list[-1] = files
        path_user = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/user/{user_id}"
        if os.path.exists(path_user): 
            inner_list[-4] = os.listdir(path_user)[0]
        if (type != 'restaurant'): 
            path_restaurant = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/restaurant/{restaurant_id}"
            if os.path.exists(path_restaurant): 
                inner_list[-3] = os.listdir(path_restaurant)[0]
        outer_list.append(inner_list)
    return outer_list