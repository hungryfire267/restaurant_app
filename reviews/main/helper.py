import requests
import os
import re
import psycopg2
from datetime import datetime, timedelta
from random import sample

DB_HOST = "localhost"
DB_NAME = "reviews_db"
DB_USER = "postgres"
DB_PASSWORD = "0414798688aB"
DB_PORT = "5432"


def weather_data(user): 
    location = user.location
    response = requests.get(f"http://api.weatherapi.com/v1/current.json?key=0f398e2477314a2c8a2112232222912&q={location}&aqi=no")
    json_dict = response.json()
    weather_condition_now = json_dict['current']['condition']['text']
    weather_degrees_now = json_dict['current']['temp_c']
    weather_wind_now = json_dict['current']['wind_kph']
    wind_dir = json_dict['current']['wind_dir']
    return weather_condition_now, weather_degrees_now, weather_wind_now, wind_dir


def weather_pred(user, hour):
    location = user.location
    response = requests.get(f"http://api.weatherapi.com/v1/forecast.json?key=0f398e2477314a2c8a2112232222912&q={location}&days=2&aqi=no")
    json_dict = response.json()['forecast']['forecastday']
    min_temp = None
    max_temp = None
    weather_condition = None
    if (hour >= 0  and hour < 17): 
        max_temp = int(json_dict[0]['day']['maxtemp_c'])
        weather_condition = json_dict[0]['day']['condition']['text']
    else: 
        min_temp = int(json_dict[1]['day']['mintemp_c'])
        max_temp = int(json_dict[1]['day']['maxtemp_c'])
        weather_condition = json_dict[1]['day']['condition']['text']
    return min_temp, max_temp, weather_condition

def get_dishtype_list(): 
    conn = None
    query = """
        select type, overview, id
        from dish_type
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

def get_images_home(): 
    image_list = [] 
    path = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/post"
    for directory in os.listdir(path):
        path_directory = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/post/{directory}"
        for file in os.listdir(path_directory): 
            image_list.append([f'{directory}/{file}', False])
    if (len(image_list) > 2):
        image_indexes = [i for i in range(0, len(image_list))]
        sampled_indexes = sample(image_indexes, 3)
        for element in sampled_indexes: 
            image_list[element][1] = True
    return image_list

def get_trending_posts(time): 
    conn = None
    query = f"""
        select p.title, p.restaurant_rating, p.dish_rating, p.cost, p.value, p.size, p.content, p.date_posted, p.upvotes,
        d.name, d.id,
        t.type, t.overview,
        r.name, p.id, u.id, r.id
        from post p
            left join dish d on (p.dish_id = d.id)
            left join dish_type t on (d.dishtype_id = t.id)
            left join restaurant r on (r.id = p.restaurant_id)
            left join public.user u on (u.id = p.user_id)
        where p.date_posted > '{time}'
        order by p.upvotes desc, p.dish_rating, p.restaurant_rating
        limit 3;
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

def day_choices(): 
    now = datetime.now()
    date_one_day = now + timedelta(days=1)
    date_two_day = now + timedelta(days=2)
    choices = [(now.strftime('%A'), 'Today'), (date_one_day.strftime('%A'), 'Tomorrow'), 
            (date_two_day.strftime('%A'), date_two_day.strftime('%A %d %B %Y'))]
    return choices

def location_string(location_list): 
    string = ' and '
    if len(location_list) == 1: 
        string = string + 'r.address ~* ' + f"\'{location_list[0]}\'"
        return string
    i = 0 
    while (i < len(location_list)):
        if i == 0: 
            string = string + '('
        string = string + 'r.address ~* ' + f"\'{location_list[i]}\'"
        if (i == len(location_list) - 1):
            string = string + ')'
        else: 
            string = string + ' or '
        i += 1
    return string

def cuisine_string(cuisine): 
    if cuisine == '':
        return ''
    else: 
        return f" and r.cuisine = \'{cuisine}\'"
    
def restaurant_recommender(day, time, location, cuisine): 
    conn = None
    query = f"""
        select r.id, r.cuisine, r.address, h.day, h.morning, h.night, h.morning_start, h.morning_end, h.night_start, h.night_end
        from restaurant r
            left join restaurant_hours h on (h.restaurant_id=r.id)
        where (h.day = '{day}' or r.hour = False) {location} {cuisine}
    """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query)
        fetch_list = cursor.fetchall()
        new_list = []
        for element in fetch_list: 
            if element[4] == 'Closed':
                continue
            elif element[4] == 'Open': 
                if (time >= element[6] and time < element[7]):
                    new_list.append(element[0])
                else: 
                    if (element[5] == 'Closed'): 
                        continue
                    elif (time >= element[8] and time < element[9]):
                        new_list.append(element[0])
            else: 
                new_list.append(element[0])
            
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close()
    return new_list

def dish_type_string(dish_type): 
    string = ''
    if dish_type == '':
        return string
    else: 
        string = f" and t.type=\'{dish_type}\'"
        return string
def restaurant_recommender_simplified(restaurant_id, dish_type):
    conn = None
    query = f"""
        select r.id
        from restaurant r 
            left join post p on (r.id=p.restaurant_id)
            left join dish d on (p.dish_id=d.id)
            left join dish_type t on (d.dishtype_id=t.id)
        where r.id = {restaurant_id} {dish_type}
    """
    try: 
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host="localhost", port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query)
        fetch_list = cursor.fetchall()
        statement = False
        if len(fetch_list) > 0:
            statement = True
    except Exception as err: 
        print("DB error: ", err)
    finally: 
        if conn: 
            conn.close()
    return statement

def order_by_average_rating(restaurant_id): 
    conn = None
    query = """
        select r.id, (avg(p.restaurant_rating) + avg(p.dish_rating))/2 as average
        from restaurant r
            left join post p on (r.id = p.restaurant_id)
        where r.id = %s
        group by r.id
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
    return round(float(fetch_list[0][1]), 2)

def logo_name_finder(path):
    for fname in os.listdir(path): 
        if fname.startswith("logo."):
            return fname