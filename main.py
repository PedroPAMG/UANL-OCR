from pdf2image import convert_from_path
import cv2
import pytesseract
from pytesseract import Output
import matplotlib.pyplot as plt
from os import scandir
import re
import os

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

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    threshold_img = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    details = pytesseract.image_to_data(threshold_img, output_type=Output.DICT, config=custom_config, lang='eng')
    total_boxes = len(details['text'])
    
    for sequence_number in range(total_boxes):
        if details['text'][sequence_number] == "Numero" and details['text'][sequence_number + 1] == "de" and details['text'][sequence_number + 2] == "Alumno":
            if int(details['conf'][sequence_number]) >30:
                (x, y, w, h) = (details['left'][sequence_number], details['top'][sequence_number], details['width'][sequence_number], details['height'][sequence_number])
                threshold_img = threshold_img[y - 20 : y + h + 80 , x - 30 : x + w + 1300]
    return threshold_img

def image_process(threshold_img):
    details = pytesseract.image_to_data(threshold_img, output_type=Output.DICT, config=custom_config, lang='eng')

    name = ''
    matricula = ''
    
    for i in range(len(details['text'])):
        if re.findall("\d{7}", details['text'][i]) and matricula == '':
            matricula = details['text'][i]
            continue

        if bool(re.findall("\d{7}", details['text'][i])) == False and matricula != '':
            name = name + details['text'][i]

        if re.findall("\d{7}", details['text'][i]) and matricula != '':
            break
    
    name = name.replace(",", " ")
    return matricula + " " +  name

def change_name(old_file_name, new_file_name):
    os.rename('PDF\{}'.format(old_file_name), 'PDF\{}.pdf'.format(new_file_name))

files = ls2('PDF/')

for file in files:
    pdf_to_image(file)

    threshold_img = image_pre_process(file)
    new_file_name = image_process(threshold_img)

    change_name(file, new_file_name)
    print("Archivo de Entrada:\t" + file)
    print("Archivo de Salida:\t" + new_file_name + ".pdf\n")