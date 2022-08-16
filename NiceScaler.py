import ctypes
import multiprocessing
import os
import os.path
import platform
import shutil
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkFont
import webbrowser
from timeit import default_timer as timer
from tkinter import *
from tkinter import ttk

import cv2
import moviepy.video.io.ImageSequenceClip
import tkinterDnD
from cv2 import dnn_superres
from win32mica import MICAMODE, ApplyMica

import sv_ttk

global app_name
app_name = "NiceScaler"
version  = "2.3"

image_path            = "no file"
AI_model              = "FSRCNN"
device                = "GPU"
input_video_path      = ""
target_file_extension = '.jpg'
windows_subversion    = int(platform.version().split('.')[2])
upscale_factor        = 2
tiles_resolution      = 1000
single_file           = False
multiple_files        = False
video_files           = False
multi_img_list        = []
video_frames_list     = []
video_frames_upscaled_list = []

paypalme           = "https://www.paypal.com/paypalme/jjstd/5"
githubme           = "https://github.com/Djdefrag/QualityScaler"
patreonme          = "https://www.patreon.com/Djdefrag"

default_font          = 'Segoe UI'
background_color      = "#181818"
window_width          = 1300
window_height         = 725
left_bar_width        = 410
left_bar_height       = window_height
drag_drop_width       = window_width - left_bar_width
drag_drop_height      = window_height
show_image_width      = drag_drop_width * 0.8
show_image_height     = drag_drop_width * 0.6
image_text_width      = drag_drop_width * 0.8
support_button_height = 95 
button_1_y            = 240
button_2_y            = 340
button_3_y            = 440
button_4_y            = 540
text_color            = "#DCDCDC"
selected_button_color = "#ffbf00"

supported_file_list     = ['.jpg', '.jpeg', '.JPG', '.JPEG',
                            '.png', '.PNG',
                            '.webp', '.WEBP',
                            '.bmp', '.BMP',
                            '.tif', '.tiff', '.TIF', '.TIFF',
                            '.mp4', '.MP4',
                            '.webm', '.WEBM',
                            '.mkv', '.MKV',
                            '.flv', '.FLV',
                            '.gif', '.GIF',
                            '.m4v', ',M4V',
                            '.avi', '.AVI',
                            '.mov', '.MOV',
                            '.qt',
                            '.3gp', '.mpg', '.mpeg']

supported_video_list    = ['.mp4', '.MP4',
                            '.webm', '.WEBM',
                            '.mkv', '.MKV',
                            '.flv', '.FLV',
                            '.gif', '.GIF',
                            '.m4v', ',M4V',
                            '.avi', '.AVI',
                            '.mov', '.MOV',
                            '.qt',
                            '.3gp', '.mpg', '.mpeg']

not_supported_file_list = ['.txt', '.exe', '.xls', '.xlsx', '.pdf',
                           '.odt', '.html', '.htm', '.doc', '.docx',
                           '.ods', '.ppt', '.pptx', '.aiff', '.aif',
                           '.au', '.bat', '.java', '.class',
                           '.csv', '.cvs', '.dbf', '.dif', '.eps',
                           '.fm3', '.psd', '.psp', '.qxd',
                           '.ra', '.rtf', '.sit', '.tar', '.zip',
                           '.7zip', '.wav', '.mp3', '.rar', '.aac',
                           '.adt', '.adts', '.bin', '.dll', '.dot',
                           '.eml', '.iso', '.jar', '.py',
                           '.m4a', '.msi', '.ini', '.pps', '.potx',
                           '.ppam', '.ppsx', '.pptm', '.pst', '.pub',
                           '.sys', '.tmp', '.xlt', '.avif']

ctypes.windll.shcore.SetProcessDpiAwareness(True)
scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
font_scale = 1/scaleFactor

# ---------------------- /Dimensions ----------------------

# ---------------------- Functions ----------------------

# ------------------------ Utils ------------------------

def openpaypal():
    webbrowser.open(paypalme, new=1)

def opengithub():
    webbrowser.open(githubme, new=1)

def openpatreon():
    webbrowser.open(patreonme, new=1)

def create_temp_dir(name_dir):
    # first delete the folder if exists
    if os.path.exists(name_dir):
        shutil.rmtree(name_dir)

    # then create a new folder
    if not os.path.exists(name_dir):
        os.makedirs(name_dir)

def find_by_relative_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def adapt_image_to_show(image_to_prepare):
    old_image     = cv2.imread(image_to_prepare)
    actual_width  = old_image.shape[1]
    actual_height = old_image.shape[0]

    if actual_width >= actual_height:
        max_val = actual_width
        max_photo_resolution = show_image_width
    else:
        max_val = actual_height
        max_photo_resolution = show_image_height

    if max_val >= max_photo_resolution:
        downscale_factor = max_val/max_photo_resolution
        new_width        = round(old_image.shape[1]/downscale_factor)
        new_height       = round(old_image.shape[0]/downscale_factor)
        resized_image    = cv2.resize(old_image,
                                   (new_width, new_height),
                                   interpolation = cv2.INTER_NEAREST )
        cv2.imwrite("temp.png", resized_image)
        return "temp.png"
    else:
        new_width        = round(old_image.shape[1])
        new_height       = round(old_image.shape[0])
        resized_image    = cv2.resize(old_image,
                                   (new_width, new_height),
                                   interpolation = cv2.INTER_NEAREST)
        cv2.imwrite("temp.png", resized_image)
        return "temp.png"

