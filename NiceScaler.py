try:
    import pyi_splash
    pyi_splash.close()
except:
    pass

import threading
import multiprocessing
import time
import os.path
import sys
import os
import tkinter      as tk
import tkinter.font as tkFont
from typing_extensions import Self
import tkinterDnD
import cv2
import time
from cv2     import dnn_superres
from tkinter import ttk
from tkinter import *
from PIL     import ImageTk, Image
from timeit  import default_timer as timer
import webbrowser
import ctypes
import win32api
import win32gui
import win32.lib.win32con as win32con
from ctypes.wintypes import HWND

ctypes.windll.shcore.SetProcessDpiAwareness(True)
scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100

if scaleFactor == 1.0:
    font_scale = 1.25
elif scaleFactor == 1.25:
    font_scale = 1.0
else:
    font_scale = 0.8

version    = "1.1.0"
author     = "Annunziata Gianluca"
paypalme   = "https://www.paypal.com/paypalme/jjstd/5"

image_path     = "no file"
AI_model       = "no model"
actual_step    = ""
want_to_stop   = False
multiple_files = False
multi_img_list = []

supported_file_list = [ '.jpg' , '.jpeg',
                        '.png' , '.PNG' ,
                        '.webp', 
                        '.bmp' , 
                        '.tif' , '.tiff']

resize_input_image   = 1
upscale_factor       = 2

# ---------------------- Dimensions ----------------------

window_width       = 1300
window_height      = 725
left_bar_width     = 420
left_bar_height    = window_height
drag_drop_width    = window_width - left_bar_width
drag_drop_height   = window_height
button_width       = 275
button_height      = 35
show_image_width   = drag_drop_width * 0.9
show_image_height  = drag_drop_width * 0.7
image_text_width   = drag_drop_width * 0.9
image_text_height  = 34
button_1_y = 185
button_2_y = 267
button_3_y = 349
button_4_y = 431
label_1_y  = 225
label_2_y  = 307
label_3_y  = 389
label_4_y  = 471
drag_drop_background = "#303030"
drag_drop_text_color = "#808080"

# ---------------------- /Dimensions ----------------------

# ---------------------- Functions ----------------------

def prepare_opencv_superresolution_model_CPU(AI_model):
    if "EDSR" in AI_model:
        model_name = "edsr"
        path_model = find_file_production_and_dev("EDSR_x" + str(upscale_factor)+".pb")
    elif "ESPCN" in AI_model:
        model_name = "espcn"
        path_model = find_file_production_and_dev("ESPCN_x" + str(upscale_factor)+".pb")
    elif "FSRCNN" in AI_model:
        model_name = "fsrcnn"
        path_model = find_file_production_and_dev("FSRCNN_x" + str(upscale_factor)+".pb")
    elif "LapSRN" in AI_model:
        model_name = "lapsrn"
        path_model = find_file_production_and_dev("LapSRN_x" + str(upscale_factor)+".pb")
        
    super_res = dnn_superres.DnnSuperResImpl_create()
    super_res.readModel(path_model)
    super_res.setModel(model_name, upscale_factor)

    return super_res

def prepare_opencv_superresolution_model_CUDA(AI_model):
    if "EDSR" in AI_model:
        model_name = "edsr"
        path_model = find_file_production_and_dev("EDSR_x" + str(upscale_factor)+".pb")
    elif "ESPCN" in AI_model:
        model_name = "espcn"
        path_model = find_file_production_and_dev("ESPCN_x" + str(upscale_factor)+".pb")
    elif "FSRCNN" in AI_model:
        model_name = "fsrcnn"
        path_model = find_file_production_and_dev("FSRCNN_x" + str(upscale_factor)+".pb")
    elif "LapSRN" in AI_model:
        model_name = "lapsrn"
        path_model = find_file_production_and_dev("LapSRN_x" + str(upscale_factor)+".pb")
        
    super_res = dnn_superres.DnnSuperResImpl_create()
    super_res.readModel(path_model)
    super_res.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
    super_res.setPreferableTarget(cv2.dnn.DNN_TARGET_OPENCL_FP16)
    super_res.setModel(model_name, upscale_factor)

    return super_res

