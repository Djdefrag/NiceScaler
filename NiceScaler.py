from cgitb import text
import threading
import time
import os.path
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

version     = "1.0"
author      = "Annunziata Gianluca"
image_path  = "no file"
AI_model    = "no model"
show_filename_label  = 0
upscale_factor       = 2
resize_input_image   = 1
supported_file_list = [ '.jpg' , '.jpeg',
                        '.png' , '.PNG' ,
                        '.webp', 
                        '.bmp' , 
                        '.tif' , '.tiff']

# ----------- Dimensions -----------

window_width       = 1300
window_height      = 725
left_bar_width     = 400
left_bar_height    = window_height
drag_drop_width    = 900
drag_drop_height   = window_height
button_width       = 280
button_height      = 35
show_image_width   = 700
show_image_height  = 590
image_text_width   = drag_drop_width * 0.90
image_text_height  = 38

button_1_y = 215
button_2_y = 300
button_3_y = 380
button_4_y = 460

label_1_y = 255
label_2_y = 340
label_3_y = 420
label_4_y = 500

# ----------- /Dimensions -----------

# ----------- Functions -----------

def find_file_production_and_dev(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def count_dropped_images(event):
    file_count = 0
    for file_type in supported_file_list:
        file_count = file_count +  str(event.data).count(file_type)
    return file_count

def function_drop(event):
    global image_path
    number_images = count_dropped_images(event)
    if number_images == 0:
        info_string.set("This file is not supported!")
        return
    elif number_images == 1:
        image_path = prepare_image(str(event.data[:]))
        show_image_in_GUI(image_path)
        place_fileName_label(root, image_path)
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
                    y      = drag_drop_height/2 - show_image_height/2 - image_text_height + 5,
                    width  = show_image_width,
                    height = show_image_height)

def AI_upscale_image(image_path, AI_model):
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
    
    super_res.readModel(path_model)
    #super_res.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
    #super_res.setPreferableTarget(cv2.dnn.DNN_TARGET_OPENCL_FP16)
    super_res.setModel(model_name, upscale_factor)
    result    = super_res.upsample(cv2.imread(image_path))
    cv2.imwrite(upscaled_image_path, result)

    return

def wait_for_file(image_path, _ ):
    start     = timer()
    while not os.path.exists(image_path):
        time.sleep(1)

    if os.path.isfile(image_path):
        end       = timer()
        comp_time = end - start
        info_string.set("Done!  " + str(round(comp_time)) + " sec.")

def upscale_button_command():
    global image_path

    if "no file" in image_path:
        info_string.set("No image selected")
        return
    if "no model" in AI_model:
        info_string.set("No model selected")
        return

    info_string.set("Upscaling...")
    thread_upscale = threading.Thread(target=AI_upscale_image, args=(image_path, AI_model), daemon=True)
    thread_upscale.start()

    upscaled_image_path = image_path.replace(".PNG","").replace(".png","") + "_" + AI_model + "_x" + str(upscale_factor) + ".png"
    thread_wait_image = threading.Thread(target=wait_for_file, args=(upscaled_image_path, 0), daemon=True)
    thread_wait_image.start()
    
def prepare_image(image_to_prepare):
    new_image_path = image_to_prepare
    for file_type in supported_file_list:
        new_image_path = new_image_path.replace(file_type,".png")
    new_image_path = new_image_path.replace("{", "").replace("}", "").replace(".png", "_resized.png")
    
    if resize_input_image > 1:
        old_image      = cv2.imread(image_to_prepare.replace("{", "").replace("}", ""))
        new_width      = round(old_image.shape[1]/resize_input_image)
        new_height     = round(old_image.shape[0]/resize_input_image)
        resized_image  = cv2.resize(old_image,
                                    (new_width, new_height),
                                    interpolation = cv2.INTER_AREA)
        cv2.imwrite(new_image_path, resized_image)
        return new_image_path
    else:
        old_image      = cv2.imread(image_to_prepare.replace("{", "").replace("}", ""))
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
    EDSR_button["text"]    = "  EDSR"
    EDSR_button["relief"]  = "flat"
    EDSR_button.place(x = left_bar_width/2 - button_width/2, 
                      y = button_4_y,
                      width  = button_width,
                      height = button_height)
    EDSR_button["command"] = lambda input = "EDSR" : choose_model_EDSR(input)
    
