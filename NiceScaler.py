try:
    import pyi_splash
    pyi_splash.close()
except:
    pass

import ctypes
import multiprocessing
import os
import os.path
import shutil
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkFont
import webbrowser
from pathlib import Path
from timeit import default_timer as timer
from tkinter import *
from tkinter import ttk

import cv2
import tkinterDnD
from cv2 import dnn_superres
from PIL import Image, ImageTk

ctypes.windll.shcore.SetProcessDpiAwareness(True)
scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100

if scaleFactor == 1.0:
    font_scale = 1.25
elif scaleFactor == 1.25:
    font_scale = 1.0
else:
    font_scale = 0.85

version  = "1.3.0 - stable"
author   = "Annunziata Gianluca"
paypalme = "https://www.paypal.com/paypalme/jjstd/5"
githubme = "https://github.com/Djdefrag/NiceScaler"

image_path     = "no file"
AI_model       = "FSRCNN"
device         = "cpu"
actual_step    = ""
single_file    = False
multiple_files = False
video_files    = False
multi_img_list      = []
video_frames_list   = []
video_frames_upscaled_list = []
original_video_path = ""
default_font        = 'Calibri'

supported_file_list = ['.jpg', '.jpeg', '.JPG', '.JPEG',
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
                       '.3gp', '.mpg', '.mpeg']

supported_video_list = ['.mp4', '.MP4',
                        '.webm', '.WEBM',
                        '.mkv', '.MKV',
                        '.flv', '.FLV',
                        '.gif', '.GIF',
                        '.m4v', ',M4V',
                        '.avi', '.AVI',
                        '.mov', '.MOV',
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
                           '.sys', '.tmp', '.xlt']

upscale_factor = 2

# ---------------------- Dimensions ----------------------

window_width   = 1300
window_height  = 725
left_bar_width = 420
left_bar_height  = window_height
drag_drop_width  = window_width - left_bar_width
drag_drop_height = window_height
button_width     = 250
button_height    = 35
show_image_width  = drag_drop_width * 0.9
show_image_height = drag_drop_width * 0.7
image_text_width  = drag_drop_width * 0.9
image_text_height = 34
button_1_y = 195
button_2_y = 255
button_3_y = 315
drag_drop_background = "#303030"
drag_drop_text_color = "#808080"

# ---------------------- /Dimensions ----------------------

# ---------------------- Functions ----------------------

# ------------------------ Utils ------------------------

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

def create_temp_dir(name_dir):
    # first delete the folder if exists
    if os.path.exists(name_dir):
        shutil.rmtree(name_dir)

    # then create a new folder
    if not os.path.exists(name_dir):
        os.makedirs(name_dir)

