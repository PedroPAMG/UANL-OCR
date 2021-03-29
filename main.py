from pdf2image import convert_from_path
import cv2
import pytesseract
from pytesseract import Output
import matplotlib.pyplot as plt
from os import scandir
import numpy as np
import re
import os

banned_symbol = ('/','|','"','!','(',')','_',';','.','~','‘','-','“','—',"'",'*',':','[',']','»',',','}','{','§','°','=')
banned_letter = ('a', 'b', 'c', 'd', 'e', 'é', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')
banned_number = ('0','1','2','3','4','5','6','7','8','9')

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
custom_config = r'--oem 3 --psm 6'

def ls2(path): 
    return [obj.name for obj in scandir(path) if obj.is_file()]

def pdf_to_image(pdf_name):
    images = convert_from_path(pdf_path = 'PDF/' + pdf_name , poppler_path = r'poppler-21.02.0\Library\bin')
    images[0].save(pdf_name + '.jpg', 'JPEG')

def image_pre_process(jpg_name):
    image = cv2.imread(jpg_name + '.jpg')
    os.remove(jpg_name + '.jpg')
    
    matricula_img = ''
    name_img = ''
    x = False
    
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    threshold_img = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    details = pytesseract.image_to_data(threshold_img, output_type=Output.DICT, config=custom_config, lang='eng')
    total_boxes = len(details['text'])
    
    for sequence_number in range(total_boxes):
        if details['text'][sequence_number] == "Alumno" and x == False:
            if int(details['conf'][sequence_number]) >30:
                (x, y, w, h) = (details['left'][sequence_number], details['top'][sequence_number], details['width'][sequence_number], details['height'][sequence_number])
                matricula_img = threshold_img[y - 10 : y + h + 60 , x - 45 : x + w + 50]
                x = True
                continue

        if details['text'][sequence_number] == "Alumno" and x == True:
            if int(details['conf'][sequence_number]) >30:
                (x, y, w, h) = (details['left'][sequence_number], details['top'][sequence_number], details['width'][sequence_number], details['height'][sequence_number])
                name_img = threshold_img[y + 12 : y + h + 65 , x - 150 : x + w + 600]

    return matricula_img, name_img

def image_process(matricula_img, name_img, file):
    name = ''
    matricula = ''
    
    if type(matricula_img).__module__ == np.__name__ and type(name_img).__module__ == np.__name__:
        matricula_details = pytesseract.image_to_data(matricula_img, output_type=Output.DICT, config=custom_config, lang='eng')
        name_details = pytesseract.image_to_data(name_img, output_type=Output.DICT, config=custom_config, lang='eng')

        for i in range(len(matricula_details['text'])):
            if re.findall("\d{7}", matricula_details['text'][i]) and matricula == '':
                matricula = matricula_details['text'][i]

                if int(len(matricula)) >= 8:
                    matricula = matricula[:7]
    
        for a in range(len(name_details['text'])):
            name = name + name_details['text'][a]

        for symbol in banned_number:
            name = name.replace(symbol , '')

        name = name.replace(",", " ")
        new_file_name = matricula + " " +  name
    
    else:
        file = file.replace('.pdf','')
        new_file_name = 'ERROR ' + file
    
    return new_file_name

def change_name(old_file_name, new_file_name):
    try:
        os.rename('PDF/{}'.format(old_file_name), 
                'PDF/{}.pdf'.format(new_file_name))
    except:
        os.rename('PDF/{}'.format(old_file_name), 
                'PDF/{}'.format('ERROR ' + old_file_name))

files = ls2('PDF/')

for file in files:
    print("Archivo de Entrada:\t" + file)

    pdf_to_image(file)
    
    matricula_img, name_img = image_pre_process(file)
    new_file_name = image_process(matricula_img, name_img, file)

    for symbol in banned_symbol:
        new_file_name = new_file_name.replace(symbol , '')
    for symbol in banned_letter:
        new_file_name = new_file_name.replace(symbol , '')

    change_name(file, new_file_name)

    print("Archivo de Salida:\t" + new_file_name + ".pdf\n")