def prepare_output_filename(img, AI_model, upscale_factor, target_file_extension):
    result_path = (img.replace("_resized" + target_file_extension, "").replace(target_file_extension, "") 
                    + "_"  + AI_model 
                    + "_x" + str(upscale_factor) 
                    + target_file_extension)
    return result_path

def delete_list_of_files(list_to_delete):
    if len(list_to_delete) > 0:
        for to_delete in list_to_delete:
            if os.path.exists(to_delete):
                os.remove(to_delete)

def write_in_log_file(text_to_insert):
    log_file_name   = app_name + ".log"
    with open(log_file_name,'w') as log_file:
        log_file.write(text_to_insert) 
    log_file.close()

def read_log_file():
    log_file_name   = app_name + ".log"
    with open(log_file_name,'r') as log_file:
        step = log_file.readline()
    log_file.close()
    return step

def extract_frames_from_video(video_path):
    create_temp_dir(app_name + "_temp")

    cap          = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    extr_frame   = 0
    video_frames_list = []
    
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break
        extr_frame += 1
        result_path = app_name + "_temp" + os.sep + "frame_" + str(extr_frame) + ".jpg"
        cv2.imwrite(result_path, frame)
        video_frames_list.append(result_path)

        write_in_log_file("Extracted frames " + str(extr_frame) + "/" + str(total_frames))
    cap.release()

    return video_frames_list

def video_reconstruction_by_frames(input_video_path, video_frames_upscaled_list, AI_model, upscale_factor):
    # 1) get original video informations
    cap          = cv2.VideoCapture(input_video_path)
    frame_rate   = int(cap.get(cv2.CAP_PROP_FPS))
    path_as_list = input_video_path.split("/")
    video_name   = str(path_as_list[-1])
    only_path    = input_video_path.replace(video_name, "")
    cap.release()

    # 2) remove any file extension from original video path string
    for video_type in supported_video_list:
        video_name = video_name.replace(video_type, "")

    # 3) create upscaled video path string
    upscaled_video_name = (only_path +
                           video_name +
                           "_" +
                           AI_model +
                           "_x" +
                           str(upscale_factor) +
                           ".mp4")

    # 4) create upscaled video with upscaled frames
    clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(video_frames_upscaled_list, fps=frame_rate)
    clip.write_videofile(upscaled_video_name)

def convert_image_list(image_list, target_file_extension):
    converted_images = []
    for image in image_list:
        image = image.strip()
        converted_img = convert_image_and_save(image, target_file_extension)
        converted_images.append(converted_img)

    return converted_images

def convert_image_and_save(image_to_prepare, target_file_extension):
    image_to_prepare = image_to_prepare.replace("{", "").replace("}", "")
    new_image_path = image_to_prepare

    for file_type in supported_file_list:
        new_image_path = new_image_path.replace(file_type, target_file_extension)

    cv2.imwrite(new_image_path, cv2.imread(image_to_prepare))
    return new_image_path

# ----------------------- /Utils ------------------------


# ----------------------- Core ------------------------

def on_drop_event(event):
    global image_path
    global multiple_files
    global multi_img_list
    global video_files
    global single_file
    global input_video_path

    info_string.set("")

    supported_file_dropped_number, not_supported_file_dropped_number, supported_video_dropped_number = count_files_dropped(event)
    all_supported, single_file, multiple_files, video_files, more_than_one_video = check_compatibility(supported_file_dropped_number, not_supported_file_dropped_number, supported_video_dropped_number)

    if video_files:
        # video section
        if not all_supported:
            info_string.set("Some files are not supported")
            return
        elif all_supported:
            if multiple_files:
                info_string.set("Only one video supported")
                return
            elif not multiple_files:
                if not more_than_one_video:
                    input_video_path = str(event.data).replace("{", "").replace("}", "")
                    
                    show_video_info_with_drag_drop(input_video_path)

                    # reset variable
                    image_path = "no file"
                    multi_img_list = []

                elif more_than_one_video:
                    info_string.set("Only one video supported")
                    return
    else:
        # image section
        if not all_supported:
            if multiple_files:
                info_string.set("Some files are not supported")
                return
            elif single_file:
                info_string.set("This file is not supported")
                return
        elif all_supported:
            if multiple_files:
                image_list_dropped = drop_event_to_image_list(event)

                show_list_images_in_GUI(image_list_dropped)
                
                multi_img_list = image_list_dropped

                place_clean_button()

                # reset variable
                image_path = "no file"
                video_frames_list = []

            elif single_file:
                image_list_dropped = drop_event_to_image_list(event)

                # convert images to png
                show_single_image_inGUI = threading.Thread(target = show_image_in_GUI,
                                                         args=(str(image_list_dropped[0]), 1),
                                                         daemon=True)
                show_single_image_inGUI.start()

                multi_img_list = image_list_dropped

                # reset variable
                image_path = "no file"
                video_frames_list = []

def check_compatibility(supported_file_dropped_number, not_supported_file_dropped_number, supported_video_dropped_number):
    all_supported  = True
    single_file    = False
    multiple_files = False
    video_files    = False
    more_than_one_video = False

    if not_supported_file_dropped_number > 0:
        all_supported = False

    if supported_file_dropped_number + not_supported_file_dropped_number == 1:
        single_file = True
    elif supported_file_dropped_number + not_supported_file_dropped_number > 1:
        multiple_files = True

    if supported_video_dropped_number == 1:
        video_files = True
        more_than_one_video = False
    elif supported_video_dropped_number > 1:
        video_files = True
        more_than_one_video = True

    return all_supported, single_file, multiple_files, video_files, more_than_one_video