def find_file_production_and_dev(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def openpaypal():
    webbrowser.open(paypalme, new=1)

def opengithub():
    webbrowser.open(githubme, new=1)

# ----------------------- /Utils ------------------------

def function_drop(event):
    global image_path
    global multiple_files
    global multi_img_list
    global video_files
    global single_file

    info_string.set("")

    supported_file_dropped_number, not_supported_file_dropped_number, supported_video_dropped_number = count_files_dropped(event)

    all_supported, single_file, multiple_files, video_files, more_than_one_video = check_compatibility(
        supported_file_dropped_number, 
        not_supported_file_dropped_number, 
        supported_video_dropped_number)

    if video_files:
        # video section
        if not all_supported:
            info_string.set("Some files are not supported.")
            return
        elif all_supported:
            if multiple_files:
                info_string.set("Only one video supported.")
                return
            elif not multiple_files:
                if not more_than_one_video:
                    file_vid = str(event.data).replace("{", "").replace("}", "")
                    show_video_info_with_drag_drop(file_vid)
                    thread_extract_frames = threading.Thread(target=extract_frames_from_video,
                                                             args=(
                                                                 file_vid, 1),
                                                             daemon=True)
                    thread_extract_frames.start()

                    # reset variable
                    image_path = "no file"
                    multi_img_list = []

                elif more_than_one_video:
                    info_string.set("Only one video supported.")
                    return
    else:
        # image section
        if not all_supported:
            if multiple_files:
                info_string.set("Some files are not supported.")
                return
            elif single_file:
                info_string.set("This file is not supported.")
                return
        elif all_supported:
            if multiple_files:
                image_list_dropped = from_string_to_image_list(event)
                thread_convert_images = threading.Thread(target=convert_multi_images_to_png,
                                                         args=(
                                                             image_list_dropped, 1),
                                                         daemon=True)
                thread_convert_images.start()

                show_list_images_in_GUI_with_drag_drop(image_list_dropped)
                multi_img_list = convert_only_image_filenames(image_list_dropped)

                # reset variable
                image_path = "no file"
                video_frames_list = []

            elif single_file:
                multiple_files = False
                image_path = convert_single_image_to_png(str(event.data))
                show_image_in_GUI_with_drag_drop(image_path)
                place_fileName_label(image_path)

                # reset variable
                multi_img_list = []
                video_frames_list = []

def upscale_button_command():
    global image_path
    global multiple_files
    global actual_step
    global process_upscale
    global upscale_factor
    global video_frames_list
    global video_files
    global video_frames_upscaled_list
    global original_video_path
    global device

    if "no model" in AI_model:
        info_string.set("No AI model selected!")
        return

    if video_files:
        if "extracting" in actual_step:
            info_string.set("Waiting for frames extraction...")
            return
        elif "ready" in actual_step:
            info_string.set("Upscaling video...")
            place_stop_button()

            video_frames_upscaled_list = convert_frames_list_uspcaled(
                video_frames_list, AI_model, upscale_factor)

            process_upscale = multiprocessing.Process(target=OpenCV_AI_upscale_video_frames,
                                                      args=(video_frames_list, AI_model, upscale_factor, device))
            process_upscale.start()

            thread_wait = threading.Thread(target=thread_wait_for_videoframes_and_video_reconstruct,
                                           args=(video_frames_list, video_frames_upscaled_list,
                                                 AI_model, upscale_factor, original_video_path),
                                           daemon=True)
            thread_wait.start()

    elif multiple_files:
        if "converting" in actual_step:
            info_string.set("Waiting for images conversion...")
            return
        elif "ready" in actual_step:
            info_string.set("Upscaling multiple images...")
            place_stop_button()

            process_upscale = multiprocessing.Process(target=OpenCV_AI_upscale_multiple_images,
                                                      args=(multi_img_list, AI_model, upscale_factor, device))
            process_upscale.start()

            thread_wait = threading.Thread(target=thread_wait_for_multiple_file,
                                           args=(multi_img_list,
                                                 AI_model, upscale_factor),
                                           daemon=True)
            thread_wait.start()

    elif single_file:
        place_stop_button()
        info_string.set("Upscaling single image...")
        process_upscale = multiprocessing.Process(target=OpenCV_AI_upscale_image,
                                                  args=(image_path, AI_model, upscale_factor, device))
        process_upscale.start()

        thread_wait = threading.Thread(target=thread_wait_for_single_file,
                                       args=(image_path.replace(
                                           ".png", "") + "_" + AI_model + "_x" + str(upscale_factor) + ".png", 1),
                                       daemon=True)
        thread_wait.start()

    elif "no file" in image_path:
        info_string.set("No file selected!")

def extract_frames_from_video(video_path, _):
    global actual_step
    global video_frames_list
    global original_video_path

    original_video_path = video_path

    actual_step = "extracting"
    info_string.set("Extracting frames from video...")

    # create a temp directory for frames
    temp_dir = "NiceScaler_temp"
    create_temp_dir(temp_dir)

    cap = cv2.VideoCapture(video_path)
    num_frame = 0
    video_frames_list = []
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break
        num_frame += 1
        result_path = temp_dir + os.sep + "frame_" + str(num_frame) + ".png"
        cv2.imwrite(result_path, frame)
        video_frames_list.append(result_path)
        info_string.set("Extracting frames n. " + str(num_frame))

    cap.release()
    cv2.destroyAllWindows()
    actual_step = "ready"
    info_string.set("")

def video_reconstruction_by_frames(original_video_path, video_frames_upscaled_list, AI_model, upscale_factor):

    info_string.set("Reconstructing video...")
    cap = cv2.VideoCapture(original_video_path)
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    path_as_list = original_video_path.split("/")
    video_name = str(path_as_list[-1])
    only_path = original_video_path.replace(video_name, "")
    cap.release()

    for video_type in supported_video_list:
        video_name = video_name.replace(video_type, "")

    upscaled_video_name = only_path + video_name + "_" + \
        AI_model + "_x" + str(upscale_factor) + ".mp4"

    first_image = video_frames_upscaled_list[0]
    img = cv2.imread(first_image)
    height, width, layers = img.shape
    size = (width, height)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(upscaled_video_name, fourcc, frame_rate, size)

    for upscaled_frame in video_frames_upscaled_list:
        #print(upscaled_frame)
        frame = cv2.imread(upscaled_frame)
        video.write(frame)

    video.release()

def prepare_opencv_superresolution_model(AI_model, upscale_factor, device):
    if "EDSR" in AI_model:
        model_name = "edsr"
        path_model = find_file_production_and_dev(
            "EDSR_x" + str(upscale_factor)+".pb")
    elif "ESPCN" in AI_model:
        model_name = "espcn"
        path_model = find_file_production_and_dev(
            "ESPCN_x" + str(upscale_factor)+".pb")
    elif "FSRCNN" in AI_model:
        model_name = "fsrcnn"
        path_model = find_file_production_and_dev(
            "FSRCNN_x" + str(upscale_factor)+".pb")
    elif "LapSRN" in AI_model:
        model_name = "lapsrn"
        path_model = find_file_production_and_dev(
            "LapSRN_x" + str(upscale_factor)+".pb")

    super_res = dnn_superres.DnnSuperResImpl_create()
    super_res.readModel(path_model)
    if device == "opencl16":
        super_res.setPreferableTarget(cv2.dnn.DNN_TARGET_OPENCL_FP16)
    elif device == "opencl":
        super_res.setPreferableTarget(cv2.dnn.DNN_TARGET_OPENCL)
    elif device == "cuda16":
        # opencv must be built with cuda
        super_res.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        super_res.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)

    super_res.setModel(model_name, upscale_factor)
    return super_res

