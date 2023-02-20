import re
import requests
import os
from PIL import Image
import psycopg2

DB_HOST = "localhost"
DB_NAME = "reviews_db"
DB_USER = "postgres"
DB_PASSWORD = "0414798688aB"
DB_PORT = "5432"


def valid_phone_number(number, city):
    location_dict = {'Sydney': '(02)', 'Melbourne': '(03)', 'Brisbane': '(07)', 'Perth': '(08)', 
        'Adelaide': '(08)', 'Canberra': '(02)', 'Hobart': '(03)'}
    phone_number = location_dict[city] + ' ' + number[:4] + ' ' + number[4:]
    return phone_number

def get_dish_overview(dish_type):
    dish_type = re.sub(' +', ' ', dish_type).title()
    dish_type_wiki = re.sub(' ', '_', dish_type)
    response = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{dish_type_wiki}")
    page = response.json()
    overview = None
    if (page['type'] == "standard"): 
        overview = page['extract']
    return dish_type, overview

def directory_exists(type, id): 
    path = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/{type}/{id}"
    if os.path.exists(path) is False: 
        os.mkdir(path)
    return path

def transform_name(type, file_name):
    _, file_extension = os.path.splitext(file_name)
    new_name = type + file_extension
    return new_name

def image_resizer(path):
    im = Image.open(path)
    dish_type = re.split('/', path)[-1]
    width, height = im.size
    ratio = 900 / height
    newsize = (round(width * ratio), 900)
    im1 = im.resize(newsize)
    os.remove(path)
    im1 = im1.save(path)
    
def get_my_post(post_id): 
    conn = None 
    query = """ 
        select p.id, p.title, p.restaurant_rating, p.dish_rating, p.cost, p.value, p.size, p.content, p.date_posted, p.upvotes,
        d.name, t.type, r.id, r.name
        from post p
            left join dish d on (d.id = p.dish_id)
            left join dish_type t on (t.id = d.dishtype_id)
            left join restaurant r on (r.id = p.restaurant_id)
        where p.id = %s
    """
    try:
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, [post_id])
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