def count_files_dropped(event):
    supported_file_dropped_number = 0
    not_supported_file_dropped_number = 0
    supported_video_dropped_number = 0

    # count compatible images files
    for file_type in supported_file_list:
        supported_file_dropped_number = supported_file_dropped_number + \
            str(event.data).count(file_type)

    # count compatible video files
    for file_type in supported_video_list:
        supported_video_dropped_number = supported_video_dropped_number + \
            str(event.data).count(file_type)

    # count not supported files
    for file_type in not_supported_file_list:
        not_supported_file_dropped_number = not_supported_file_dropped_number + \
            str(event.data).count(file_type)

    return supported_file_dropped_number, not_supported_file_dropped_number, supported_video_dropped_number

def thread_check_steps_for_images( not_used_var, not_used_var2 ):
    time.sleep(2)
    try:
        while True:
            step = read_log_file()
            if "Upscale completed" in step or "Error while upscaling" in step or "Stopped upscaling" in step:
                info_string.set(step)
                stop = 1 + "x"
            info_string.set(step)
            time.sleep(1)
    except:
        place_upscale_button()

def thread_check_steps_for_videos( not_used_var, not_used_var2 ):
    time.sleep(2)
    try:
        while True:
            step = read_log_file()
            if "Upscale video completed" in step or "Error while upscaling" in step or "Stopped upscaling" in step:
                info_string.set(step)
                stop = 1 + "x"
            info_string.set(step)
            time.sleep(1)
    except:
        place_upscale_button()

def drop_event_to_image_list(event):
    image_list = str(event.data).replace("{", "").replace("}", "")

    for file_type in supported_file_list:
        image_list = image_list.replace(file_type, file_type+"\n")

    image_list = image_list.split("\n")
    image_list.pop() 

    return image_list

#-----------------------------------------------------------------------

def prepare_upscaled_file_name(file_name, AI_model, upscale_factor, target_file_extension):
    file_name = file_name.replace(target_file_extension, "") 
    result_path = (file_name + 
                "_" + AI_model + 
                "_x" + str(upscale_factor) + 
                target_file_extension)
    return result_path

def prepare_opencv_superresolution_model(AI_model, upscale_factor, device):
    
    if "ESPCN" in AI_model:
        model_name = "espcn"
        path_model = find_by_relative_path("ESPCN_x" + str(upscale_factor)+".pb")
    elif "FSRCNN" in AI_model:
        model_name = "fsrcnn"
        path_model = find_by_relative_path("FSRCNN_x" + str(upscale_factor)+".pb")
    elif "LapSRN" in AI_model:
        model_name = "lapsrn"
        path_model = find_by_relative_path("LapSRN_x" + str(upscale_factor)+".pb")

    super_res = dnn_superres.DnnSuperResImpl_create()
    super_res.readModel(path_model)
    
    if device == "GPU":
        super_res.setPreferableTarget(cv2.dnn.DNN_TARGET_OPENCL_FP16)
    else:
        super_res.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    super_res.setModel(model_name, upscale_factor)
    return super_res

def process_upscale_multiple_images_opencv(image_list, AI_model, upscale_factor, device, target_file_extension):
    write_in_log_file('Preparing for upscaling')
    start = timer()

    # 1) convert images to target file extension
    image_list = convert_image_list(image_list, target_file_extension)

    # 2) prepare OpenCV model and variables
    super_res = prepare_opencv_superresolution_model(AI_model, upscale_factor, device)
    how_many_images = len(image_list)
    done_images     = 0

    write_in_log_file('Upscaling')

    # 3) starting upscale images
    for image in image_list:
        result_path = prepare_upscaled_file_name(image, AI_model, upscale_factor, target_file_extension)
        result_image = super_res.upsample(cv2.imread(image))
        cv2.imwrite(result_path, result_image)
        done_images += 1
        write_in_log_file("Upscaled images " + 
                            str(done_images) + 
                            "/" + str(how_many_images))
    
    # 4) finish upscale, update logfile
    write_in_log_file("Upscale completed [" + str(round(timer() - start)) + " sec.]")

def process_upscale_video_opencv(input_video_path, AI_model, upscale_factor, device, tiles_resolution, target_file_extension):
    start = timer()

    # 0) extract frames from input video
    write_in_log_file('Extracting video frames')
    image_list = extract_frames_from_video(input_video_path)
    
    # 1) preparing variables and model
    write_in_log_file('Preparing for upscaling')
    how_many_images = len(image_list)
    done_images     = 0
    video_frames_upscaled_list = []
    super_res = prepare_opencv_superresolution_model(AI_model, upscale_factor, device)

    write_in_log_file('Upscaling')
    for image in image_list:
        result_path = prepare_upscaled_file_name(image, AI_model, upscale_factor, target_file_extension)
        
        result_image = super_res.upsample(cv2.imread(image))
        video_frames_upscaled_list.append(result_path)
        cv2.imwrite(result_path, result_image)
        
        done_images += 1
        write_in_log_file("Upscaled images " + 
                            str(done_images) + 
                            "/" + str(how_many_images))
    
    write_in_log_file("Processing upscaled video")
    
    video_reconstruction_by_frames(input_video_path, video_frames_upscaled_list, AI_model, upscale_factor)

    write_in_log_file("Upscale video completed [" + str(round(timer() - start)) + " sec.]")

# ----------------------- /Core ------------------------

# ---------------------- GUI related ----------------------

