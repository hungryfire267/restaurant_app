import psycopg2
import re
from datetime import datetime
from random import sample
import os

DB_HOST = "localhost"
DB_NAME = "reviews_db"
DB_USER = "postgres"
DB_PASSWORD = "0414798688aB"
DB_PORT = "5432"
API_KEY = "AIzaSyDHcRd0y-v7MUoSDQDDKAKfAO_XdfyhvBo"

def get_restaurant_information(label): 
    conn = None
    query = f"""
        select r.id, r.name, r.address, r.phone_number, avg(p.restaurant_rating), avg(p.dish_rating), r.cuisine
        from restaurant r 
            left join post p on (r.id = p.restaurant_id)
        where r.name ~* '{label}'
        group by r.id, r.name, r.address, r.phone_number
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

def logo_name_finder(path):
    for fname in os.listdir(path): 
        if fname.startswith("logo."):
            return fname

def restaurant_info_simplifier(lists): 
    new_list = []
    for element in lists: 
        inner_list = []
        i = 0
        score = 0
        while (i < len(element)):
            if (i == 2):
                address = element[i] 
                address = address.rsplit(' ', 1)[0]
                suburb_state = re.search(', (.*)', address).group(1)
                suburb_state = re.sub(r'( \w+$)', r',\1', suburb_state)
                inner_list.append(suburb_state)
            elif (i == 4 or i == 5):
                avg = round(float(element[i]), 2)
                score += avg
            else: 
                inner_list.append(element[i])
            i += 1
        inner_list.append(round(score/2, 2))
        path = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/restaurant/{element[0]}"
        logo_name = None
        if (os.path.exists(path)):
            logo_name = logo_name_finder(path)
        inner_list.append(logo_name)
        new_list.append(inner_list)
    return new_list

def get_averages(restaurant_id): 
    conn = None
    avg_dish_rating = None
    avg_restaurant_rating = None
    avg_dish_cost = None
    query = """
        select avg(p.restaurant_rating), avg(p.dish_rating), avg(p.cost)
        from post p
            left join restaurant r on (r.id = p.restaurant_id)
        where r.id = %s
    """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [restaurant_id])
        lists = cursor.fetchall()
        avg_restaurant_rating = round(float(lists[0][0]), 2) 
        avg_dish_rating = round(float(lists[0][1]), 2)
        avg_dish_cost = round(float(lists[0][2]), 2)
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close()
        return avg_restaurant_rating, avg_dish_rating, avg_dish_cost

def price_range(cost): 
    if (cost < 10): 
        return '$'
    elif (cost < 25): 
        return '$$'
    elif (cost < 50): 
        return '$$$'
    else: 
        return '$$$$'
    
def map_link_retriever(address):
    string_list = address.split()
    new_string = f"https://www.google.com/maps/embed/v1/place?key={API_KEY}&q={string_list[0]}"
    i = 1
    while (i < len(string_list)): 
        new_string = new_string + '+' + string_list[i]
        i += 1
    return new_string

def get_restaurant_suburb(address): 
    address_list = re.split(' ', address)
    current_state = address_list[-2]
    result = re.search(rf", (.*) {current_state}", address)
    return result.group(1), current_state

def get_popular_restaurants_suburb(restaurant_id, suburb, state): 
    conn = None
    query = """
        select r.id, r.name, count(*)
        from restaurant r
            left join post p on (r.id = p.restaurant_id)
        where r.id != %s and r.address ~ %s
        group by r.id, r.name
        order by count desc
        limit 5;
    """
    required = ', ' + suburb + ' ' + state
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [restaurant_id, required])
        fetch_list = cursor.fetchall()
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close() 
    return fetch_list

def dish_string(dish): 
    string = 'and '
    if (dish == ''):
        return dish
    else: 
        string = string + 'd.name~*' + f"\'{dish}\'"
        return string 

def get_posts(restaurant_id, type, order, dish): 
    conn = None
    query = f"""
        select p.title, d.name, p.cost, p.date_posted, p.content, p.restaurant_rating, p.dish_rating, p.upvotes, t.type, p.value, p.size, p.id,
        u.id, u.username, c.comment, c.date_posted, p.reply
        from post p
            left join dish d on (d.id = p.dish_id)
            left join dish_type t on (t.id = d.dishtype_id)
            left join public.user u on (u.id = p.user_id)
            left join restaurant_comment c on (c.post_id = p.id)
        where p.restaurant_id = {restaurant_id} {dish}
        order by {type} {order} p.date_posted desc
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

