# libraries to build project:
#    tk-tools
#    python-tkdnd
#    ttkwidgets
#    opencv-python
#    openc-contrib-python
#    auto-py-to-exe

import sys
import os
import tkinter      as tk
import tkinter.font as tkFont
import tkinterDnD
import cv2
import time
from cv2     import dnn_superres
from tkinter import ttk
from tkinter import *
from PIL     import ImageTk, Image
from timeit  import default_timer as timer

# windows dpi
from ctypes import windll 
windll.shcore.SetProcessDpiAwareness(1) 

version     = "0.9.7"
author      = "Annunziata Gianluca"
image_path  = "no file"
AI_model    = "no model"
upscale_factor     = 4
resize_input_image = 1

# ----------- Dimensions -----------

window_width       = 1400
window_height      = 800
left_bar_width     = 400
left_bar_height    = window_height
drag_drop_width    = 1000
drag_drop_height   = window_height
button_width       = 275
button_height      = 35
show_image_width   = 800
show_image_height  = 650
image_text_width   = drag_drop_width * 0.85
image_text_height  = 38

# ----------- /Dimensions -----------

# ----------- Functions -----------

def find_file_production_and_dev(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller "
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def count_dropped_images(event):
    count_png  = 0
    count_PNG  = 0
    count_jpg  = 0
    count_jpeg = 0
    count_webp = 0

    count_png = str(event.data).count('.png') 
    count_PNG = str(event.data).count('.PNG') 
    count_jpg = str(event.data).count('.jpg')
    count_jpeg = str(event.data).count('.jpeg')
    count_webp = str(event.data).count('.webp')

    return count_png + count_PNG + count_jpg + count_jpeg + count_webp

def function_drop(event):
    global image_path
    number_images = count_dropped_images(event)
    if number_images == 0:
        info_string.set("This file is not supported!")
        return
    elif number_images == 1:
        image_path = prepare_image(str(event.data[:]))
        show_image_in_GUI(image_path)
    else:
        info_string.set("Only one image supported!")
        return

def show_image_in_GUI(image_to_show):
    global image
    file_name_string.set(image_to_show)
    
    image  = tk.PhotoImage(file=image_to_show)
    img_label            = tk.Label(root)
    img_label['image']   = image
    img_label["justify"] = "center"
    img_label["bg"]      = "black"
    img_label["relief"]  = "flat"
    img_label.place(x      = left_bar_width + drag_drop_width/2 - show_image_width/2,
                    y      = drag_drop_height/2 - show_image_height/2 - image_text_height,
                    width  = show_image_width,
                    height = show_image_height)

def AI_upscale(image_path, AI_model):
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
        
    super_res           = dnn_superres.DnnSuperResImpl_create()
    upscaled_image_path = image_path.replace(".PNG","").replace(".png","") + "_" + AI_model + "_x" + str(upscale_factor) + ".png"
    
    start     = timer()
    super_res.readModel(path_model)
    
    #super_res.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
    #super_res.setPreferableTarget(cv2.dnn.DNN_TARGET_OPENCL_FP16)
    
    super_res.setModel(model_name, upscale_factor)
    result    = super_res.upsample(cv2.imread(image_path))
    end       = timer()
    
    cv2.imwrite(upscaled_image_path, result)

    return upscaled_image_path, end - start
    
def upscale_command():
    global image_path
    info_string.set("")

    if "no file" in image_path:
        info_string.set("No image selected")
        return
    if "no model" in AI_model:
        info_string.set("No model selected")
        return
    
    upscaled_image_path, comp_time = AI_upscale(image_path, AI_model)
    info_string.set("Done!  " + str(round(comp_time)) + " sec.")
    show_image_in_GUI(upscaled_image_path)
    image_path = "no file"
    
def prepare_image(image_to_modify):
    new_image_path = image_to_modify.replace("{", "").replace("}", "").replace(".PNG",".png").replace(".jpg",".png").replace(".jpeg",".png").replace(".webp",".png").replace(".png", "_resized.png")
    if resize_input_image > 1:
        old_image      = cv2.imread(image_to_modify.replace("{", "").replace("}", ""))
        new_width      = round(old_image.shape[1]/resize_input_image)
        new_height     = round(old_image.shape[0]/resize_input_image)
        resized_image  = cv2.resize(old_image,
                                    (new_width, new_height),
                                    interpolation = cv2.INTER_AREA)
        cv2.imwrite(new_image_path, resized_image)
        return new_image_path
    else:
        old_image      = cv2.imread(image_to_modify.replace("{", "").replace("}", ""))
        cv2.imwrite(new_image_path.replace("_resized.png", ".png"), old_image)
        return new_image_path.replace("_resized.png", ".png")
           
def place_EDSR_button(root, background_color, text_color):
    ft = tkFont.Font(family='Verdana',size=10)
    EDSR_button            = tk.Button(root)
    EDSR_button["anchor"]  = "w"
    EDSR_button["bg"]      = background_color
    EDSR_button["font"]    = ft
    EDSR_button["fg"]      = text_color
    EDSR_button["justify"] = "left"
    EDSR_button["text"]    = " EDSR"
    EDSR_button["relief"]  = "flat"
    EDSR_button.place(x=left_bar_width/2 - button_width/2,y=215,width=button_width,height=button_height)
    EDSR_button["command"] = lambda input = "EDSR" : choose_model_EDSR(input)
    
def place_ESPCN_button(root, background_color, text_color):
    ft = tkFont.Font(family='Verdana',size=10)
    ESPCN_button            = tk.Button(root)
    ESPCN_button["anchor"]  = "w"
    ESPCN_button["bg"]      = background_color
    ESPCN_button["font"]    = ft
    ESPCN_button["fg"]      = text_color
    ESPCN_button["justify"] = "left"
    ESPCN_button["text"]    = " ESPCN"
    ESPCN_button["relief"]  = "flat"
    ESPCN_button.place(x=left_bar_width/2 - button_width/2 ,y=295,width=button_width,height=button_height)
    ESPCN_button["command"] = lambda input = "ESPCN" : choose_model_ESPCN(input)
    
def place_FSRCNN_button(root, background_color, text_color):
    ft = tkFont.Font(family='Verdana',size=10)
    FSRCNN_button            = tk.Button(root)
    FSRCNN_button["anchor"]  = "w"
    FSRCNN_button["bg"]      = background_color
    FSRCNN_button["font"]    = ft
    FSRCNN_button["fg"]      = text_color
    FSRCNN_button["justify"] = "left"
    FSRCNN_button["text"]    = " FSRCNN"
    FSRCNN_button["relief"]  = "flat"
    FSRCNN_button.place(x=left_bar_width/2 - button_width/2,y=375,width=button_width,height=button_height)
    FSRCNN_button["command"] = lambda input = "FSRCNN" : choose_model_FSRCNN(input)
    
def place_LapSRN_button(root, background_color, text_color):
    ft = tkFont.Font(family='Verdana',size=10)
    LapSRN_button            = tk.Button(root)
    LapSRN_button["anchor"]  = "w"
    LapSRN_button["bg"]      = background_color
    LapSRN_button["font"]    = ft
    LapSRN_button["fg"]      = text_color
    LapSRN_button["justify"] = "left"
    LapSRN_button["text"]    = " LapSRN"
    LapSRN_button["relief"]  = "flat"
    LapSRN_button.place(x=left_bar_width/2 - button_width/2,y=455,width=button_width,height=button_height)
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
    
# ---------- /Functions ----------

class App:
    def __init__(self, root):
        root.title("NiceScale " + version + " | Copyright© Gianluca Annunziata")
        width = window_width
        height = window_height
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)
        
        # BIG BLACK BAR
        ft = tkFont.Font(family='Verdana',size=13)

        Left_container            = tk.Label(root)
        Left_container["anchor"]  = "e"
        Left_container["bg"]      = "#000000"
        Left_container["cursor"]  = "arrow"
        Left_container["font"]    = ft
        Left_container["fg"]      = "#333333"
        Left_container["justify"] = "center"
        Left_container["text"]    = ""
        Left_container["relief"]  = "flat"
        Left_container.place(x=0,y=0,width = left_bar_width, height = left_bar_height)
        
        # TITLE - VERSION
        Title            = tk.Label(root)
        Title["bg"]      = "#000000"
        Title["font"]    = ft
        Title["fg"]      = "#1e9fff"
        Title["justify"] = "center"
        Title["text"]    = "NiceScaler " + version
        Title.place(x=0,y=10,width=400,height=62)
        
        ft = tkFont.Font(family='Verdana',size=9)
        Under_title            = tk.Label(root)
        Under_title["bg"]      = "#000000"
        Under_title["font"]    = ft
        Under_title["fg"]      = "#d3d3d3"
        Under_title["justify"] = "center"
        Under_title["text"]    = "upscale x4 every photo you want"
        Under_title.place(x=0,y=55,width=400,height=42)

        # SECTION TO CHOOSE MODEL
        IA_selection_borders            = tk.Label(root)
        IA_selection_borders["bg"]      = "#000000"
        IA_selection_borders["fg"]      = "white"
        IA_selection_borders["justify"] = "center"
        IA_selection_borders["text"]    = ""
        IA_selection_borders["relief"]  = "groove"
        IA_selection_borders.place(x      = left_bar_width/2 - 340/2,
                                   y      = 130,
                                   width  = 340,
                                   height = 440)
        
        ft                            = tkFont.Font(family='Verdana',size=11)        
        IA_selection_title            = tk.Label(root)
        IA_selection_title["bg"]      = "#010000"
        IA_selection_title["font"]    = ft
        IA_selection_title["fg"]      = "#dcdcdc"
        IA_selection_title["justify"] = "center"
        IA_selection_title["text"]    = "Select IA model"
        IA_selection_title.place(x=0,y=150,width=398,height=44)

        default_button_color  = "#484848"
        default_text_color    = "#f2f2f2"
        selected_button_color = "white"
        selected_text_color   = "black"
        
        place_EDSR_button(root, default_button_color, default_text_color)
        place_ESPCN_button(root, default_button_color, default_text_color)
        place_FSRCNN_button(root, default_button_color, default_text_color)
        place_LapSRN_button(root, default_button_color, default_text_color)    

        # LABELS
        ft                   = tkFont.Font(family='Verdana',size=8)
        
        EDSR_label           = tk.Label(root)
        EDSR_label["bg"]     = "#000000"
        EDSR_label["font"]   = ft
        EDSR_label["fg"]     = "#ababab"
        EDSR_label["anchor"] = "w"
        EDSR_label["text"]   = "Accuracy 76% / Really Slow"
        EDSR_label.place(x=80,y=252,width=button_width,height=30)
    
        ESPCN_label           = tk.Label(root)
        ESPCN_label["bg"]     = "#000000"
        ESPCN_label["font"]   = ft
        ESPCN_label["fg"]     = "#ababab"
        ESPCN_label["anchor"] = "w"
        ESPCN_label["text"]   = "Accuracy 73% / Really Fast"
        ESPCN_label.place(x=80,y=332,width=button_width,height=30)
        
        FSRCNN_label           = tk.Label(root)
        FSRCNN_label["bg"]     = "#000000"
        FSRCNN_label["font"]   = ft
        FSRCNN_label["fg"]     = "#ababab"
        FSRCNN_label["anchor"] = "w"
        FSRCNN_label["text"]   = "Accuracy 73% / Really Fast"
        FSRCNN_label.place(x=80,y=412,width=button_width,height=30)

        LapSRN_label           = tk.Label(root)
        LapSRN_label["bg"]     = "#000000"
        LapSRN_label["font"]   = ft
        LapSRN_label["fg"]     = "#ababab"
        LapSRN_label["anchor"] = "w"
        LapSRN_label["text"]   = "Accuracy 73% / Medium speed"
        LapSRN_label.place(x=80,y=492,width=button_width,height=30)
        
        # ERROR MESSAGE
        info_string.set("")
        error_message_label = ttk.Label(root,
                              font       = ("Verdana", 10),
                              textvar    = info_string,
                              relief     = "flat",
                              justify    = "center",
                              background = "black",
                              foreground = "#ffbf00",
                              anchor     = "center")
        error_message_label.place(x      = 0,
                                  y      = 635,
                                  width  = left_bar_width,
                                  height = 30)
        
        # UPSCALE BUTTON
        Upscale_button            = tk.Button(root)
        Upscale_button["bg"]      = "#01aaed"
        ft = tkFont.Font(family   = 'Verdana',size=11)
        Upscale_button["font"]    = ft
        Upscale_button["fg"]      = "#000000"
        Upscale_button["justify"] = "center"
        Upscale_button["text"]    = "Upscale x4"
        Upscale_button["relief"]  = "flat"
        Upscale_button.place(x      = left_bar_width/2 - 350/2,
                             y      = 700,
                             width  = 350,
                             height = 65)
        Upscale_button["command"] = lambda : upscale_command()

        # DRAG & DROP WIDGET
        
        drag_drop = ttk.Label(root,
                              ondrop     = function_drop,
                              relief     = "solid",
                              justify    = "center",
                              background = "#E8E8E8",
                              foreground = "#202020")
        drag_drop.place(x=400,y=0,width = drag_drop_width, height = drag_drop_height)
        
        # FILE NAME
        file_name_string.set('Drop a photo here!')
        drag_drop = ttk.Label(root,
                              font = ("Verdana", 9),
                              textvar = file_name_string,
                              relief  = "solid",
                              justify = "center",
                              background = "#E8E8E8",
                              foreground = "#383838",
                              anchor = "center")
        drag_drop.place(x = left_bar_width + drag_drop_width/2 - image_text_width/2,
                        y = drag_drop_height - image_text_height - 25,
                        width  = image_text_width,
                        height = image_text_height)


if __name__ == "__main__":
    root              = tkinterDnD.Tk()
    file_name_string  = tk.StringVar()
    info_string      = tk.StringVar()
    app               = App(root)
    root.mainloop()