def upscale_button_command():
    global image_path
    global multiple_files
    global process_upscale
    global thread_wait
    global upscale_factor
    global video_frames_list
    global video_files
    global video_frames_upscaled_list
    global input_video_path
    global device

    info_string.set("...")

    if video_files:
        place_stop_button()

        process_upscale = multiprocessing.Process(target = process_upscale_video_opencv,
                                                  args   = (input_video_path, 
                                                            AI_model, 
                                                            upscale_factor, 
                                                            device,
                                                            tiles_resolution,
                                                            target_file_extension))
        process_upscale.start()

        thread_wait = threading.Thread(target = thread_check_steps_for_videos,
                                       args   = (upscale_factor, device), 
                                       daemon = True)
        thread_wait.start()

    elif multiple_files:
        place_stop_button()
        
        process_upscale = multiprocessing.Process(target = process_upscale_multiple_images_opencv,
                                                    args   = (multi_img_list, 
                                                             AI_model, 
                                                             upscale_factor, 
                                                             device,
                                                             target_file_extension))
        process_upscale.start()

        thread_wait = threading.Thread(target = thread_check_steps_for_images,
                                        args   = (upscale_factor, device), daemon = True)
        thread_wait.start()

    elif single_file:
        place_stop_button()

        process_upscale = multiprocessing.Process(target = process_upscale_multiple_images_opencv,
                                                    args   = (multi_img_list, 
                                                             AI_model, 
                                                             upscale_factor, 
                                                             device,
                                                             target_file_extension))
        process_upscale.start()

        thread_wait = threading.Thread(target = thread_check_steps_for_images,
                                       args   = (upscale_factor, device), daemon = True)
        thread_wait.start()

    elif "no file" in image_path:
        info_string.set("No file selected")
  
def stop_button_command():
    global process_upscale
    process_upscale.terminate()
    
    # this will stop thread that check upscaling steps
    write_in_log_file("Stopped upscaling") 

def clear_input_variables():
    global image_path
    global multi_img_list
    global video_frames_list
    global single_file
    global multiple_files
    global video_files

    # reset variable
    image_path        = "no file"
    multi_img_list    = []
    video_frames_list = []
    single_file       = False
    multiple_files    = False
    video_files       = False
    multi_img_list    = []
    video_frames_list = []

def clear_app_background():
    drag_drop = ttk.Label(root,
                          ondrop = on_drop_event,
                          relief = "flat",
                          background = background_color,
                          foreground = text_color)
    drag_drop.place(x = left_bar_width + 50, y=0,
                    width = drag_drop_width, height = drag_drop_height)

def place_drag_drop_widget():
    clear_input_variables()

    clear_app_background()

    ft = tkFont.Font(family = default_font,
                        size   = round(12 * font_scale),
                        weight = "bold")

    text_drop = (" DROP FILES HERE \n\n"
                + " ⥥ \n\n"
                + " IMAGE   - jpg png tif bmp webp \n\n"
                + " IMAGE LIST   - jpg png tif bmp webp \n\n"
                + " VIDEO   - mp4 webm mkv flv gif avi mov mpg qt 3gp \n\n")

    drag_drop = ttk.Notebook(root, ondrop  = on_drop_event)

    x_center = 30 + left_bar_width + drag_drop_width/2 - (drag_drop_width * 0.75)/2
    y_center = drag_drop_height/2 - (drag_drop_height * 0.75)/2

    drag_drop.place(x = x_center, 
                    y = y_center, 
                    width  = drag_drop_width * 0.75, 
                    height = drag_drop_height * 0.75)

    drag_drop_text = ttk.Label(root,
                            text    = text_drop,
                            ondrop  = on_drop_event,
                            font    = ft,
                            anchor  = "center",
                            relief  = 'flat',
                            justify = "center",
                            foreground = text_color)

    x_center = 30 + left_bar_width + drag_drop_width/2 - (drag_drop_width * 0.5)/2
    y_center = drag_drop_height/2 - (drag_drop_height * 0.5)/2
    
    drag_drop_text.place(x = x_center, 
                         y = y_center, 
                         width  = drag_drop_width * 0.50, 
                         height = drag_drop_height * 0.50)