def get_restaurant_dish_images_sql(restaurant_id): 
    conn = None
    query = """ 
        select p.id, d.name
        from post p
            left join restaurant r on (r.id = p.restaurant_id)
            left join dish d on (d.id = p.dish_id)
        where r.id = %s
    """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [restaurant_id])
        fetch_list = cursor.fetchall()
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close()
    return fetch_list

def get_restaurant_dish_images(post_list):
    restaurant_images = []
    dish_images = []
    for element in post_list: 
        inner_list_restaurant = [element[0], element[1], None, False]
        inner_list_dish = [element[0], element[1], None, False]
        path = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/post/{element[0]}" 
        for files in os.listdir(path): 
            if re.match("restaurant", files): 
                inner_list_restaurant[2] = files
                restaurant_images.append(inner_list_restaurant)
            elif re.match("dish", files): 
                inner_list_dish[2] = files
                dish_images.append(inner_list_dish)
    if (len(restaurant_images) > 2): 
        restaurant_images_indexes = [i for i in range(0, len(restaurant_images))]
        restaurant_images_indexes_sample = sample(restaurant_images_indexes, 3)
        for element in restaurant_images_indexes_sample: 
            restaurant_images[element][3] = True
    if (len(dish_images) > 2): 
        dish_images_indexes = [i for i in range(0, len(dish_images))]
        dish_images_indexes_sample = sample(dish_images_indexes, 3)
        for element in dish_images_indexes_sample: 
            dish_images[element][3] = True
    return restaurant_images, dish_images

def get_info(user_id): 
    conn = None
    query = """
        select info
        from restaurant_user
        where user_id=%s
        order by date_posted desc
    """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [user_id])
        fetch_list = cursor.fetchall()
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close()
    return fetch_list[0][0]

def get_hours(restaurant_id): 
    conn = None
    query = """
        select day, morning, morning_start, morning_end, night, night_start, night_end
        from restaurant_hours
        where restaurant_id=%s
    """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [restaurant_id])
        fetch_list = cursor.fetchall()
        outer_list = []
        for element in fetch_list: 
            inner_list = [] 
            i = 0 
            while (i < len(element)): 
                if (i == 1 and element[i] == 'Closed'): 
                    break
                elif (i == 4 and element[i] == 'Closed'):
                    break
                elif (i == 1 or i == 4): 
                    i += 1
                    continue
                else:
                    inner_list.append(element[i])
                    i+= 1
            outer_list.append(inner_list)
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close()
    return outer_list

def get_city(address):
    word_list = re.split(r' ', address)
    state = word_list[-2]
    city_dict = {"NSW": "Sydney", "VIC": "Melbourne", "QLD": "Brisbane", "WA": "Perth", "SA": "Adelaide", "ACT": "Canberra", "TAS": "Hobart"}
    return city_dict[state]

def valid_phone_number(number, city):
    location_dict = {'Sydney': '(02)', 'Melbourne': '(03)', 'Brisbane': '(07)', 'Perth': '(08)', 
        'Adelaide': '(08)', 'Canberra': '(02)', 'Hobart': '(03)'}
    phone_number = location_dict[city] + ' ' + number[:4] + ' ' + number[4:]
    return phone_number

def directory_exists(type, id): 
    path = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/{type}/{id}"
    if os.path.exists(path) is False: 
        os.mkdir(path)
    return path

def transform_name(type, file_name):
    _, file_extension = os.path.splitext(file_name)
    new_name = type + file_extension
    return new_name

def logo_remover(type, path): 
    for fname in os.listdir(path):
        if fname.startswith(type):
            os.remove(os.path.join(path, fname))

