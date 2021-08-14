from __future__ import print_function

import urllib
import os
import subprocess
import cv2
import numpy as np
import re
import csv
import ast

from patterns import value_patterns, serving_size_patterns


image_dir='tmp/Images/'
res_dir='tmp/Results/'

def pre_process(img_path):
    ### image pre-processing ###
    img = cv2.imread(img_path)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)
    cv2.threshold(cv2.medianBlur(img, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    write_img_path = img_path.split('.')[0] + "_cvt.png"
    cv2.imwrite(write_img_path, img)

    return write_img_path

def do_tesseract(image_dir='tmp/English/', res_dir='tmp/Results/'):
    ### tesseract processing ###
    files =  os.listdir(image_dir)
    count = 0
    result = []
    for file in files:
        imgfilepath = image_dir + file
        imgfilepath = pre_process(imgfilepath)
        print (imgfilepath)


        jsonfilepath = res_dir + file.split('.')[0]

        
        command = 'tesseract {} {} -l eng'.format(
                imgfilepath,
                jsonfilepath,
            )

        try:
            output = subprocess.check_output(command, shell=True)
            print("output: ", output)
        except subprocess.CalledProcessError as e:
            print(e.output)

        os.remove(imgfilepath)

def find_fact(line_str):
    # extract the fact value using the value_patters
    facts = value_patterns.keys()
    for fact in facts:
        if fact in ['sodium', 'cholesterol']:
            for val in value_patterns[fact]:
                if val in line_str:
                    return fact, val
        elif fact in line_str:
            for val in value_patterns[fact]:
                if val in line_str: 
                    return fact, val

    return None, None

def extract_size(line_str):
    size_strs = re.findall('(\d{0,9}[9g])', line_str)
    for size in size_strs:
        if len(size) > 1:
            if size[-1] == '9' or size[-1] == 'g': 
                size_int = int(size[:-1])
                return size_int
    return -1

def extract_serving_size(lines):
    ### extract serving size ###
    size = -1
    for line in lines:
        for sc_pattern in serving_size_patterns:
            if sc_pattern in line.lower():
                size = extract_size(line)

    return size

def convertTuple(tup):
    str = ''.join(tup)
    return str

def get_fact_amount(line_str, fact):
    ### get fact amount and unit ###
    b_str = line_str.split(fact)[-1]
    amount = -1
    unit = ''
    if fact in ['fat', 'sodium', 'hydrate', 'fibre', 'fiber', 'sugar', 'cholesterol', 'protein', 'salt']:
        # these unit is "g" or "mg"
        # amts = re.findall('\d{0,9}[ mg9]', b_str)
        finds = re.findall('(\d+(?:\.\d+)?)( mg| g| m9| 9|g|mg|9|m9)', b_str)
        amts = []
        for item in finds:
            amts.append(convertTuple(item))
        for am in amts:
            if len(am) > 1:
                print (amts, "::::::::::", am, "------------>", line_str)
                am = am.strip()
                if 'm' in am:
                    size_str = am.split('m')[0].strip()
                    unit = 'mg'
                elif am[-1] == '9' or am[-1] == 'g': 
                    size_str = am[:-1]
                    unit = 'g'
                print ("size_str", size_str)
                if len(size_str) > 1 and size_str[0] == '0':
                    if '.' not in size_str:
                        size_str = '0.' + size_str[1:]
                
                size_num = ast.literal_eval(size_str)
                return size_num, unit

    elif fact in ['calorie']:
        # these unit is kcal
        amts = re.findall('\d+', b_str)
        unit = 'kcal'
        for am in amts:
            size_int = int(am)
            return size_int, unit
    elif fact in ['energy']:
        # these unit is KJ
        unit = 'KJ'
    else: 
        print ("Unkown Fact: **********************{}*******************".format(fact))
    
    return amount, unit

def parse_one_txt(file_path):
    nutritions = []
    print (file_path)
    
    # extract serving size
    file1ines = open(file_path, 'r')
    serving_size = extract_serving_size(file1ines)

    file1ines = open(file_path, 'r')
    count = 0
    for line in file1ines:
        line_str = line.strip().lower()
        count += 1

        # extract fact from line_str
        fact, value = find_fact(line_str)
        if value is not None:
            amount, unit = get_fact_amount(line_str, fact)
            if amount < 0:
                print ('fact "{}" is exist, but no amount found in line ====> "{}"'.format(value, line_str))
            else:
                nutritions.append({'fact': value, 'amount': amount, 'unit': unit})
        else:
            print ('no fact in line: "{}"'.format(line_str))
    return serving_size, nutritions

def get_dict_list(image_name, serving_size, nutritions):
    result = []
    for item in nutritions:
        res_item = dict()
        res_item['image_id'] = "image_"+image_name
        res_item['Nutrient'] = item['fact']
        res_item['Amount'] = item['amount']
        res_item['Unit'] = item['unit']
        res_item['Serving size'] = serving_size
        res_item['Serving size unit'] = 'g'
        res_item['Language'] = 'English'

        result.append(res_item)
    return result

def parse_txt(txt_dir):
    txt_files =  os.listdir(txt_dir)

    keys = ['image_id', 'Nutrient', 'Amount', 'Unit', 'Serving size', 'Serving size unit', 'Language']
    with open('tmp/output.csv', 'w', newline='', encoding='utf-8')  as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        for tf in txt_files:
            # if tf == "22.txt":
                serving_size, nutritions = parse_one_txt(txt_dir+tf)
                img_res = get_dict_list(tf.replace('.txt', ''), serving_size, nutritions)
                dict_writer.writerows(img_res)
                print (nutritions)

#do_tesseract(image_dir, res_dir)
#parse_txt(res_dir)