def show_video_info_with_drag_drop(video_path):
    global image
    
    fist_frame = "temp.jpg"
    
    clear_app_background()

    # 1) get video informations
    cap          = cv2.VideoCapture(video_path)
    width        = round(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height       = round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    num_frames   = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_rate   = cap.get(cv2.CAP_PROP_FPS)
    duration     = num_frames/frame_rate
    minutes      = int(duration/60)
    seconds      = duration % 60
    path_as_list = video_path.split("/")
    video_name   = str(path_as_list[-1])
    
    # 2) get first frame of the video
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break
        cv2.imwrite(fist_frame, frame)
        break
    cap.release()

    # 3) resize the frame to fit the UI
    image_to_show_resized = adapt_image_to_show(fist_frame)

    # 4) show the resized image in the UI
    image = tk.PhotoImage(file = image_to_show_resized)
    drag_drop_and_images = ttk.Label(root,
                                     image   = image,
                                     ondrop  = on_drop_event,
                                     anchor  = "center",
                                     relief  = "flat",
                                     justify = "center",
                                     background = background_color,
                                     foreground = "#202020")
    drag_drop_and_images.place(x = 30 + left_bar_width + drag_drop_width/2 - show_image_width/2,
                               y = drag_drop_height/2 - show_image_height/2 - 15,
                               width  = show_image_width,
                               height = show_image_height)

    # 5) remove the temp first frame
    os.remove(fist_frame)

    # 6) create string video description
    file_description = ( video_name + "\n" + "[" + str(width) + "x" + str(height) + "]" + " | " + str(minutes) + 'm:' + str(round(seconds)) + "s | " + str(num_frames) + "frames | " + str(round(frame_rate)) + "fps")

    video_info_width = drag_drop_width * 0.8

    video_info_space = ttk.Label(root,
                                 text    = file_description,
                                 ondrop  = on_drop_event,
                                 font    = (default_font, round(11 * font_scale), "bold"),
                                 anchor  = "center",
                                 relief  = "flat",
                                 justify = "center",
                                 background = background_color,
                                 foreground = "#D3D3D3",
                                 wraplength = video_info_width * 0.95)
    video_info_space.place(x = 30 + left_bar_width + drag_drop_width/2 - video_info_width/2,
                           y = drag_drop_height - 85,
                           width  = video_info_width,
                           height = 65)

    # 7) show clear button
    place_clean_button()

def show_list_images_in_GUI(image_list_prepared):
    clear_app_background()

    final_string = "\n"
    counter_img = 0

    for elem in image_list_prepared:
        counter_img += 1
        if counter_img <= 8:
            # add first 8 files in list
            img     = cv2.imread(elem.strip())
            width   = round(img.shape[1])
            height  = round(img.shape[0])
            img_name = str(elem.split("/")[-1])

            final_string += (str(counter_img) 
                            + ".  " 
                            + img_name 
                            + " | [" + str(width) + "x" + str(height) + "]" + "\n\n")
        else:
            final_string += "and others... \n"
            break

    list_height = 420
    list_width  = 750

    images_list = ttk.Label(root,
                            text    = final_string,
                            ondrop  = on_drop_event,
                            font    = (default_font, round(12 * font_scale)),
                            anchor  = "n",
                            relief  = "flat",
                            justify = "left",
                            background = background_color,
                            foreground = "#D3D3D3",
                            wraplength = list_width)

    images_list.place(x = 30 + left_bar_width + drag_drop_width/2 - list_width/2,
                               y = drag_drop_height/2 - list_height/2 - 25,
                               width  = list_width,
                               height = list_height)

    images_counter = ttk.Entry(root, 
                                foreground = text_color,
                                ondrop  = on_drop_event,
                                font    = (default_font, round(12 * font_scale), "bold"), 
                                justify = 'center')

    images_counter.insert(0, str(len(image_list_prepared)) + ' images')

    images_counter.configure(state='disabled')

    images_counter.place(x = left_bar_width + drag_drop_width/2 + 125,
                        y = drag_drop_height/2 + 250,
                        width  = 250,
                        height = 42)

def show_image_in_GUI(image_to_show, _ ):
    global image

    image_to_show = image_to_show.replace('{', '').replace('}', '')

    # 1) resize image to fit the UI
    image_to_show_resized = adapt_image_to_show(image_to_show)

    # 2) clean the background
    clear_app_background()

    # 3) show the resized image in the UI
    image = tk.PhotoImage(file = image_to_show_resized)
    drag_drop_and_images = ttk.Label(root,
                                     text="",
                                     image   = image,
                                     ondrop  = on_drop_event,
                                     anchor  = "center",
                                     relief  = "flat",
                                     justify = "center",
                                     background = background_color,
                                     foreground = "#202020")
    drag_drop_and_images.place(x = 30 + left_bar_width + drag_drop_width/2 - show_image_width/2,
                               y = drag_drop_height/2 - show_image_height/2,
                               width  = show_image_width,
                               height = show_image_height)

    # 4) show the image file information in the UI
    path_as_list = image_to_show.split("/")
    img_name     = str(path_as_list[-1])
    img          = cv2.imread(image_to_show)
    width        = round(img.shape[1])
    height       = round(img.shape[0])

    single_image_path = (img_name + " | [" + str(width) + "x" + str(height) + "]")
    single_image_info = ttk.Label(root,
                                  font =(default_font, round(11 * font_scale), "bold"),
                                  text = single_image_path,
                                  relief  = "flat",
                                  justify = "center",
                                  background = background_color,
                                  foreground = "#D3D3D3",
                                  anchor     = "center")

    single_image_info.place(x = 30 + left_bar_width + drag_drop_width/2 - image_text_width/2,
                            y = drag_drop_height - 70,
                            width  = image_text_width,
                            height = 40)

    # 5) delete the resized temp image
    if "temp.png" in image_to_show_resized:
        os.remove(image_to_show_resized)

    # 6) show clear button
    place_clean_button()

def place_upscale_button():
    global play_icon
    play_icon = tk.PhotoImage(file = find_by_relative_path('upscale_icon.png'))
    
    ft = tkFont.Font(family = default_font,
                    size   = round(11 * font_scale),
                    weight = 'bold')
    Upsc_Butt_Style = ttk.Style()
    Upsc_Butt_Style.configure("Bold.TButton", font = ft, foreground = text_color)

    Upscale_button = ttk.Button(root, 
                                text  = '  UPSCALE',
                                image = play_icon,
                                compound = tk.LEFT,
                                style    = 'Bold.TButton')

    Upscale_button.place(x      = 50 + left_bar_width/2 - 310/2,  
                         y      = left_bar_height - 110,
                         width  = 310,
                         height = 45)
    Upscale_button["command"] = lambda: upscale_button_command()

def place_stop_button():
    ft = tkFont.Font(family = default_font,
                    size   = round(11 * font_scale),
                    weight = 'bold')
    
    global stop_icon
    stop_icon = tk.PhotoImage(file = find_by_relative_path('stop_icon.png'))
    
    Upsc_Butt_Style = ttk.Style()
    Upsc_Butt_Style.configure("Bold.TButton", font = ft)

    Stop_button = ttk.Button(root, 
                                text  = '  STOP UPSCALE ',
                                image = stop_icon,
                                compound = tk.LEFT,
                                style    = 'Bold.TButton')

    Stop_button.place(x      = 50 + left_bar_width/2 - 310/2,  
                      y      = left_bar_height - 110,
                      width  = 310,
                      height = 45)

    Stop_button["command"] = lambda: stop_button_command()

def combobox_AI_selection(event):
    global AI_model

    AI_model = str(selected_AI.get())

    Combo_box_AI.set('')
    Combo_box_AI.set(AI_model)

def combobox_upscale_factor_selection(event):
    global upscale_factor

    selected = str(selected_upscale_factor.get())
    if '0.5' in selected:
        upscale_factor = 0.5
    if '1' in selected:
        upscale_factor = 1
    elif '2' in selected:
        upscale_factor = 2
    elif '3' in selected:
        upscale_factor = 3
    elif '4' in selected:
        upscale_factor = 4

    Combo_box_upscale_factor.set('') # clean selection in widget
    Combo_box_upscale_factor.set(selected)

def combobox_backend_selection(event):
    global device

    selected = str(selected_backend.get())
    if 'GPU' in selected:
        device = "GPU"
    elif 'CPU' in selected:
        device = "CPU"

    Combo_box_backend.set('')
    Combo_box_backend.set(selected)

def combobox_VRAM_selection(event):
    global tiles_resolution

    selected = str(selected_VRAM.get())

    if 'Minimal' == selected:
        tiles_resolution = 250
    if 'Medium' == selected:
        tiles_resolution = 500
    if 'High' == selected:
        tiles_resolution = 750
    if 'Max' == selected:
        tiles_resolution = 1000

    Combo_box_VRAM.set('')
    Combo_box_VRAM.set(selected)

def place_backend_combobox():
    ft = tkFont.Font(family = default_font,
                     size   = round(11 * font_scale),
                     weight = "bold")

    root.option_add("*TCombobox*Listbox*Background", background_color)
    root.option_add("*TCombobox*Listbox*Foreground", selected_button_color)
    root.option_add("*TCombobox*Listbox*Font",       ft)
    root.option_add('*TCombobox*Listbox.Justify',    'center')

    global Combo_box_backend
    Combo_box_backend = ttk.Combobox(root, 
                            textvariable = selected_backend, 
                            justify      = 'center',
                            foreground   = text_color,
                            values       = ['GPU', 'CPU'],
                            state        = 'readonly',
                            takefocus    = False,
                            font         = ft)
    Combo_box_backend.place(x = 50 + left_bar_width/2 - 285/2, 
                            y = button_3_y, 
                            width  = 290, 
                            height = 42)
    Combo_box_backend.bind('<<ComboboxSelected>>', combobox_backend_selection)
    Combo_box_backend.set('GPU')

def place_upscale_factor_combobox():
    ft = tkFont.Font(family = default_font,
                     size   = round(11 * font_scale),
                     weight = "bold")

    root.option_add("*TCombobox*Listbox*Background", background_color)
    root.option_add("*TCombobox*Listbox*Foreground", selected_button_color)
    root.option_add("*TCombobox*Listbox*Font",       ft)
    root.option_add('*TCombobox*Listbox.Justify', 'center')

    global Combo_box_upscale_factor
    Combo_box_upscale_factor = ttk.Combobox(root, 
                            textvariable = selected_upscale_factor, 
                            justify      = 'center',
                            foreground   = text_color,
                            values       = ['x2', 'x4'],
                            state        = 'readonly',
                            takefocus    = False,
                            font         = ft)
    Combo_box_upscale_factor.place(x = 50 + left_bar_width/2 - 285/2, 
                       y = button_2_y, 
                       width  = 290, 
                       height = 42)
    Combo_box_upscale_factor.bind('<<ComboboxSelected>>', combobox_upscale_factor_selection)
    Combo_box_upscale_factor.set('x2')

def place_AI_combobox():
    ft = tkFont.Font(family = default_font,
                     size   = round(11 * font_scale),
                     weight = "bold")

    root.option_add("*TCombobox*Listbox*Background", background_color)
    root.option_add("*TCombobox*Listbox*Foreground", selected_button_color)
    root.option_add("*TCombobox*Listbox*Font",       ft)
    root.option_add('*TCombobox*Listbox.Justify', 'center')

    global Combo_box_AI
    Combo_box_AI = ttk.Combobox(root, 
                        textvariable = selected_AI, 
                        justify      = 'center',
                        foreground   = text_color,
                        values       = ['FSRCNN', 'ESPCN', 'LapSRN'],
                        state        = 'readonly',
                        takefocus    = False,
                        font         = ft)
    Combo_box_AI.place(x = 50 + left_bar_width/2 - 285/2,  
                       y = button_1_y, 
                       width  = 290, 
                       height = 42)
    Combo_box_AI.bind('<<ComboboxSelected>>', combobox_AI_selection)
    Combo_box_AI.set("FSRCNN")

def place_VRAM_combobox():
    ft = tkFont.Font(family = default_font,
                     size   = round(11 * font_scale),
                     weight = "bold")


    root.option_add("*TCombobox*Listbox*Background", background_color)
    root.option_add("*TCombobox*Listbox*Foreground", selected_button_color)
    root.option_add("*TCombobox*Listbox*Font",       ft)
    root.option_add('*TCombobox*Listbox.Justify',    'center')

    global Combo_box_VRAM
    Combo_box_VRAM = ttk.Combobox(root, 
                            textvariable = selected_VRAM, 
                            justify      = 'center',
                            foreground   = text_color,
                            values       = ['Minimal', 'Medium', 'High', 'Max'],
                            state        = 'readonly',
                            takefocus    = False,
                            font         = ft)
    Combo_box_VRAM.place(x = 50 + left_bar_width/2 - 285/2, 
                         y = button_4_y, 
                         width  = 290, 
                         height = 42)
    Combo_box_VRAM.bind('<<ComboboxSelected>>', combobox_VRAM_selection)
    Combo_box_VRAM.set('Max')

def place_clean_button():
    global clear_icon
    clear_icon = tk.PhotoImage(file = find_by_relative_path('clear_icon.png'))

    clean_button = ttk.Button(root, 
                            text     = '  CLEAN',
                            image    = clear_icon,
                            compound = 'left',
                            style    = 'Bold.TButton')

    clean_button.place(x = 50 + left_bar_width + drag_drop_width/2 - 175/2,
                       y = 20,
                       width  = 175,
                       height = 40)
    clean_button["command"] = lambda: place_drag_drop_widget()

def place_background():
    Background = ttk.Label(root, background = background_color, relief = 'flat')
    Background.place(x = 0, 
                     y = 0, 
                     width  = window_width,
                     height = window_height)

def place_left_bar():
    Left_bar = ttk.Notebook(root)
    if windows_subversion >= 22000:  # Windows 11
        Left_bar.place(x = 50, 
                       y = 0, 
                       width  = left_bar_width,
                       height = 700)
    else:                            # Windows 10
        Left_bar.place(x = 50, 
                       y = 20, 
                       width  = left_bar_width,
                       height = 670)

def place_app_title():
    horizontal_center = 50 + left_bar_width/2

    Title = ttk.Label(root, 
                      font = (default_font, round(17 * font_scale), "bold"),
                      foreground = "#4169e1", 
                      anchor     = 'center', 
                      text       = app_name)
    Title.place(x = horizontal_center - 300/2,
                y = 30,
                width  = 300,
                height = 55)

    label_version = ttk.Button(root,
                               padding = '0 0 0 0',
                               text    = version,
                               compound = 'center',
                               style    = 'Bold.TButton')
    label_version.place(x = 50 + left_bar_width - 65*2,
                        y = 43,
                        width  = 60,
                        height = 32) 

def place_github_button():
    global logo_git
    logo_git = PhotoImage(file = find_by_relative_path("github_logo.png"))

    ft = tkFont.Font(family = default_font)
    Butt_Style = ttk.Style()
    Butt_Style.configure("Bold.TButton", font = ft)

    github_button = ttk.Button(root,
                               image = logo_git,
                               padding = '0 0 0 0',
                               text    = ' Github',
                               compound = 'left',
                               style    = 'Bold.TButton')
    github_button.place(x = 50 + left_bar_width/2 - 115/2 - 113 - 10,
                        y = support_button_height,
                        width  = 113,
                        height = 35)
    github_button["command"] = lambda: opengithub()

def place_paypal_button():
    global logo_paypal
    logo_paypal = PhotoImage(file=find_by_relative_path("paypal_logo.png"))

    ft = tkFont.Font(family = default_font)
    Butt_Style = ttk.Style()
    Butt_Style.configure("Bold.TButton", font = ft)

    logo_paypal_label = ttk.Button(root,
                                   image = logo_paypal,
                                   padding = '0 0 0 0',
                                   text = ' Paypal',
                                   compound = 'left',
                                   style    = 'Bold.TButton')
    logo_paypal_label.place(x = 50 + left_bar_width/2 - 113/2,
                            y = support_button_height,
                            width  = 113,
                            height = 35)
    logo_paypal_label["command"] = lambda: openpaypal()

def place_patreon_button():
    global logo_patreon
    logo_patreon = PhotoImage(file=find_by_relative_path("patreon_logo.png"))

    ft = tkFont.Font(family = default_font)
    Butt_Style = ttk.Style()
    Butt_Style.configure("Bold.TButton", font = ft)
    
    logo_patreon_label = ttk.Button(root,
                                   image = logo_patreon,
                                   padding = '0 0 0 0',
                                   text = ' Patreon',
                                   compound = 'left',
                                   style    = 'Bold.TButton')
    logo_patreon_label.place(x = 50 + left_bar_width/2 + 113/2 + 10,
                            y = support_button_height,
                            width  = 113,
                            height = 35)
    logo_patreon_label["command"] = lambda: openpatreon()

def place_AI_models_title():
    IA_selection_title = ttk.Label(root, 
                                   font = (default_font, round(12 * font_scale), "bold"), 
                                   foreground = text_color, 
                                   justify    = 'left', 
                                   relief     = 'flat', 
                                   text       = " ◪  AI model ")
    IA_selection_title.place(x = left_bar_width/2 - 115,
                             y = button_1_y - 45,
                             width  = 200,
                             height = 40)

def place_upscale_factor_title():
    Upscale_fact_selection_title = ttk.Label(root, 
                                            font = (default_font, round(12 * font_scale), "bold"), 
                                            foreground = text_color, 
                                            justify    = 'left', 
                                            relief     = 'flat', 
                                            text       = " ⤮  Upscale factor ")
    Upscale_fact_selection_title.place(x = left_bar_width/2 - 115,
                                        y = button_2_y - 45,
                                        width  = 200,
                                        height = 40)

def place_backend_title():
    Upscale_backend_selection_title = ttk.Label(root, 
                                                font = (default_font, round(12 * font_scale), "bold"), 
                                                foreground = text_color, 
                                                justify    = 'left', 
                                        	    relief     = 'flat', 
                                                text       = " ⍚  AI backend ")
    Upscale_backend_selection_title.place(x = left_bar_width/2 - 115,
                                          y = button_3_y - 45,
                                          width  = 200,
                                          height = 40)

def place_VRAM_title():
    IA_selection_title = ttk.Label(root, 
                                   font = (default_font, round(12 * font_scale), "bold"), 
                                   foreground = text_color, 
                                   justify    = 'left', 
                                   relief     = 'flat', 
                                   text       = " ⋈  Vram/Ram ")
    IA_selection_title.place(x = left_bar_width/2 - 115,
                             y = button_4_y - 45,
                             width  = 200,
                             height = 40)

def place_message_box():
    message_label = ttk.Label(root,
                            font = (default_font, round(11 * font_scale), "bold"),
                            textvar    = info_string,
                            relief     = "flat",
                            justify    = "center",
                            foreground = "#ffbf00",
                            anchor     = "center")
    message_label.place(x = 50 + left_bar_width/2 - (left_bar_width * 0.75)/2,
                        y = 575,
                        width  = left_bar_width * 0.75,
                        height = 30)

# ---------------------- /GUI related ----------------------

# ---------------------- /Functions ----------------------

def apply_windows_dark_bar(window_root):
    window_root.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute          = ctypes.windll.dwmapi.DwmSetWindowAttribute
    get_parent                    = ctypes.windll.user32.GetParent
    hwnd                          = get_parent(window_root.winfo_id())
    rendering_policy              = DWMWA_USE_IMMERSIVE_DARK_MODE
    value                         = 2
    value                         = ctypes.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ctypes.byref(value), ctypes.sizeof(value))    

    #Changes the window size
    window_root.geometry(str(window_root.winfo_width()+1) + "x" + str(window_root.winfo_height()+1))
    #Returns to original size
    window_root.geometry(str(window_root.winfo_width()-1) + "x" + str(window_root.winfo_height()-1))