def get_restaurant_rating_scores(restuarant_id): 
    conn = None
    lists = []
    query = """
        select p.restaurant_rating
        from post p 
            left join restaurant r on (r.id = p.restaurant_id)
        where r.id = %s
    """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [restuarant_id])
        fetch_list = cursor.fetchall() 
        for element in fetch_list: 
            lists.append(element[0])
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close() 
    return lists
    
def get_dish_rating_scores(restaurant_id): 
    conn = None
    lists = []
    query = """ 
        select p.dish_rating
        from post p
            left join restaurant r on (r.id = p.restaurant_id)
        where r.id = %s
    """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [restaurant_id])
        fetch_list = cursor.fetchall() 
        for element in fetch_list: 
            lists.append(element[0])
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close() 
    return lists

def convert_dict_ratings(lists): 
    new_dict = {}
    for i in range(1, 6):
        new_dict[i] = 0
    for element in lists: 
        new_dict[element] += 1
    ratings_keys = []
    ratings_values = []
    for element in new_dict.keys():
        ratings_keys.append(element)
        ratings_values.append(new_dict[element])
    return ratings_keys, ratings_values

def get_top_3(restaurant_id):
    conn = None
    query = f"""
        select d.name, avg(p.dish_rating)
        from post p
            left join restaurant r on (r.id = p.restaurant_id)
            left join dish d on (d.id = p.dish_id)
        where r.id = {restaurant_id} and p.dish_rating >= 4
        group by d.name
        order by avg desc, d.name asc
        limit 3
    """
    try:
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [restaurant_id])
        fetch_list = cursor.fetchall()
        labels = [] 
        ratings = []
        i = 1
        for element in fetch_list: 
            labels.append(f"{i}. {element[0]}")
            ratings.append(round(float(element[1]), 2))
            i += 1
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close() 

    return labels, ratings

def get_worst_3(restaurant_id):
    conn = None
    query = f"""
        select d.name, avg(p.dish_rating)
        from post p
            left join restaurant r on (r.id = p.restaurant_id)
            left join dish d on (d.id = p.dish_id)
        where r.id = {restaurant_id} and p.dish_rating < 3
        group by d.name
        order by avg asc, d.name asc
        limit 3
    """
    try:
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [restaurant_id])
        fetch_list = cursor.fetchall()
        labels = [] 
        ratings = []
        i = 1
        for element in fetch_list: 
            labels.append(f"{i}. {element[0]}")
            ratings.append(element[1])
            i += 1
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close() 

    return labels, ratings

def get_popular_3(restaurant_id): 
    conn = None 
    query = """
        select d.name, count(*)
        from dish d
            left join post p on (p.dish_id = d.id)
            left join restaurant r on (p.restaurant_id =r.id)
        where r.id = %s
        group by d.name
        order by count desc, d.name asc
        limit 3
    """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [restaurant_id])
        fetch_list = cursor.fetchall()
        popular_3_labels = [] 
        popular_3_values = [] 
        for element in fetch_list: 
            popular_3_labels.append(element[0])
            popular_3_values.append(str(element[1]))

    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close() 
    return popular_3_labels, popular_3_values

def get_avg_cost(restaurant_id): 
    conn = None
    query = """ 
        select avg(p.cost)
        from post p
            left join restaurant r on (p.restaurant_id = r.id)
            where r.id = 1
    """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [restaurant_id])
        fetch_list = cursor.fetchall()
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close() 
    return round(float(fetch_list[0][0]), 2)

def get_posts_month_restaurant(restaurant_id, date):
    print(date)
    conn = None
    query = """ 
        select count(*) as count
        from post p
            left join restaurant r on (r.id = p.restaurant_id)
        where restaurant_id = %s and p.date_posted > %s
    """
    try:
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [restaurant_id, date])
        fetch_list = cursor.fetchall()
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close() 
    return fetch_list[0][0]

def get_posts_v2(post_id): 
    conn = None
    query = f"""
        select p.title, d.name, p.cost, p.date_posted, p.content, p.restaurant_rating, p.dish_rating, p.upvotes, t.type, p.value, p.size, p.id,
        u.id, u.username, p.reply
        from post p
            left join dish d on (d.id = p.dish_id)
            left join dish_type t on (t.id = d.dishtype_id)
            left join public.user u on (u.id = p.user_id)
        where p.id = {post_id}
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