from zipfile import ZipFile
from PIL import Image, ImageFont, ImageDraw
import pytesseract
import io
import cv2 as cv
import numpy
# loading the face detection classifier
face_cascade = cv.CascadeClassifier('readonly/haarcascade_frontalface_default.xml')
eye_cascade = cv.CascadeClassifier("readonly/haarcascade_eye.xml")


#We are using this function to decide which file path we are going to pass to the main function
def which_zip_file():
    number = "0"
    while number != "1" and number != "2":
        number = input("which zip file do you want to use?, input 1 for images.zip or input 2 for small_img.zip ")
    if number == "1":    
        zip_file_path = "readonly/images.zip"
    if number == "2":
        zip_file_path = "readonly/small_img.zip"
    return zip_file_path

#This function grabs an image and parses it for text using pytesseract
def image_to_text(image):
    text = pytesseract.image_to_string(image)
    return text

def get_faces(image_dict):
#grabs the image from the image dictionary    
    pil_image  = image_dict
#turns the image into CV forma    
    cv_image = numpy.array(pil_image)
#transform to grayscale
    gray = cv.cvtColor(cv_image, cv.COLOR_BGR2GRAY)
#detects faces    
    faces = face_cascade.detectMultiScale(gray, 1.30)
    return faces

def make_the_image_dictionary(file_path):
#Creates an empty dictionary
    image_dict = {'images':{}, 'text':{}, 'faces_coord' : {}}
#Using a loop: gets an image from the zip file, adds it to the image dictionary, adds the text to text key and ads the face coordinates to faces_coord key
    with ZipFile(file= file_path, mode = 'r') as zippy:
        for file in zippy.namelist():
            temporary_reference = io.BytesIO(zippy.read(file))
            image_file = Image.open(temporary_reference).convert("RGB")
            image_dict['images'][file] = image_file
            image_dict['text'][file] = image_to_text(image_dict['images'][file]).lower()
            image_dict['faces_coord'][file] =  get_faces(image_dict['images'][file])
    return image_dict

def fill_colage(image_dict,key1):
#reset canvas    
    colage = 0
#creates new image    
    colage = Image.new("RGB", [625,275])
#sets coordinates
    y_cord = 25
    x_cord = 0    
    for x,y,h,w in image_dict['faces_coord'][key1]:
#grabs the image from image key and crops with the coordinates from faces_coord keys        
        crop = image_dict['images'][key1].crop((x,y,x+w,y+h))
#resizes the crop to a standard size    
        crop = crop.resize((125,125))
#adds the crop to the canvas    
        colage.paste(crop, (x_cord,y_cord))
        x_cord += 125
#move the paste coordinates        
        if x_cord >= 625:
            x_cord = 0
            y_cord += 125 
#choose font            
    font = ImageFont.truetype("readonly/fanwood-webfont.ttf", size = 20)
#create canvas to write    
    text_image = Image.new("RGB", (650,25), color = "white")
#prepares writing function    
    text = ImageDraw.Draw(text_image)
#Write header text    
    text.text((1, 2), "Results found in file {}".format(key1), font=font, fill = (0,0,0,0)) 
#paste header to canvas
    colage.paste(text_image, (0,0)) 
    return colage

def fill_not_found(image_dict,key1):
#reset canvas    
    collage = 0
#creates new canvas    
    collage = Image.new("RGB", [625,50], color = "white")
#create font
    font = ImageFont.truetype("readonly/fanwood-webfont.ttf", size = 20)
#creates area to write
    text_image2 = Image.new("RGB", (650,50), color = "white")
#prepare text function    
    text2 = ImageDraw.Draw(text_image2)
#write message if names are found but no faces    
    text2.text((1, 2), "Results found in file {}\nBut there were no faces in that file! ".format(key1), font=font, fill = (0,0,0,0)) 
#write on canvas    
    collage.paste(text_image2, (0,0)) 
    return collage

def paste_together(lst):
#sets height to create the canvas to paste all the images    
    height = []
    h_sum = 0
#calculate the height of the main canvas
    for im_spot in range(len(lst)):
        height.append(lst[im_spot].height)
        h_sum +=  lst[im_spot].height
#create main canvas        
    final_image = Image.new("RGB", [625,h_sum])
    y_cd = 0
#paste images    
    for image in range(len(lst)):
        final_image.paste(lst[image], (0,y_cd))
        y_cd += height[image]
    return final_image

def search_for_name_return_image():
#asks for a name to search    
    name = str(input("what name are you searching for?"))
#sets the zip file to use    
    file_path = which_zip_file()
#create the dictionary with images, text and face coordinates    
    image_dict = make_the_image_dictionary(file_path)
#create empty list
    image_list = []
#fill the list eith images    
    for images in image_dict['text']:
        if name in image_dict['text'][images] and len(image_dict['faces_coord'][images]) > 0: 
            image_list.append(fill_colage(image_dict,images))
        if name in image_dict['text'][images] and len(image_dict['faces_coord'][images]) == 0:
            image_list.append(fill_not_found(image_dict,images))
#paste the images on the list on the main canvas            
    final = paste_together(image_list)
    return final

example = search_for_name_return_image()
display(example)