def apply_windows_transparency_effect(window_root):
    window_root.wm_attributes("-transparent", background_color)
    hwnd = ctypes.windll.user32.GetParent(window_root.winfo_id())
    ApplyMica(hwnd, MICAMODE.DARK )

class ErrorMessage():
    def __init__(self, error_root):
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
        scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        font_scale = 1.2/scaleFactor
        
        error_root.title("")
        width  = 515
        height = 525
        screenwidth = error_root.winfo_screenwidth()
        screenheight = error_root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        error_root.geometry(alignstr)
        error_root.resizable(width=False, height=False)

        error_root.iconphoto(False, PhotoImage(file = find_by_relative_path("logo.png")))

        window_width  = 515
        window_height = 530

        error_string  = "Upscale\nerror"
        error_suggest = (" Ops, some error occured while upscaling: \n\n"
                             + " - have you changed the file location? \n"
                             + " - try to set Upscale Factor to x2 or x3 \n"
                             + " - try to set AI Backend to <cpu> ")

        ft = tkFont.Font(family=default_font,
                         size=int(12 * font_scale),
                         weight="bold")

        Error_container = tk.Label(error_root)
        Error_container["anchor"]  = "center"
        Error_container["justify"] = "center"
        Error_container["font"]    = ft
        Error_container["bg"]      = "#FF4433"
        Error_container["fg"]      = "#202020"
        Error_container["text"]    = error_string
        Error_container["relief"]  = "flat"
        Error_container.place(x = 0,
                              y = 0,
                              width  = window_width,
                              height = window_height/4)

        ft = tkFont.Font(family=default_font,
                    size=int(11 * font_scale),
                    weight="bold")

        Suggest_container = tk.Label(error_root)
        Suggest_container["anchor"]  = "center"
        Suggest_container["justify"] = "left"
        Suggest_container["font"]    = ft
        Suggest_container["bg"]      = background_color
        Suggest_container["fg"]      = "grey"
        Suggest_container["text"]    = error_suggest
        Suggest_container["relief"]  = "flat"
        Suggest_container["wraplength"] = window_width*0.9
        Suggest_container.place(x = 0,
                                y = window_height/4,
                                width  = window_width,
                                height = window_height*0.75)

        error_root.attributes('-topmost', True)
        
        if windows_subversion >= 22000: # Windows 11
            apply_windows_transparency_effect(error_root)
        apply_windows_dark_bar(error_root)

        error_root.update()
        error_root.mainloop()