def place_ESPCN_button(root, background_color, text_color):
    ft = tkFont.Font(family='Verdana',size=10)
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
    ft = tkFont.Font(family='Verdana',size=10)
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
    ft = tkFont.Font(family='Verdana',size=10)
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

def place_fileName_label(root, image_path):
    global show_filename_label
    show_filename_label = show_filename_label + 1

    if show_filename_label == 1:
        img      = cv2.imread(image_path.replace("{", "").replace("}", ""))
        width      = round(img.shape[1])
        height     = round(img.shape[0])
        file_name_string.set(image_path + " | " + str(width) + "x" + str(height))
        drag_drop = ttk.Label(root,
                              font = ("Verdana", 9),
                              textvar    = file_name_string,
                              relief     = "flat",
                              justify    = "center",
                              background = "#E0E0E0",
                              foreground = "black",
                              anchor     = "center")
        drag_drop.place(x = left_bar_width + drag_drop_width/2 - image_text_width/2,
                        y = drag_drop_height - image_text_height - 30,
                        width  = image_text_width,
                        height = image_text_height)
    else:
        img      = cv2.imread(image_path.replace("{", "").replace("}", ""))
        width      = round(img.shape[1])
        height     = round(img.shape[0])
        file_name_string.set(image_path + " | " + str(width) + "x" + str(height))

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
        root.title("NiceScale " + version) # + " | Copyright© Gianluca Annunziata")
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
        Left_container["bg"]      = "#000000"
        Left_container["cursor"]  = "arrow"
        Left_container["fg"]      = "#333333"
        Left_container["justify"] = "center"
        Left_container["text"]    = ""
        Left_container["relief"]  = "flat"
        Left_container.place(x=0,y=0,width = left_bar_width, height = left_bar_height)
        
        # TITLE - VERSION
        ft = tkFont.Font(family='Verdana',size=13)
        Title            = tk.Label(root)
        Title["bg"]      = "#000000"
        Title["font"]    = ft
        Title["fg"]      = "#1e9fff"
        Title["anchor"]  = "w" 
        Title["text"]    = "NiceScaler " + version
        Title.place(x = 88,
                    y = 10,
                    width  = left_bar_width,
                    height = 60)
        
        ft = tkFont.Font(family='Verdana',size=9)
        Under_title            = tk.Label(root)
        Under_title["bg"]      = "#000000"
        Under_title["font"]    = ft
        Under_title["fg"]      = "#d3d3d3"
        Under_title["anchor"]  = "w" 
        Under_title["text"]    = "upscale any photo you wish"
        Under_title.place(x = 90,
                          y = 53,
                          width  = left_bar_width,
                          height = 34)

        global logo_big
        logo_big = PhotoImage(file=find_file_production_and_dev("logo4_big.png"))
        logo_label            = tk.Label(root)
        logo_label['image']   = logo_big
        logo_label["justify"] = "center"
        logo_label["bg"]      = "black"
        logo_label["relief"]  = "flat"
        logo_label.place(x    = 26,
                   y      = 31,
                   width  = 45,
                   height = 45)

        # SECTION TO CHOOSE MODEL
        IA_selection_borders            = tk.Label(root)
        IA_selection_borders["bg"]      = "#000000"
        IA_selection_borders["fg"]      = "white"
        IA_selection_borders["justify"] = "center"
        IA_selection_borders["text"]    = ""
        IA_selection_borders["relief"]  = "groove"
        IA_selection_borders.place(x      = left_bar_width/2 - 350/2,
                                   y      = 125,
                                   width  = 350,
                                   height = 442)
        
        ft                            = tkFont.Font(family='Verdana',size=12)        
        IA_selection_title            = tk.Label(root)
        IA_selection_title["bg"]      = "#010000"
        IA_selection_title["font"]    = ft
        IA_selection_title["fg"]      = "#dcdcdc"
        IA_selection_title["anchor"]  = "w" 
        IA_selection_title["text"]    = "          Select IA model"
        IA_selection_title.place(x=0,y=150,width=400,height=40)

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
        ft                   = tkFont.Font(family='Verdana',size=9)
        
        EDSR_label           = tk.Label(root)
        EDSR_label["bg"]     = "#000000"
        EDSR_label["font"]   = ft
        EDSR_label["fg"]     = "#FF4433"
        EDSR_label["anchor"] = "w"
        EDSR_label["text"]   = "Accuracy 88.5% / really slow"
        EDSR_label.place(x = 75,
                         y = label_4_y,
                         width  = button_width,
                         height = 31)
    
        ESPCN_label           = tk.Label(root)
        ESPCN_label["bg"]     = "#000000"
        ESPCN_label["font"]   = ft
        ESPCN_label["fg"]     = "#ababab"
        ESPCN_label["anchor"] = "w"
        ESPCN_label["text"]   = "Accuracy 87.7% / really fast"
        ESPCN_label.place(x = 75, 
                          y = label_2_y,
                          width  = button_width,
                          height = 31)
        
        FSRCNN_label           = tk.Label(root)
        FSRCNN_label["bg"]     = "#000000"
        FSRCNN_label["font"]   = ft
        FSRCNN_label["fg"]     = "#50C878"
        FSRCNN_label["anchor"] = "w"
        FSRCNN_label["text"]   = "Accuracy 87.6% / really fast"
        FSRCNN_label.place(x = 75,
                           y = label_1_y,
                           width  = button_width,
                           height = 31)

        LapSRN_label           = tk.Label(root)
        LapSRN_label["bg"]     = "#000000"
        LapSRN_label["font"]   = ft
        LapSRN_label["fg"]     = "#ababab"
        LapSRN_label["anchor"] = "w"
        LapSRN_label["text"]   = "Accuracy 87.4% / slow"
        LapSRN_label.place(x = 75,
                           y = label_3_y,
                           width  = button_width,
                           height = 31)
        
        # MESSAGE
        info_string.set("")
        error_message_label = ttk.Label(root,
                              font       = ("Verdana", 9),
                              textvar    = info_string,
                              relief     = "flat",
                              justify    = "center",
                              background = "black",
                              foreground = "#ffbf00",
                              anchor     = "center")
        error_message_label.place(x      = 0,
                                  y      = 600,
                                  width  = left_bar_width,
                                  height = 30)
        
        # UPSCALE BUTTON
        Upscale_button            = tk.Button(root)
        Upscale_button["bg"]      = "#01aaed"
        ft = tkFont.Font(family   = 'Verdana',size=11)
        Upscale_button["font"]    = ft
        Upscale_button["fg"]      = "#000000"
        Upscale_button["justify"] = "center"
        Upscale_button["text"]    = "Upscale x2"
        Upscale_button["relief"]  = "flat"
        Upscale_button.place(x      = left_bar_width/2 - button_width/2,
                             y      = left_bar_height - 50 - 50/2,
                             width  = button_width,
                             height = 50)
        Upscale_button["command"] = lambda : upscale_button_command()

        # DRAG & DROP WIDGET
        drag_drop = ttk.Label(root,
                              text    = "Drop an image here",
                              ondrop     = function_drop,
                              font       = ("Verdana", 11),
                              anchor     = "center",
                              relief     = "solid",
                              justify    = "center",
                              background = "#F5F5F5",
                              foreground = "#505050")
        drag_drop.place(x=400,y=0,width = drag_drop_width, height = drag_drop_height)






if __name__ == "__main__":
    root              = tkinterDnD.Tk()
    file_name_string  = tk.StringVar()
    info_string       = tk.StringVar()
    app               = App(root)
    root.mainloop()