def check_compatibility(supported_file_dropped_number, not_supported_file_dropped_number, supported_video_dropped_number):
    all_supported = True
    single_file = False
    multiple_files = False
    video_files = False
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

def OpenCV_AI_upscale_image(image_path, AI_model, upscale_factor, device):
    super_res = prepare_opencv_superresolution_model(
        AI_model, upscale_factor, device)
    result = super_res.upsample(cv2.imread(image_path))
    upscaled_image_path = image_path.replace(
        ".png", "") + "_" + AI_model + "_x" + str(upscale_factor) + ".png"
    cv2.imwrite(upscaled_image_path, result)

def OpenCV_AI_upscale_multiple_images(image_list, AI_model, upscale_factor, device):
    super_res = prepare_opencv_superresolution_model(
        AI_model, upscale_factor, device)
    for image in image_list:
        result_path = image.replace(
            ".png", "") + "_" + AI_model + "_x" + str(upscale_factor) + ".png"
        result = super_res.upsample(cv2.imread(image))
        cv2.imwrite(result_path, result)

def OpenCV_AI_upscale_video_frames(video_frames_list, AI_model, upscale_factor, device):
    super_res = prepare_opencv_superresolution_model(
        AI_model, upscale_factor, device)
    for image in video_frames_list:
        result_path = image.replace(
            ".png", "") + "_" + AI_model + "_x" + str(upscale_factor) + ".png"
        result = super_res.upsample(cv2.imread(image))
        cv2.imwrite(result_path, result)
        video_frames_upscaled_list.append(result_path)

def thread_wait_for_single_file(image_path, _):
    start = timer()
    while not os.path.exists(image_path):
        time.sleep(1)

    if os.path.isfile(image_path):
        end = timer()
        info_string.set(
            "Upscale completed [" + str(round(end - start)) + " sec.]")
        place_upscale_button()
        return

def thread_wait_for_multiple_file(image_list, AI_model, upscale_factor):
    start = timer()

    how_many_images = len(image_list)
    counter_done = 0
    for image in image_list:
        while not os.path.exists(image.replace(".png", "") + "_" + AI_model + "_x" + str(upscale_factor) + ".png"):
            time.sleep(1)

        if os.path.isfile(image.replace(".png", "") + "_" + AI_model + "_x" + str(upscale_factor) + ".png"):
            counter_done += 1
            info_string.set("Upscaled " + str(counter_done) +
                            "/" + str(how_many_images))

        if counter_done == how_many_images:
            end = timer()
            info_string.set(
                "Upscale completed [" + str(round(end - start)) + " sec.]")
            place_upscale_button()
            return

def thread_wait_for_videoframes_and_video_reconstruct(video_frames_list, video_frames_upscaled_list, AI_model, upscale_factor, original_video_path):
    start = timer()

    how_many_images = len(video_frames_list)  # original frames
    counter_done = 0
    for image in video_frames_upscaled_list:  # count upscaled frames
        while not os.path.exists(image):
            time.sleep(1)

        if os.path.isfile(image):
            counter_done += 1
            info_string.set("Upscaled " + str(counter_done) +
                            "/" + str(how_many_images))

        if counter_done == how_many_images:
            video_reconstruction_by_frames(original_video_path,
                                           video_frames_upscaled_list,
                                           AI_model,
                                           upscale_factor)
            end = timer()
            info_string.set(
                "Video upscale completed [" + str(round(end - start)) + " sec.]")
            place_upscale_button()
            return

def stop_button_command():
    global process_upscale
    process_upscale.terminate()
    info_string.set("Stopped")
    place_upscale_button()

def convert_frames_list_uspcaled(video_frames_list, AI_model, upscale_factor):
    video_frames_upscaled_list = []
    for image in video_frames_list:
        result_path = image.replace(
            ".png", "") + "_" + AI_model + "_x" + str(upscale_factor) + ".png"
        video_frames_upscaled_list.append(result_path)

    return video_frames_upscaled_list

def from_string_to_image_list(event):
    image_list = str(event.data).replace("{", "").replace("}", "")

    for file_type in supported_file_list:
        image_list = image_list.replace(file_type, file_type+"\n")

    image_list = image_list.split("\n")
    image_list.pop()  # to remove last void element

    return image_list

def convert_only_image_filenames(image_list):
    list_converted = []
    for image in image_list:
        image = image.strip().replace("{", "").replace("}", "")
        for file_type in supported_file_list:
            image = image.replace(file_type, ".png")

        list_converted.append(image)

    return list(dict.fromkeys(list_converted))

def convert_multi_images_to_png(image_list, _):
    global actual_step

    actual_step = "converting"
    info_string.set("Converting images...")

    for image in image_list:
        image = image.strip()
        image_prepared = convert_single_image_to_png(image)

    actual_step = "ready"
    info_string.set("")

def convert_single_image_to_png(image_to_prepare):
    image_to_prepare = image_to_prepare.replace("{", "").replace("}", "")
    if ".png" in image_to_prepare:
        return image_to_prepare
    else:
        new_image_path = image_to_prepare
        for file_type in supported_file_list:
            new_image_path = new_image_path.replace(file_type, ".png")

        image_to_convert = cv2.imread(image_to_prepare)
        cv2.imwrite(new_image_path, image_to_convert)
        return new_image_path