class App:
    def __init__(self, root):
        sv_ttk.use_dark_theme()
        
        root.title('')
        width        = window_width
        height       = window_height
        screenwidth  = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr     = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)
        root.iconphoto(False, PhotoImage(file = find_by_relative_path("logo.png")))

        if windows_subversion >= 22000: # Windows 11
            apply_windows_transparency_effect(root)
        apply_windows_dark_bar(root)

        place_background()               # Background
        place_left_bar()                 # Left bar background
        place_app_title()                # App title
        place_github_button()
        place_paypal_button()
        place_patreon_button()
        place_AI_models_title()          # AI models title
        place_AI_combobox()              # AI models widget
        place_upscale_factor_title()     # Upscale factor title
        place_upscale_factor_combobox()  # Upscale factor widget
        place_backend_title()            # Backend title
        place_backend_combobox()         # Backend widget
        place_message_box()              # Message box
        place_upscale_button()           # Upscale button
        place_drag_drop_widget()         # Drag&Drop widget
        
if __name__ == "__main__":
    multiprocessing.freeze_support()

    root        = tkinterDnD.Tk()
    info_string = tk.StringVar()
    selected_AI = tk.StringVar()
    selected_upscale_factor = tk.StringVar()
    selected_backend = tk.StringVar()
    selected_VRAM    = tk.StringVar()


    app = App(root)
    root.update()
    root.mainloop()