def find_file_production_and_dev(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def function_drop(event):
    global image_path
    global multiple_files
    global multi_img_list
    info_string.set("")

    all_supported, multiple_files = count_images_and_check_incompatibility(event)
    if all_supported == False:
        if multiple_files:
            info_string.set("Some files are not supported!")
            return
        else:
            info_string.set("This file is not supported!")
            return
    else:
        if multiple_files:
            image_list_dropped             = from_string_to_image_list(event)
            image_list_filenames_converted = convert_only_image_filenames(image_list_dropped)
            thread_convert_images          = threading.Thread(target = convert_and_resize_multi_images, 
                                                              args   = (image_list_dropped, 1), 
                                                              daemon  = True)
            thread_convert_images.start()
            show_list_images_in_GUI_with_drag_drop(image_list_filenames_converted) 
            multi_img_list = image_list_filenames_converted
        else:
            # one image only
            multiple_files = False
            image_path = convert_and_resize_single_image(str(event.data))
            show_image_in_GUI_with_drag_drop(image_path)
            place_fileName_label(image_path)
   
def count_images_and_check_incompatibility(event):
    supported_file_dropped_number = 0
    all_file_dropped       = 0
    multiple_files         = False
    all_supported          = False

    # count compatible file
    for file_type in supported_file_list:
        supported_file_dropped_number = supported_file_dropped_number + str(event.data).count(file_type)
    
    # count all files dropped
    all_file_dropped = all_file_dropped + str(event.data).count(".")
    
    if supported_file_dropped_number == all_file_dropped:
        all_supported = True
    if supported_file_dropped_number > 1:
        multiple_files = True    
    
    return all_supported, multiple_files

def process_OpenCV_AI_upscale_image(image_path, AI_model):
    if "EDSR" in AI_model:
        model_name = "edsr"
        path_model = find_file_production_and_dev("EDSR_x" + str(upscale_factor)+".pb")
    elif "ESPCN" in AI_model:
        model_name = "espcn"
        path_model = find_file_production_and_dev("ESPCN_x" + str(upscale_factor)+".pb")
    elif "FSRCNN" in AI_model:
        model_name = "fsrcnn"
        path_model = find_file_production_and_dev("FSRCNN_x" + str(upscale_factor)+".pb")
    elif "LapSRN" in AI_model:
        model_name = "lapsrn"
        path_model = find_file_production_and_dev("LapSRN_x" + str(upscale_factor)+".pb")
        
    super_res = prepare_opencv_superresolution_model_CPU(AI_model)
    result    = super_res.upsample(cv2.imread(image_path))
    upscaled_image_path = image_path.replace(".PNG","").replace(".png","") + "_" + AI_model + "_x" + str(upscale_factor) + ".png"
    cv2.imwrite(upscaled_image_path, result)

def process_OpenCV_AI_upscale_multiple_images(image_list, AI_model):
    for image in image_list:
        super_res   = prepare_opencv_superresolution_model_CPU(AI_model)
        result_path = image.replace(".PNG","").replace(".png","") + "_" + AI_model + "_x" + str(upscale_factor) + ".png"
        result      = super_res.upsample(cv2.imread(image))
        cv2.imwrite(result_path, result)
    
def thread_wait_for_single_file(image_path, _ ):
    start     = timer()
    while not os.path.exists(image_path):
        time.sleep(1)

    if os.path.isfile(image_path):
        end       = timer()
        info_string.set("Upscale completed [" + str(round(end - start)) + " sec.]")
        place_upscale_button()
        return

def thread_wait_for_multiple_file(image_list, AI_model, upscale_factor):
    start     = timer()

    how_many_images = len(image_list)
    counter_done = 0
    for image in image_list:
        while not os.path.exists(image.replace(".png","") + "_" + AI_model + "_x" + str(upscale_factor) + ".png"):
            time.sleep(1)

        if os.path.isfile(image.replace(".png","") + "_" + AI_model + "_x" + str(upscale_factor) + ".png"):
            counter_done += 1

        if counter_done == how_many_images:    
            end       = timer()
            info_string.set("Upscale completed [" + str(round(end - start)) + " sec.]")
            place_upscale_button()
            return

def upscale_button_command():
    global image_path
    global multiple_files
    global actual_step
    global want_to_stop 
    global process_multi_upscale
    global process_single_upscale

    want_to_stop = False

    if "no model" in AI_model:
        info_string.set("No AI model selected!")
        return

    if multiple_files:
        if "converting" in actual_step:
            info_string.set("Waiting for images conversion...")
            return
        elif "ready"    in actual_step:
            info_string.set("Upscaling multiple images...")
            place_stop_button()

            process_multi_upscale = multiprocessing.Process(target = process_OpenCV_AI_upscale_multiple_images, 
                                                            args   = (multi_img_list, AI_model))
            process_multi_upscale.start()

            thread_wait_multi = threading.Thread(target = thread_wait_for_multiple_file, 
                                                 args   = (multi_img_list, AI_model, upscale_factor),
                                                 daemon = True)
            thread_wait_multi.start()

    elif "no file" in image_path:
        info_string.set("No image selected!")

    else:
        place_stop_button()
        info_string.set("Upscaling single image...")
        process_single_upscale = multiprocessing.Process(target = process_OpenCV_AI_upscale_image, 
                                                         args   = (image_path, AI_model))
        process_single_upscale.start()

        thread_wait = threading.Thread(target = thread_wait_for_single_file, 
                                       args   = (image_path.replace(".png","") + "_" + AI_model + "_x" + str(upscale_factor) + ".png", 1 ), 
                                       daemon = True)
        thread_wait.start()

def stop_button_command():
    global process_multi_upscale
    global process_single_upscale
    global want_to_stop
    
    want_to_stop = True

    try:
        process_multi_upscale.terminate()
    except:
        process_single_upscale.terminate()

    info_string.set("Upscaling stopped")
    place_upscale_button()

def from_string_to_image_list(event):
    image_list = str(event.data).replace("{", "").replace("}", "")
    
    for file_type in supported_file_list:
        image_list = image_list.replace(file_type, file_type+"\n")

    image_list = image_list.split("\n")
    image_list.pop() # to remove last void element

    return image_list

def convert_only_image_filenames(image_list):
    list_converted = []
    for image in image_list:
        image = image.strip().replace("{", "").replace("}", "")
        for file_type in supported_file_list:
            image = image.replace(file_type,".png")
        if resize_input_image > 1:
            image = image.replace(".png", "_resized.png")
        
        list_converted.append(image)

    return list(dict.fromkeys(list_converted))
    
def convert_and_resize_multi_images(image_list, _ ):
    global multiple_files
    global actual_step

    multiple_files = True
    actual_step    = "converting"
    info_string.set("Converting images...")
    
    for image in image_list:
        image = image.strip()
        image_prepared = convert_and_resize_single_image(image)
    
    actual_step    = "ready"
    info_string.set("")

def convert_and_resize_single_image(image_to_prepare):
    if ".png" in image_to_prepare:
        return image_to_prepare.replace("{", "").replace("}", "")
    else:
        image_to_prepare = image_to_prepare.replace("{", "").replace("}", "")
        new_image_path = image_to_prepare
        
        for file_type in supported_file_list:
            new_image_path = new_image_path.replace(file_type,".png")
        
        if resize_input_image > 1:
            old_image      = cv2.imread(image_to_prepare)
            new_width      = round(old_image.shape[1]/resize_input_image)
            new_height     = round(old_image.shape[0]/resize_input_image)
            resized_image  = cv2.resize(old_image,
                                        (new_width, new_height),
                                        interpolation = cv2.INTER_AREA)
            cv2.imwrite(new_image_path.replace(".png", "_resized.png"), resized_image)
            return new_image_path.replace(".png", "_resized.png")
        else:
            old_image      = cv2.imread(image_to_prepare.replace("{", "").replace("}", ""))
            cv2.imwrite(new_image_path, old_image)
            return new_image_path

# ---------------------- GUI related ---------------------- 

def openpaypal():
    webbrowser.open(paypalme,new=1)

def clear_drag_drop_background():
    drag_drop = ttk.Label(root,
                          ondrop     = function_drop,
                          relief     = "flat",
                          background = drag_drop_background,
                          foreground = drag_drop_text_color)
    drag_drop.place(x=left_bar_width, y=0, width = drag_drop_width, height = drag_drop_height)

def show_list_images_in_GUI_with_drag_drop(image_list_prepared):

    clear_drag_drop_background()
    
    final_string = "\n"
    counter_img = 0
    for elem in image_list_prepared:
        counter_img += 1
        if counter_img <= 20:
            # add first 20 files in list
            final_string +=  elem.strip() + "\n"
        else:
            # if files > 20 stop list and add ...
            final_string +=  "and others... \n"
            break

    list_height = 420
    list_width  = 750
    
    list_header = ttk.Label(root,
                            text       = "Image list",
                            ondrop     = function_drop,
                            font       = ("Verdana", round(11 * font_scale)), #11
                            anchor     = "center",
                            relief     = "flat",
                            justify    = "center",
                            background = "#181818",
                            foreground = "#D3D3D3")
    list_header.place(x = left_bar_width + drag_drop_width/2 - list_width/2,
                               y = drag_drop_height/2 - list_height/2 - 45,
                               width  = 200,
                               height = 35)

    multiple_images_list = ttk.Label(root,
                            text       = final_string,
                            ondrop     = function_drop,
                            font       = ("Verdana", round(9 * font_scale)), #9
                            anchor     = "n",
                            relief     = "flat",
                            justify    = "left",
                             background = "#181818",
                            foreground = "#D3D3D3",
                            wraplength = list_width - 10)
    multiple_images_list.place(x = left_bar_width + drag_drop_width/2 - list_width/2,
                               y = drag_drop_height/2 - list_height/2,
                               width  = list_width,
                               height = list_height)

    # then image counter
    multiple_images_label = ttk.Label(root,
                            text       = " Images loaded " + str(len(image_list_prepared)),
                            ondrop     = function_drop,
                            font       = ("Verdana", round(11 * font_scale)),
                            anchor     = "center",
                            relief     = "flat",
                            justify    = "center",
                            background = "#181818",
                            foreground = "#D3D3D3")
    multiple_images_label.place(x = left_bar_width + drag_drop_width/2 - 400/2,
                         y = drag_drop_height/2 + 500/2 + 25,
                         width  = 400,
                         height = 42)

def show_image_in_GUI_with_drag_drop(image_to_show):
    global image
    clear_drag_drop_background()

    image  = tk.PhotoImage(file=image_to_show)
    drag_drop_and_images = ttk.Label(root,
                            text    = "",
                            image   = image,
                            ondrop     = function_drop,
                            font       = ("Verdana",round(10 * font_scale)),
                            anchor     = "center",
                            relief     = "flat",
                            justify    = "center",
                            background = drag_drop_background,
                            foreground = "#202020")
    drag_drop_and_images.place(x      = left_bar_width + drag_drop_width/2 - show_image_width/2,
                               y      = drag_drop_height/2 - show_image_height/2 - image_text_height+1,
                               width  = show_image_width,
                               height = show_image_height)
        
def place_fileName_label(image_path):
    img      = cv2.imread(image_path.replace("{", "").replace("}", ""))
    width      = round(img.shape[1])
    height     = round(img.shape[0])
    file_name_string.set(image_path + " | [" + str(width) + "x" + str(height) + "]")
    drag_drop = ttk.Label(root,
                            font = ("Verdana", round(9 * font_scale)),
                            textvar    = file_name_string,
                            relief     = "flat",
                            justify    = "center",
                            background = "#181818",
                            foreground = "#D3D3D3",
                            anchor     = "center")

                            
    drag_drop.place(x = left_bar_width + drag_drop_width/2 - image_text_width/2,
                    y = drag_drop_height - image_text_height - 22,
                    width  = image_text_width,
                    height = image_text_height)

# ---------------------- Buttons ----------------------

def place_upscale_button():
    # UPSCALE BUTTON
    Upscale_button            = tk.Button(root)
    Upscale_button["bg"]      = "#01aaed"
    ft = tkFont.Font(family   = 'Verdana', size = round(11 * font_scale))
    Upscale_button["font"]    = ft
    Upscale_button["fg"]      = "#202020"
    Upscale_button["justify"] = "center"
    Upscale_button["text"]    = "Upscale x2"
    Upscale_button["relief"]  = "flat"
    Upscale_button.place(x      = left_bar_width/2 - button_width/2,
                         y      = left_bar_height - 50 - 25/2,
                         width  = button_width + 12,
                         height = 42)
    Upscale_button["command"] = lambda : upscale_button_command()

def place_stop_button():
    # UPSCALE BUTTON
    Upscale_button            = tk.Button(root)
    Upscale_button["bg"]      = "#FF4433"
    ft = tkFont.Font(family   = 'Verdana', size = round(11 * font_scale))
    Upscale_button["font"]    = ft
    Upscale_button["fg"]      = "#202020"
    Upscale_button["justify"] = "center"
    Upscale_button["text"]    = "[x] Stop upscaling"
    Upscale_button["relief"]  = "flat"
    Upscale_button.place(x      = left_bar_width/2 - button_width/2,
                         y      = left_bar_height - 50 - 25/2,
                         width  = button_width + 12,
                         height = 42)
    Upscale_button["command"] = lambda : stop_button_command()

def place_EDSR_button(root, background_color, text_color):
    ft = tkFont.Font(family   = 'Verdana', size = round(10 * font_scale))
    EDSR_button            = tk.Button(root)
    EDSR_button["anchor"]  = "w"
    EDSR_button["bg"]      = background_color
    EDSR_button["font"]    = ft
    EDSR_button["fg"]      = text_color
    EDSR_button["justify"] = "left"
    EDSR_button["text"]    = "  EDSR"
    EDSR_button["relief"]  = "flat"
    EDSR_button.place(x = left_bar_width/2 - button_width/2, 
                      y = button_4_y,
                      width  = button_width,
                      height = button_height)
    EDSR_button["command"] = lambda input = "EDSR" : choose_model_EDSR(input)
    
def place_ESPCN_button(root, background_color, text_color):
    ft = tkFont.Font(family   = 'Verdana', size = round(10 * font_scale))
    ESPCN_button            = tk.Button(root)
    ESPCN_button["anchor"]  = "w"
    ESPCN_button["bg"]      = background_color
    ESPCN_button["font"]    = ft
    ESPCN_button["fg"]      = text_color
    ESPCN_button["justify"] = "left"
    ESPCN_button["text"]    = "  ESPCN"
    ESPCN_button["relief"]  = "flat"
    ESPCN_button.place(x = left_bar_width/2 - button_width/2 ,
                       y = button_2_y,
                       width  = button_width,
                       height = button_height)
    ESPCN_button["command"] = lambda input = "ESPCN" : choose_model_ESPCN(input)
    
def place_FSRCNN_button(root, background_color, text_color):
    ft = tkFont.Font(family   = 'Verdana', size = round(10 * font_scale))
    FSRCNN_button            = tk.Button(root)
    FSRCNN_button["anchor"]  = "w"
    FSRCNN_button["bg"]      = background_color
    FSRCNN_button["font"]    = ft
    FSRCNN_button["fg"]      = text_color
    FSRCNN_button["justify"] = "left"
    FSRCNN_button["text"]    = "  FSRCNN"
    FSRCNN_button["relief"]  = "flat"
    FSRCNN_button.place(x = left_bar_width/2 - button_width/2,
                        y = button_1_y,
                        width  = button_width,
                        height = button_height)
    FSRCNN_button["command"] = lambda input = "FSRCNN" : choose_model_FSRCNN(input)
    
def place_LapSRN_button(root, background_color, text_color):
    ft = tkFont.Font(family   = 'Verdana', size = round(10 * font_scale))
    LapSRN_button            = tk.Button(root)
    LapSRN_button["anchor"]  = "w"
    LapSRN_button["bg"]      = background_color
    LapSRN_button["font"]    = ft
    LapSRN_button["fg"]      = text_color
    LapSRN_button["justify"] = "left"
    LapSRN_button["text"]    = "  LapSRN"
    LapSRN_button["relief"]  = "flat"
    LapSRN_button.place(x = left_bar_width/2 - button_width/2,
                        y = button_3_y,
                        width  = button_width,
                        height = button_height)
    LapSRN_button["command"] = lambda input = "LapSRN" : choose_model_LapSRN(input)

def choose_model_EDSR(choosed_model):
    global AI_model
    AI_model = choosed_model
    
    default_button_color  = "#484848"
    default_text_color    = "#f2f2f2"
    selected_button_color = "white"
    selected_text_color   = "black"
    
    place_EDSR_button(root, selected_button_color, selected_text_color) # changing
    place_ESPCN_button(root, default_button_color, default_text_color)
    place_FSRCNN_button(root, default_button_color, default_text_color)
    place_LapSRN_button(root, default_button_color, default_text_color) 
    
def choose_model_ESPCN(choosed_model):
    global AI_model
    AI_model = choosed_model
    
    default_button_color  = "#484848"
    default_text_color    = "#f2f2f2"
    selected_button_color = "white"
    selected_text_color   = "black"
    
    place_EDSR_button(root, default_button_color, default_text_color)
    place_ESPCN_button(root, selected_button_color, selected_text_color) # changing
    place_FSRCNN_button(root, default_button_color, default_text_color)
    place_LapSRN_button(root, default_button_color, default_text_color)

def choose_model_FSRCNN(choosed_model):
    global AI_model
    AI_model = choosed_model
    
    default_button_color  = "#484848"
    default_text_color    = "#f2f2f2"
    selected_button_color = "white"
    selected_text_color   = "black"
    
    place_EDSR_button(root, default_button_color, default_text_color)
    place_ESPCN_button(root, default_button_color, default_text_color)
    place_FSRCNN_button(root, selected_button_color, selected_text_color) # changing
    place_LapSRN_button(root, default_button_color, default_text_color)

def choose_model_LapSRN(choosed_model):
    global AI_model
    AI_model = choosed_model
    
    default_button_color  = "#484848"
    default_text_color    = "#f2f2f2"
    selected_button_color = "white"
    selected_text_color   = "black"
    
    place_EDSR_button(root, default_button_color, default_text_color)
    place_ESPCN_button(root, default_button_color, default_text_color)
    place_FSRCNN_button(root, default_button_color, default_text_color)
    place_LapSRN_button(root, selected_button_color, selected_text_color) # changing

# ---------------------- /Buttons ----------------------

# ---------------------- /GUI related ---------------------- 

# ---------------------- /Functions ----------------------

class App:
    def __init__(self, root):
        root.title("   NiceScaler " + version) # + " | Copyright© Gianluca Annunziata")
        width        = window_width
        height       = window_height
        screenwidth  = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr     = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        logo = PhotoImage(file=find_file_production_and_dev("logo4.png"))
        root.iconphoto(False, logo)

        # BIG BLACK BAR
        Left_container            = tk.Label(root)
        Left_container["anchor"]  = "e"
        Left_container["bg"]      = "#202020"
        Left_container["cursor"]  = "arrow"
        Left_container["fg"]      = "#333333"
        Left_container["justify"] = "center"
        Left_container["text"]    = ""
        Left_container["relief"]  = "flat"
        Left_container.place(x=0,y=0,width = left_bar_width, height = left_bar_height)
        
        # TITLE
        ft = tkFont.Font(family='Verdana', size = round(14 * font_scale)),
        Title            = tk.Label(root)
        Title["bg"]      = "#202020"
        Title["font"]    = ft
        Title["fg"]      = "#1e9fff"
        Title["anchor"]  = "w" 
        Title["text"]    = "  NiceScaler "
        Title.place(x = 88,
                    y = 20,
                    width  = left_bar_width,
                    height = 60)
        
        ft = tkFont.Font(family='Verdana',size = round(9 * font_scale)),
        Under_title            = tk.Label(root)
        Under_title["bg"]      = "#202020"
        Under_title["font"]    = ft
        Under_title["fg"]      = "#d3d3d3"
        Under_title["anchor"]  = "w" 
        Under_title["text"]    = "   upscale any photo you wish"
        Under_title.place(x = 90,
                          y = 60,
                          width  = left_bar_width,
                          height = 34)

        global logo_big
        logo_big = PhotoImage(file=find_file_production_and_dev("logo4_big.png"))
        logo_label            = tk.Label(root)
        logo_label['image']   = logo_big
        logo_label["justify"] = "center"
        logo_label["bg"]      = "#202020"
        logo_label["relief"]  = "flat"
        logo_label.place(x    = 40,
                   y      = 40,
                   width  = 45,
                   height = 45)

        global logo_paypal
        logo_paypal = PhotoImage(file=find_file_production_and_dev("paypal35.png"))
        logo_paypal_label            = tk.Button(root)
        logo_paypal_label['image']   = logo_paypal
        logo_paypal_label["justify"] = "center"
        logo_paypal_label["bg"]      = "#202020"
        logo_paypal_label["relief"]  = "flat"
        logo_paypal_label["activebackground"]    = "grey"
        logo_paypal_label["borderwidth"]  = 1
        logo_paypal_label.place(x    = left_bar_width - 70,
                   y      = 45,
                   width  = 35,
                   height = 35)
        logo_paypal_label["command"] = lambda : openpaypal()

        # SECTION TO CHOOSE MODEL
        IA_selection_borders              = tk.Label(root)
        IA_selection_borders["bg"]        = "#181818"
        IA_selection_borders["justify"]   = "center"
        IA_selection_borders["relief"]    = "flat"
        IA_selection_borders.place(x      = left_bar_width/2 - 350/2,
                                   y      = 127,
                                   width  = 350,
                                   height = 392)
        
        ft                            = tkFont.Font(family='Verdana',size = round(11 * font_scale))        
        IA_selection_title            = tk.Label(root)
        IA_selection_title["bg"]      = "#181818"
        IA_selection_title["font"]    = ft
        IA_selection_title["fg"]      = "#F0F0F0" 	
        IA_selection_title["anchor"]  = "center" 
        IA_selection_title["justify"] = "center"
        IA_selection_title["relief"]  = "flat"
        IA_selection_title["text"]    = "AI models"
        IA_selection_title.place(x      = left_bar_width/2 - 174,
                                 y      = 127,
                                 width  = 348,
                                 height = 40)

        # buttons
        default_button_color  = "#484848"
        default_text_color    = "#f2f2f2"
        selected_button_color = "white"
        selected_text_color   = "black"
        
        place_EDSR_button(root, default_button_color, default_text_color)
        place_ESPCN_button(root, default_button_color, default_text_color)
        place_FSRCNN_button(root, default_button_color, default_text_color)
        place_LapSRN_button(root, default_button_color, default_text_color)    

        # LABELS
        ft                   = tkFont.Font(family='Verdana', size = round(9 * font_scale))
        
        EDSR_label           = tk.Label(root)
        EDSR_label["bg"]     = "#181818"
        EDSR_label["font"]   = ft
        EDSR_label["fg"]     = "#FF4433"
        EDSR_label["anchor"] = "w"
        EDSR_label["text"]   = "Accuracy 88.5% / really slow"
        EDSR_label.place(x = 85,
                         y = label_4_y,
                         width  = button_width,
                         height = 31)
    
        ESPCN_label           = tk.Label(root)
        ESPCN_label["bg"]     = "#181818"
        ESPCN_label["font"]   = ft
        ESPCN_label["fg"]     = "#ababab"
        ESPCN_label["anchor"] = "w"
        ESPCN_label["text"]   = "Accuracy 87.7% / really fast"
        ESPCN_label.place(x = 85, 
                          y = label_2_y,
                          width  = button_width,
                          height = 31)
        
        FSRCNN_label           = tk.Label(root)
        FSRCNN_label["bg"]     = "#181818"
        FSRCNN_label["font"]   = ft
        FSRCNN_label["fg"]     = "#50C878"
        FSRCNN_label["anchor"] = "w"
        FSRCNN_label["text"]   = "Accuracy 87.6% / really fast"
        FSRCNN_label.place(x = 85,
                           y = label_1_y,
                           width  = button_width,
                           height = 31)

        LapSRN_label           = tk.Label(root)
        LapSRN_label["bg"]     = "#181818"
        LapSRN_label["font"]   = ft
        LapSRN_label["fg"]     = "#ababab"
        LapSRN_label["anchor"] = "w"
        LapSRN_label["text"]   = "Accuracy 87.4% / slow"
        LapSRN_label.place(x = 85,
                           y = label_3_y,
                           width  = button_width,
                           height = 31)
        
        # MESSAGE
        info_string.set("")
        error_message_label = ttk.Label(root,
                              font       = ("Verdana", round(9 * font_scale)),
                              textvar    = info_string,
                              relief     = "flat",
                              justify    = "center",
                              background = "#202020",
                              foreground = "#ffbf00",
                              anchor     = "center")
        error_message_label.place(x      = 0,
                                  y      = 620,
                                  width  = left_bar_width,
                                  height = 30)
        
        # UPSCALE BUTTON
        place_upscale_button()

        # DRAG & DROP WIDGET
        drag_drop = ttk.Label(root,
                              text    = " Drop single image / multiple images here \n\n jpg / png / tif / bmp / webp \n\n thank you for supporting this project :)",
                              ondrop     = function_drop,
                              font       = ("Verdana", round(12 * font_scale)),
                              anchor     = "center",
                              relief     = "flat",
                              justify    = "center",
                              background = drag_drop_background,
                              foreground = drag_drop_text_color)
        drag_drop.place(x=left_bar_width,y=0,width = drag_drop_width, height = drag_drop_height)

        root.update()
        DWMWA_USE_IMMERSIVE_DARK_MODE = 19
        hwnd                 = ctypes.windll.user32.GetParent(root.winfo_id())
        rendering_policy     = DWMWA_USE_IMMERSIVE_DARK_MODE
        value                = ctypes.c_int(2)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))

if __name__ == "__main__":
    multiprocessing.freeze_support()
    root              = tkinterDnD.Tk()
    file_name_string  = tk.StringVar()
    info_string       = tk.StringVar()
    app               = App(root)
    root.update()
    root.mainloop()