# ---------------------- GUI related ----------------------

def clear_drag_drop_background():
    drag_drop = ttk.Label(root,
                          ondrop=function_drop,
                          relief="flat",
                          background=drag_drop_background,
                          foreground=drag_drop_text_color)
    drag_drop.place(x=left_bar_width, y=0,
                    width=drag_drop_width, height=drag_drop_height)

def show_video_info_with_drag_drop(video_path):

    clear_drag_drop_background()

    cap = cv2.VideoCapture(video_path)
    width = round(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # float `width`
    height = round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # float `height`
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    file_size = Path(video_path).stat().st_size
    duration = num_frames/frame_rate
    minutes = int(duration/60)
    seconds = duration % 60
    path_as_list = video_path.split("/")
    video_name = str(path_as_list[-1])
    cap.release()

    file_description = ("\n"
                        + " >  Path: " +
                        video_path.replace(video_name, "") + "\n\n"
                        + " >  File: " + video_name + "\n\n"
                        + " >  Resolution: " +
                        str(width) + "x" + str(height) + "\n\n"
                        + " >  Size: " +
                        str(truncate(file_size / 1048576, 2)) + " MB" + "\n\n"
                        + " >  Duration: " +
                        str(minutes) + ':' + str(round(seconds)) + "\n\n"
                        + " >  Frames: " + str(num_frames) + "\n\n"
                        + " >  Fps: " + str(round(frame_rate)) + "\n\n")

    video_header = ttk.Label(root,
                             text="Video info",
                             ondrop=function_drop,
                             font=(default_font, round(
                                 12 * font_scale), "bold"),  # 11
                             anchor="center",
                             relief="flat",
                             justify="center",
                             background="#181818",
                             foreground="#D3D3D3")
    video_header.place(x=left_bar_width + drag_drop_width/2 - 750/2,
                       y=drag_drop_height/2 - 400/2 - 45,
                       width=200,
                       height=35)

    video_info_space = ttk.Label(root,
                                 text=file_description,
                                 ondrop=function_drop,
                                 font=(default_font, round(
                                     12 * font_scale), "bold"),
                                 anchor="n",
                                 relief="flat",
                                 justify="left",
                                 background="#181818",
                                 foreground="#D3D3D3",
                                 wraplength=750 - 10)
    video_info_space.place(x=left_bar_width + drag_drop_width/2 - 750/2,
                           y=drag_drop_height/2 - 400/2,
                           width=750,
                           height=380)

def show_list_images_in_GUI_with_drag_drop(image_list_prepared):
    clear_drag_drop_background()
    final_string = "\n"
    counter_img = 0
    for elem in image_list_prepared:
        counter_img += 1
        if counter_img <= 16:
            # add first 16 files in list
            path_as_list = elem.split("/")
            img_name = str(path_as_list[-1])
            final_string += (" >  " + img_name
                             + "\n")
        else:
            final_string += "and others... \n"
            break

    list_height = 420
    list_width = 750

    list_header = ttk.Label(root,
                            text="Image list",
                            ondrop=function_drop,
                            font=(default_font, round(
                                12 * font_scale), "bold"),  # 11
                            anchor="center",
                            relief="flat",
                            justify="center",
                            background="#181818",
                            foreground="#D3D3D3")
    list_header.place(x=left_bar_width + drag_drop_width/2 - list_width/2,
                      y=drag_drop_height/2 - list_height/2 - 45,
                      width=200,
                      height=35)

    multiple_images_list = ttk.Label(root,
                                     text=final_string,
                                     ondrop=function_drop,
                                     font=(default_font, round(
                                         11 * font_scale)),  # 9
                                     anchor="n",
                                     relief="flat",
                                     justify="left",
                                     background="#181818",
                                     foreground="#D3D3D3",
                                     wraplength=list_width - 10)
    multiple_images_list.place(x=left_bar_width + drag_drop_width/2 - list_width/2,
                               y=drag_drop_height/2 - list_height/2,
                               width=list_width,
                               height=list_height)

    # then image counter
    multiple_images_label = ttk.Label(root,
                                      text=str(len(image_list_prepared)
                                               ) + " images ",
                                      ondrop=function_drop,
                                      font=(default_font, round(
                                          12 * font_scale), "bold"),
                                      anchor="center",
                                      relief="flat",
                                      justify="center",
                                      background="#181818",
                                      foreground="#D3D3D3")
    multiple_images_label.place(x=left_bar_width + drag_drop_width/2 - 400/2,
                                y=drag_drop_height/2 + 500/2 + 25,
                                width=400,
                                height=42)

def show_image_in_GUI_with_drag_drop(image_to_show):
    global image
    clear_drag_drop_background()

    image = tk.PhotoImage(file=image_to_show)
    drag_drop_and_images = ttk.Label(root,
                                     text="",
                                     image=image,
                                     ondrop=function_drop,
                                     font=(default_font, round(
                                         10 * font_scale)),
                                     anchor="center",
                                     relief="flat",
                                     justify="center",
                                     background=drag_drop_background,
                                     foreground="#202020")
    drag_drop_and_images.place(x=left_bar_width + drag_drop_width/2 - show_image_width/2,
                               y=drag_drop_height/2 - show_image_height/2 - image_text_height+1,
                               width=show_image_width,
                               height=show_image_height)

def place_fileName_label(image_path):
    path_as_list = image_path.split("/")
    img_name = str(path_as_list[-1])
    img = cv2.imread(image_path.replace("{", "").replace("}", ""))
    width = round(img.shape[1])
    height = round(img.shape[0])
    file_size = Path(image_path).stat().st_size

    file_name_string.set(img_name
                         + " | [" + str(width) + "x" + str(height) + "]"
                         + " | " + str(truncate(file_size / 1048576, 2)) + " MB")
    drag_drop = ttk.Label(root,
                          font=(default_font, round(11 * font_scale), "bold"),
                          textvar=file_name_string,
                          relief="flat",
                          justify="center",
                          background="#181818",
                          foreground="#D3D3D3",
                          anchor="center")

    drag_drop.place(x=left_bar_width + drag_drop_width/2 - image_text_width/2,
                    y=drag_drop_height - image_text_height - 24,
                    width=image_text_width,
                    height=image_text_height + 5)

# ---------------------- Buttons ----------------------

def place_upscale_button():
    # UPSCALE BUTTON
    Upscale_button = tk.Button(root)
    Upscale_button["bg"] = "#1e9fff"
    ft = tkFont.Font(family=default_font,
                     size=round(12 * font_scale),
                     weight='bold')
    Upscale_button["font"] = ft
    Upscale_button["fg"] = "#202020"
    Upscale_button["justify"] = "center"
    Upscale_button["text"] = "Upscale"
    Upscale_button["relief"] = "flat"
    Upscale_button.place(x=left_bar_width/2 - (button_width + 10)/2,
                         y=left_bar_height - 50 - 25/2,
                         width=button_width + 10,
                         height=42)
    Upscale_button["command"] = lambda: upscale_button_command()

def place_stop_button():
    # UPSCALE BUTTON
    Upscale_button = tk.Button(root)
    Upscale_button["bg"] = "#FF4433"
    ft = tkFont.Font(family=default_font,
                     size=round(12 * font_scale),
                     weight='bold')
    Upscale_button["font"] = ft
    Upscale_button["fg"] = "#202020"
    Upscale_button["justify"] = "center"
    Upscale_button["text"] = "Stop upscaling"
    Upscale_button["relief"] = "flat"
    Upscale_button.place(x=left_bar_width/2 - (button_width + 10)/2,
                         y=left_bar_height - 50 - 25/2,
                         width=button_width + 10,
                         height=42)
    Upscale_button["command"] = lambda: stop_button_command()

def place_ESPCN_button(root, background_color, text_color):
    ft = tkFont.Font(family=default_font,
                     size=round(11 * font_scale),
                     weight="bold")
    ESPCN_button = tk.Button(root)
    ESPCN_button["anchor"] = "center"
    ESPCN_button["bg"] = background_color
    ESPCN_button["font"] = ft
    ESPCN_button["fg"] = text_color
    ESPCN_button["justify"] = "center"
    ESPCN_button["text"] = "ESPCN"
    ESPCN_button["relief"] = "flat"
    ESPCN_button["activebackground"] = "#ffbf00"
    if background_color == "#ffbf00":
        ESPCN_button.place(x=left_bar_width/2 - (button_width-1)/2,
                           y=button_2_y,
                           width=button_width-1,
                           height=button_height-1)
    else:
        ESPCN_button.place(x=left_bar_width/2 - button_width/2,
                           y=button_2_y,
                           width=button_width,
                           height=button_height)
    ESPCN_button["command"] = lambda input = "ESPCN": choose_model_ESPCN(input)

def place_FSRCNN_button(root, background_color, text_color):
    ft = tkFont.Font(family=default_font,
                     size=round(11 * font_scale),
                     weight="bold")
    FSRCNN_button = tk.Button(root)
    FSRCNN_button["anchor"] = "center"
    FSRCNN_button["bg"] = background_color
    FSRCNN_button["font"] = ft
    FSRCNN_button["fg"] = text_color
    FSRCNN_button["justify"] = "center"
    FSRCNN_button["text"] = "FSRCNN"
    FSRCNN_button["relief"] = "flat"
    FSRCNN_button["activebackground"] = "#ffbf00"
    if background_color == "#ffbf00":
        FSRCNN_button.place(x=left_bar_width/2 - (button_width-1)/2,
                            y=button_1_y,
                            width=button_width-1,
                            height=button_height-1)
    else:
        FSRCNN_button.place(x=left_bar_width/2 - button_width/2,
                            y=button_1_y,
                            width=button_width,
                            height=button_height)
    FSRCNN_button["command"] = lambda input = "FSRCNN": choose_model_FSRCNN(
        input)

def place_LapSRN_button(root, background_color, text_color):
    ft = tkFont.Font(family=default_font,
                     size=round(11 * font_scale),
                     weight="bold")
    LapSRN_button = tk.Button(root)
    LapSRN_button["anchor"] = "center"
    LapSRN_button["bg"] = background_color
    LapSRN_button["font"] = ft
    LapSRN_button["fg"] = text_color
    LapSRN_button["justify"] = "center"
    LapSRN_button["text"] = "LAPSRN"
    LapSRN_button["relief"] = "flat"
    LapSRN_button["activebackground"] = "#ffbf00"
    if background_color == "#ffbf00":
        LapSRN_button.place(x=left_bar_width/2 - (button_width-1)/2,
                            y=button_3_y,
                            width=button_width-1,
                            height=button_height-1)
    else:
        LapSRN_button.place(x=left_bar_width/2 - button_width/2,
                            y=button_3_y,
                            width=button_width,
                            height=button_height)
    LapSRN_button["command"] = lambda input = "LapSRN": choose_model_LapSRN(
        input)

def choose_model_ESPCN(choosed_model):
    global AI_model
    AI_model = choosed_model

    default_button_color = "#484848"
    default_text_color = "#DCDCDC"
    selected_button_color = "#ffbf00"
    selected_text_color = "#202020"

    place_ESPCN_button(root, selected_button_color,
                       selected_text_color)  # changing
    place_FSRCNN_button(root, default_button_color, default_text_color)
    place_LapSRN_button(root, default_button_color, default_text_color)

def choose_model_FSRCNN(choosed_model):
    global AI_model
    AI_model = choosed_model

    default_button_color = "#484848"
    default_text_color = "#DCDCDC"
    selected_button_color = "#ffbf00"
    selected_text_color = "#202020"

    place_ESPCN_button(root, default_button_color, default_text_color)
    place_FSRCNN_button(root, selected_button_color,
                        selected_text_color)  # changing
    place_LapSRN_button(root, default_button_color, default_text_color)

def choose_model_LapSRN(choosed_model):
    global AI_model
    AI_model = choosed_model

    default_button_color = "#484848"
    default_text_color = "#DCDCDC"
    selected_button_color = "#ffbf00"
    selected_text_color = "#202020"

    place_ESPCN_button(root, default_button_color, default_text_color)
    place_FSRCNN_button(root, default_button_color, default_text_color)
    place_LapSRN_button(root, selected_button_color,
                        selected_text_color)  # changing

def place_upscale_factor_button_x2(background_color, text_color):
    ft = tkFont.Font(family=default_font,
                     size=round(11 * font_scale),
                     weight="bold")
    Factor_x2_button = tk.Button(root)
    Factor_x2_button["anchor"] = "center"
    Factor_x2_button["bg"] = background_color
    Factor_x2_button["font"] = ft
    Factor_x2_button["fg"] = text_color
    Factor_x2_button["justify"] = "center"
    Factor_x2_button["text"] = "x2"
    Factor_x2_button["relief"] = "flat"
    Factor_x2_button["activebackground"] = "#ffbf00"
    Factor_x2_button.place(x=left_bar_width/2 + left_bar_width/4 - 85,
                           y=437,
                           width=54,
                           height=34)
    Factor_x2_button["command"] = lambda: choose_upscale_x2()

def place_upscale_factor_button_x4(background_color, text_color):
    ft = tkFont.Font(family=default_font,
                     size=round(11 * font_scale),
                     weight="bold")
    Factor_x4_button = tk.Button(root)
    Factor_x4_button["anchor"] = "center"
    Factor_x4_button["bg"] = background_color
    Factor_x4_button["font"] = ft
    Factor_x4_button["fg"] = text_color
    Factor_x4_button["justify"] = "center"
    Factor_x4_button["text"] = "x4"
    Factor_x4_button["relief"] = "flat"
    Factor_x4_button["activebackground"] = "#ffbf00"
    Factor_x4_button.place(x=left_bar_width/2 + left_bar_width/4 - 25,
                           y=437,
                           width=54,
                           height=34)
    Factor_x4_button["command"] = lambda: choose_upscale_x4()

def choose_upscale_x2():
    global upscale_factor
    upscale_factor = 2

    default_button_color = "#484848"
    default_text_color = "#DCDCDC"
    selected_button_color = "#ffbf00"
    selected_text_color = "#202020"

    place_upscale_factor_button_x2(
        selected_button_color, selected_text_color)  # selected
    place_upscale_factor_button_x4(
        default_button_color, default_text_color)   # not selected

def choose_upscale_x4():
    global upscale_factor
    upscale_factor = 4

    default_button_color = "#484848"
    default_text_color = "#DCDCDC"
    selected_button_color = "#ffbf00"
    selected_text_color = "#202020"

    place_upscale_factor_button_x2(
        default_button_color, default_text_color)   # not selected
    place_upscale_factor_button_x4(
        selected_button_color, selected_text_color)  # selected

def place_upscale_backend_cpu(background_color, text_color):
    ft = tkFont.Font(family=default_font,
                     size=round(11 * font_scale),
                     weight="bold")
    Backend_cpu_button = tk.Button(root)
    Backend_cpu_button["anchor"] = "center"
    Backend_cpu_button["justify"] = "center"
    Backend_cpu_button["bg"] = background_color
    Backend_cpu_button["font"] = ft
    Backend_cpu_button["fg"] = text_color
    Backend_cpu_button["text"] = "cpu"
    Backend_cpu_button["relief"] = "flat"
    Backend_cpu_button["activebackground"] = "#ffbf00"
    Backend_cpu_button.place(x=left_bar_width/2 + left_bar_width/4 - 85,
                             y=522,
                             width=54,
                             height=34)
    Backend_cpu_button["command"] = lambda: choose_backend_cpu()

def place_upscale_backend_opencl(background_color, text_color):
    ft = tkFont.Font(family=default_font,
                     size=round(11 * font_scale),
                     weight="bold")
    Backend_cpu_button = tk.Button(root)
    Backend_cpu_button["anchor"] = "center"
    Backend_cpu_button["justify"] = "center"
    Backend_cpu_button["bg"] = background_color
    Backend_cpu_button["font"] = ft
    Backend_cpu_button["fg"] = text_color
    Backend_cpu_button["text"] = "gpu"
    Backend_cpu_button["relief"] = "flat"
    Backend_cpu_button["activebackground"] = "#ffbf00"
    Backend_cpu_button.place(x=left_bar_width/2 + left_bar_width/4 - 25,
                             y=522,
                             width=54,
                             height=34)
    Backend_cpu_button["command"] = lambda: choose_backend_opencl()

def choose_backend_cpu():
    global device
    device = "cpu"

    default_button_color = "#484848"
    default_text_color = "#DCDCDC"
    selected_button_color = "#ffbf00"
    selected_text_color = "#202020"

    place_upscale_backend_cpu(selected_button_color, selected_text_color)
    place_upscale_backend_opencl(default_button_color, default_text_color)

def choose_backend_opencl():
    global device
    device = "opencl16"

    default_button_color = "#484848"
    default_text_color = "#DCDCDC"
    selected_button_color = "#ffbf00"
    selected_text_color = "#202020"

    place_upscale_backend_cpu(default_button_color, default_text_color)
    place_upscale_backend_opencl(selected_button_color, selected_text_color)

# ---------------------- /Buttons ----------------------

# ---------------------- /GUI related ----------------------

# ---------------------- /Functions ----------------------


class App:
    def __init__(self, root):
        root.title("   NiceScaler " + version)
        width = window_width
        height = window_height
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height,
                                    (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        logo = PhotoImage(file=find_file_production_and_dev(
            "logo_shadow_little.png"))
        root.iconphoto(False, logo)

        # BIG BLACK BAR
        Left_container = tk.Label(root)
        Left_container["anchor"] = "e"
        Left_container["bg"] = "#202020"
        Left_container["cursor"] = "arrow"
        Left_container["justify"] = "center"
        Left_container["relief"] = "flat"
        Left_container.place(x=0, y=0, width=left_bar_width,
                             height=left_bar_height)

        # TITLE BACKGROUND
        Title_borders = tk.Label(root)
        Title_borders["bg"] = "#0077b6"
        Title_borders["justify"] = "center"
        Title_borders["relief"] = "flat"
        Title_borders.place(x=0,
                            y=0,
                            width=left_bar_width,
                            height=175)

        # TITLE
        ft = tkFont.Font(family=default_font,
                         size=round(20 * font_scale),
                         weight="bold"),
        Title = tk.Label(root)
        Title["bg"] = "#0077b6"
        Title["font"] = ft
        Title["fg"] = "#181818"
        Title["anchor"] = "center"
        Title["text"] = "NiceScaler"
        Title.place(x=0,
                    y=64,
                    width=left_bar_width,
                    height=60)

        global logo_git
        logo_git = PhotoImage(
            file=find_file_production_and_dev("github_shadow_45.png"))
        logo_git_label = tk.Button(root)
        logo_git_label['image'] = logo_git
        logo_git_label["justify"] = "center"
        logo_git_label["bg"] = "#0077b6"
        logo_git_label["relief"] = "flat"
        logo_git_label["activebackground"] = "#0077b6"
        logo_git_label.place(x=left_bar_width/2 - 55,
                             y=12,
                             width=50,
                             height=50)
        logo_git_label["command"] = lambda: opengithub()

        global logo_paypal
        logo_paypal = PhotoImage(
            file=find_file_production_and_dev("paypal_shadow_50.png"))
        logo_paypal_label = tk.Button(root)
        logo_paypal_label['image'] = logo_paypal
        logo_paypal_label["justify"] = "center"
        logo_paypal_label["bg"] = "#0077b6"
        logo_paypal_label["relief"] = "flat"
        logo_paypal_label["activebackground"] = "#0077b6"
        logo_paypal_label["borderwidth"] = 1
        logo_paypal_label.place(x=left_bar_width/2 + 5,
                                y=12,
                                width=50,
                                height=50)
        logo_paypal_label["command"] = lambda: openpaypal()

        # SECTION TO CHOOSE MODEL
        IA_selection_borders = tk.Label(root)
        IA_selection_borders["bg"] = "#181818"
        IA_selection_borders["justify"] = "center"
        IA_selection_borders["relief"] = "flat"
        IA_selection_borders.place(x=left_bar_width/2 - 350/2,
                                   y=128,
                                   width=350,
                                   height=270)

        ft = tkFont.Font(family=default_font,
                         size=round(12 * font_scale),
                         weight="bold")
        IA_selection_title = tk.Label(root)
        IA_selection_title["bg"] = "#181818"
        IA_selection_title["font"] = ft
        IA_selection_title["fg"] = "#DCDCDC"
        IA_selection_title["anchor"] = "w"
        IA_selection_title["justify"] = "center"
        IA_selection_title["relief"] = "flat"
        IA_selection_title["text"] = "      AI models"
        IA_selection_title.place(x=left_bar_width/2 - 174,
                                 y=140,
                                 width=348,
                                 height=40)

        # BUTTONS
        default_button_color = "#484848"
        default_text_color = "#DCDCDC"
        selected_button_color = "#ffbf00"
        selected_text_color = "#202020"

        place_ESPCN_button(root, default_button_color, default_text_color)
        place_FSRCNN_button(root, selected_button_color, selected_text_color)
        place_LapSRN_button(root, default_button_color, default_text_color)

        # SECTION TO CHOOSE UPSCALE FACTOR
        Upscale_fact_selection_borders = tk.Label(root)
        Upscale_fact_selection_borders["bg"] = "#181818"
        Upscale_fact_selection_borders["justify"] = "center"
        Upscale_fact_selection_borders["relief"] = "flat"
        Upscale_fact_selection_borders.place(x=left_bar_width/2 - 350/2,
                                             y=418,
                                             width=350,
                                             height=70)

        place_upscale_factor_button_x2(
            selected_button_color, selected_text_color)
        place_upscale_factor_button_x4(
            default_button_color, default_text_color)

        ft = tkFont.Font(family=default_font,
                         size=round(12 * font_scale),
                         weight="bold")
        Upscale_fact_selection_title = tk.Label(root)
        Upscale_fact_selection_title["bg"] = "#181818"
        Upscale_fact_selection_title["font"] = ft
        Upscale_fact_selection_title["fg"] = "#DCDCDC"
        Upscale_fact_selection_title["anchor"] = "w"
        Upscale_fact_selection_title["justify"] = "center"
        Upscale_fact_selection_title["relief"] = "flat"
        Upscale_fact_selection_title["text"] = "      Upscale factor"
        Upscale_fact_selection_title.place(x=left_bar_width/2 - 175,
                                           y=432,
                                           width=155,
                                           height=40)

        # AI BACKEND
        Upscale_backend_selection_borders = tk.Label(root)
        Upscale_backend_selection_borders["bg"] = "#181818"
        Upscale_backend_selection_borders["justify"] = "center"
        Upscale_backend_selection_borders["relief"] = "flat"
        Upscale_backend_selection_borders.place(x=left_bar_width/2 - 350/2,
                                                y=505,
                                                width=350,
                                                height=70)

        place_upscale_backend_cpu(selected_button_color, selected_text_color)
        place_upscale_backend_opencl(default_button_color, default_text_color)

        ft = tkFont.Font(family=default_font,
                         size=round(12 * font_scale),
                         weight="bold")
        Upscale_backend_selection_title = tk.Label(root)
        Upscale_backend_selection_title["bg"] = "#181818"
        Upscale_backend_selection_title["font"] = ft
        Upscale_backend_selection_title["fg"] = "#DCDCDC"
        Upscale_backend_selection_title["anchor"] = "w"
        Upscale_backend_selection_title["justify"] = "center"
        Upscale_backend_selection_title["relief"] = "flat"
        Upscale_backend_selection_title["text"] = "      AI backend"
        Upscale_backend_selection_title.place(x=left_bar_width/2 - 175,
                                              y=520,
                                              width=155,
                                              height=40)

        # MESSAGE
        info_string.set("")
        error_message_label = ttk.Label(root,
                                        font=(default_font, round(
                                            11 * font_scale)),
                                        textvar=info_string,
                                        relief="flat",
                                        justify="center",
                                        background="#202020",
                                        foreground="#ffbf00",
                                        anchor="center")
        error_message_label.place(x=0,
                                  y=618,
                                  width=left_bar_width,
                                  height=30)

        # UPSCALE BUTTON
        place_upscale_button()

        # DRAG & DROP WIDGET
        drag_drop = ttk.Label(root,
                              text=" DROP FILES HERE \n"
                              + " ____________________________________________ \n\n"
                              + " IMAGE  [ jpg - png - tif - bmp - webp ]                      \n\n"
                              + " VIDEO  [ mp4 - webm - mkv - flv - gif - avi - mov ] \n\n\n"
                              + "    thank you for supporting this project   😋",
                              ondrop=function_drop,
                              font=(default_font, round(
                                  13 * font_scale), "normal"),
                              anchor="center",
                              relief="flat",
                              justify="center",
                              background=drag_drop_background,
                              foreground=drag_drop_text_color)
        drag_drop.place(x=left_bar_width, y=0,
                        width=drag_drop_width, height=drag_drop_height)

        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        value = ctypes.c_int(2)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, 
            ctypes.byref(value), 
            ctypes.sizeof(value))


if __name__ == "__main__":
    multiprocessing.freeze_support()

    root = tkinterDnD.Tk()
    file_name_string = tk.StringVar()
    info_string = tk.StringVar()

    app = App(root)
    root.update()
    root.mainloop()
