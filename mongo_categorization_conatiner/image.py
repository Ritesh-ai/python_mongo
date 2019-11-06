import os
import sys
import urllib.request
import cv2
import time
import re
import time
import pandas as pd

from pymongo import MongoClient


path = os.path.join(os.getcwd(), 'images/')
cropPath = os.path.join(os.getcwd(), 'croppedImages/')

class Validations(object):
    def __init__(self):
        pass
    
    def strip_lower(self,text):
        try:
            return text.strip().lower()
        except:
            return ''

    def cropper(self,url, image_name):
        try:
            urllib.request.urlretrieve(url,path + str(image_name))
            img = cv2.imread(path + str(image_name))
            width = img.shape[0]
            height = img.shape[1]
            image = img.copy()
            if img.shape:
                new_width = 400
                new_height = 400
                left = int((width - new_width)/2)
                top = int((height - new_height)/2)
                right = int((width + new_width)/2)
                bottom = int((height + new_height)/2)

                crop = image[left:right, top:bottom]              # image[y:y+h, x:x+w]
                
                cv2.imwrite(cropPath+image_name+".jpg", crop)

                return str(cropPath+image_name+".jpg")
        except Exception as e:
            if os.path.isfile(path + str(image_name)):
                print(path + str(image_name))
                os.remove(path + str(image_name))
            return ''

    def email_validator(self,text):        
        try:
            email_val = "[a-zA-Z0-9]+@[a-z]+\.[a-z]{2,3}(\.)?[a-z]{0,2}"
            data = re.match(email_val, text)
            if data:
                return text
        except:
            return ''

    def phone_validator(self,text):
        try:
            phone_val = "\+?[0-9\-]{4,14}"
            data = re.match(phone_val, text)
            if data:
                return text
        except:
            return ''

    def countrycodeconverter(self,code):
        try:
            df = pd.read_excel("countrycodes.xls")
            data = df[df.Code == code]
            print(data.values.tolist())
            return data.values.tolist()[0][0]
        except:
            return ''
    
    def timestampcheck(self,text):
        from datetime import datetime
        try:
            year,month,day = text.split('T')[0].split("-")
            data = datetime(int(year),int(month),int(day))
            return text
        except:
            return datetime.now()

    def fb_httpvalidator(self,text):
        try:
            reg = "(https?:\/\/)?(www\.)?facebook\.(com|co.in)?\/.+"
            if re.match(reg, text):
                return text
        except:
            return ''

    def linkedin_httpvalidator(self,text):
        try:
            reg = "(https?:\/\/)?(www\.)?linkedin\.(com|co.in)?\/.+"
            if re.match(reg, text):
                return text
        except:
            return ''

    def twitter_httpvalidator(self,text):
        try:
            reg = "(https?:\/\/)?(www\.)?twitter\.(com|co.in)?\/.+"
            if re.match(reg, text):
                return text
        except:
            return ''
    
    def hourlycheck(self,text):
        try:
            rate = int(text)
            return rate
        except:
            return 0
        


client = MongoClient('localhost:27017')
db = client.eb
collection = db.users

validator = Validations()

fname_list, lname_list, city_list, company_name_list, user_type_list, review_list = [],[],[],[],[],[]
portfolio_list, questions_list, hourly_rate_list, fb_url_list, linkdin_url_list, twitter_url_list = [],[],[],[],[],[]
min_project_amount_list, max_project_amount_list, country_list, image_new_path_list, number_list, email_list = [],[],[],[],[],[]
reg_date_list, user_profile_completed_list = [],[]

for index,post in enumerate(collection.find()):
    print(index+1)
    fname = post['user_fname']
    fname_list.append(validator.strip_lower(fname))

    lname = post['user_lname']
    lname_list.append(validator.strip_lower(lname))

    city  =  post['user_city']
    city_list.append(validator.strip_lower(city))

    company_name = post['user_company_name']
    company_name_list.append(validator.strip_lower(company_name))

    user_type = post['user_type']
    user_type_list.append(validator.strip_lower(user_type))

    reviews = post['reviews']
    if len(reviews) != 0:
        data = [validator.strip_lower(item) for item in reviews]
        review_list.append(data)
    else:
        review_list.append([])
    

    # portfolio = post['user_portfolio']
    # if len(portfolio) > 1:
    #     for item in portfolio:
    #         title = item['title']
    #         title = validator.strip_lower(title)
    #         description = item['description']
    #         description = validator.strip_lower(description)
    #         image = item['image']
            
    questions = post['user_questions']
    questions_list.append({key: validator.strip_lower(value) for key,value in questions.items()})

    hourly_rate = post['hourly_rate']
    hourly_rate_list.append(validator.hourlycheck(hourly_rate))

    fb_url = post['user_fb_url']
    fb_url_list.append(validator.fb_httpvalidator(fb_url))

    linkdin_url = post['user_linkdin_url']
    linkdin_url_list.append(validator.linkedin_httpvalidator(linkdin_url))
    
    twitter_url = post['user_twitter_url']
    twitter_url_list.append(validator.twitter_httpvalidator(twitter_url))
    
    reg_date = post['user_reg_date']
    reg_date_list.append(validator.timestampcheck(reg_date))

    try:min_project_amount = int(post['user_min_project_amount'])
    except: pasmin_project_amount = 0
    min_project_amount_list.append(min_project_amount)
    
    try:max_project_amount = int(post['user_max_project_amount'])
    except: max_project_amount = 0
    max_project_amount_list.append(max_project_amount)

    country = post['user_country']
    country_list.append(validator.countrycodeconverter(country))

    try:
        image_name = str(str(post['user_fname'])+str(post['user_id']))
    except:
        image_name = str(str(post['user_fname'])+str(post['_id']))

    image_url = str(post['user_image'])
    
    image_new_path = validator.cropper(image_url,image_name)
    image_new_path_list.append(image_new_path)

    num_text = post['user_mobile']
    number_list.append(validator.phone_validator(num_text))

    email_text = post['user_email']
    email_list.append(validator.email_validator(email_text))

    user_profile_completed = 0
    for item in post.values():
        if (item != None) and (item != 0) and (type(item) is not float):
            if (type(item) is list):
                if len(item) != 0:
                    user_profile_completed+=1
                else:
                    pass
            elif (type(item) is dict):
                if len(item) != 0:
                    user_profile_completed+=1
                else:
                    pass
            else:
                user_profile_completed+=1
    user_profile_completed_list.append(user_profile_completed)
    # break


data_container = {'fname_list': fname_list, 'lname_list': lname_list, 'city_list': city_list, 'company_name_list': company_name_list, 'user_type_list': user_type_list, 'review_list': review_list, 'questions_list': questions_list, 'hourly_rate_list': hourly_rate_list, 'fb_url_list': fb_url_list, 'linkdin_url_list': linkdin_url_list, 'twitter_url_list': twitter_url_list, 'min_project_amount_list': min_project_amount_list, 'max_project_amount_list': max_project_amount_list, 'country_list': country_list, 'image_new_path_list': image_new_path_list, 'number_list': number_list, 'email_list': email_list, 'reg_date_list': reg_date_list, 'user_profile_completed_list': user_profile_completed_list }


data = pd.DataFrame(data_container)

print(data)

data.to_csv("mongo_data_container.csv")
