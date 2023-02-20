import os
from random import sample
image_list = [] 
path = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/post"
for directory in os.listdir(path):
    path_directory = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/post/{directory}"
    for file in os.listdir(path_directory): 
        image_list.append([f'{directory}/{file}', False])
image_indexes = [i for i in range(0, len(image_list))]
sampled_indexes = sample(image_indexes, 3)
for element in sampled_indexes: 
    image_list[element][1] = True
print(image_list)
