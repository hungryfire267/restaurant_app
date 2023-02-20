import psycopg2
import os
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

DB_HOST = "localhost"
DB_NAME = "reviews_db"
DB_USER = "postgres"
DB_PASSWORD = "0414798688aB"
DB_PORT = "5432"

# Gets the profile of a particular user
def get_user_profile(): 
    conn = None 
    query="""
        select u.id, u.username, u.email, u.location, u.role, count(*) as count
        from public.user u
            left join post p on (p.user_id = u.id)
        group by u.id, u.username, u.email, u.location, u.role
        order by u.id
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

# Gets the posts of a particular user
def get_user_posts(user_id, search):
    conn = None
    query = f"""
        select r.id, r.name, p.title, p.restaurant_rating, p.dish_rating, p.cost, p.content, p.date_posted, d.name, p.id, p.value,
        p.size, p.upvotes, c.comment, c.date_posted
        from post p
            left join restaurant r on r.id = p.restaurant_id
            left join dish d on d.id = p.dish_id
            left join public.user u on u.id = p.user_id
            left join restaurant_comment c on (c.post_id = p.id)
        where u.id = {user_id} {search}
        order by p.date_posted desc 
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


def get_user_cuisine(user_id): 
    conn = None
    query = """
        select r.cuisine, count(*)
        from restaurant r
            left join post p on (r.id = p.restaurant_id)
            left join public.user u on (u.id = p.user_id)
        where u.id = %s
        group by r.cuisine
    """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [user_id])
        fetch_list = cursor.fetchall()
        cuisine_list = [] 
        count_list = [] 
        for element in fetch_list: 
            cuisine_list.append(element[0])
            count_list.append(str(element[1]))

    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close() 
    return cuisine_list, count_list

def get_user_costs(user_id):
    conn = None 
    query = """ 
        select p.cost 
        from post p
            left join public.user u on (p.user_id = u.id)
        where u.id = %s
    """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [user_id])
        fetch_list = cursor.fetchall()
        cost_dict = {}
        cost_list = ['$', '$$', '$$$', '$$$$']
        for element in cost_list: 
            cost_dict[element] = 0
        for element in fetch_list: 
            if (element[0] < 10): 
                cost_dict['$'] += 1
            elif (element[0] < 25): 
                cost_dict['$$'] += 1
            elif (element[0] < 50): 
                cost_dict['$$$'] += 1
            else: 
                cost_dict['$$$$'] += 1
        cost_labels = []
        cost_values = [] 
        for element in cost_dict.keys():
            cost_labels.append(element)
            cost_values.append(str(cost_dict[element]))
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close() 
    return cost_labels, cost_values

def get_user_avg(user_id): 
    conn = None 
    query = """ 
        select avg(p.restaurant_rating) as avg_restaurant, avg(p.dish_rating) 
        from post p
            left join public.user u on (u.id = p.user_id)
        where u.id = %s
    """
    conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query, [user_id])
    fetch_list = cursor.fetchall()
    avg_restaurant = round(float(fetch_list[0][0]), 2)
    avg_dish = round(float(fetch_list[0][1]), 2)
    return avg_restaurant, avg_dish

def get_no_posts_week(user_id, date_posted):
    conn = None
    query = """
        select count(*)
        from post p
            left join public.user u on (u.id = p.user_id)
        where u.id = %s and p.date_posted > %s
    """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [user_id, date_posted])
        fetch_list = cursor.fetchall()
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close() 
    return fetch_list[0][0]

def get_user_ratings(user_id): 
    conn = None
    query = """
        select p.restaurant_rating, p.dish_rating
        from post p 
            left join public.user u on (u.id = p.user_id)
        where u.id = %s  
    """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [user_id])
        fetch_list = cursor.fetchall()
        restaurant_dict = {}
        dish_dict = {} 
        for i in range(1, 6):
            restaurant_dict[i] = 0
            dish_dict[i] = 0 
        for element in fetch_list: 
            restaurant_dict[element[0]] += 1
            dish_dict[element[1]] += 1
        restaurant_labels = []
        restaurant_values = []
        dish_labels = []
        dish_values = []
        for element in dish_dict.keys(): 
            restaurant_labels.append(element)
            restaurant_values.append(str(restaurant_dict[element]))
            dish_labels.append(element)
            dish_values.append(str(dish_dict[element]))
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close() 
    return restaurant_labels, restaurant_values, dish_labels, dish_values

def get_popular_restaurant_user(user_id): 
    conn = None
    query = """ 
        select r.name, count(*)
        from restaurant r
            left join post p on (p.restaurant_id = r.id)
            left join public.user u on (p.user_id = u.id)
        where u.id = %s
        group by r.name
        order by count desc, r.name asc
        limit 3
    """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [user_id])
        fetch_list = cursor.fetchall()
        popular_labels = []
        popular_values = []
        for element in fetch_list: 
            popular_labels.append(element[0])
            popular_values.append(element[1])
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close() 
    return popular_labels, popular_values

def get_top_3_dish_types(user_id): 
    conn = None 
    query = """ 
        select t.type, count(*)
        from dish_type t
            left join dish d on (t.id = d.dishtype_id)
            left join post p on (p.dish_id = d.id)
        where p.user_id = %s
        group by t.type
        order by count desc
        limit 3
    """
    try:
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [user_id])
        fetch_list = cursor.fetchall()
        labels = []
        values = []
        for element in fetch_list: 
            labels.append(element[0])
            values.append(element[1])
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close()
    return labels, values

def user_dashboard_info(user_id): 
    cuisine_labels, cuisine_values = get_user_cuisine(user_id)
    cost_labels, cost_values = get_user_costs(user_id)
    avg_restaurant, avg_dish = get_user_avg(user_id)
    past_date_one_wk = datetime.now() - timedelta(days=7)
    past_date_one_month = datetime.now() - relativedelta(months=1)
    past_date_half_yr = datetime.now() - relativedelta(months=6)
    past_date_one_yr = datetime.now() - relativedelta(months=12)
    count_wk = get_no_posts_week(user_id, past_date_one_wk)
    count_month = get_no_posts_week(user_id, past_date_one_month)
    count_half_yr = get_no_posts_week(user_id, past_date_half_yr)
    count_yr = get_no_posts_week(user_id, past_date_one_yr)
    restaurant_labels, restaurant_values, dish_labels, dish_values = get_user_ratings(user_id)
    popular_labels, popular_values =  get_popular_restaurant_user(user_id)
    top_3_dish_labels, top_3_dish_values = get_top_3_dish_types(user_id)
    return count_wk, count_month, count_half_yr, count_yr, avg_restaurant, avg_dish,\
        cuisine_labels, cuisine_values, cost_labels, cost_values, \
        restaurant_labels, restaurant_values, dish_labels, dish_values,\
        popular_labels, popular_values, top_3_dish_labels, top_3_dish_values
