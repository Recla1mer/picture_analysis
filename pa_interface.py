from tkinter import filedialog
from tkinter import ttk
from tkinter import *
from PIL import ImageTk, Image

import os
import copy
import sys
import numpy as np

import pa_plot as pp
import pa

TEMP_PLOTS_DIRECTORY_NAME = "Temporary_Plots/"
SHOW_IMAGES_DIRECTORY_NAME = "Temporarily_Resized_Images/"
Temp_TEXT_DIRECTORY_NAME = "Temporary_txt_Files/"

SAVE_POSITION_DIRECTORY = "Position_dependent/"
SAVE_POSITION_FILE = "last_pd"
SAVE_VOLT_DIRECTORY = "Voltage_dependent/"
SAVE_VOLT_FILE = "last_vd"
SAVE_EXP_DIRECTORY = "Exponential_fit/"
SAVE_EXP_FILE = "last_ef"

if not os.path.isdir(TEMP_PLOTS_DIRECTORY_NAME):
    os.mkdir(TEMP_PLOTS_DIRECTORY_NAME)
if not os.path.isdir(SHOW_IMAGES_DIRECTORY_NAME):
    os.mkdir(SHOW_IMAGES_DIRECTORY_NAME)
if not os.path.isdir(Temp_TEXT_DIRECTORY_NAME):
    os.mkdir(Temp_TEXT_DIRECTORY_NAME)

#set looks of ui interface
window_bg = "gray"

frame_settings = {
    "bg": "white",
    "relief": "flat",
    "borderwidth": 1,
    "highlightbackground": "black",
    "highlightthickness": 1,
    "width": 622.1,
    "height": 70
}

button_settings = {
    "relief": "raise",
    "bg": "black",
    "fg": "black",
    "highlightbackground": "light gray",
    "highlightcolor": "black",
    "highlightthickness": 1,
    # "underline": 5,
    # "height": 2,
    # "width": 5,
    # "activebackground": "blue",
    "activeforeground": "blue",
    "font": "TkDefaultFont"
}

entry_settings = {
    "relief": "flat",
    "bg": "white",
    "fg": "black",
    "highlightbackground": "gray",
    "highlightcolor": "blue",
    "highlightthickness": 2
}

label_settings = {
    "relief": "flat",
    "bg": "light gray",
    "fg": "black",
    "highlightbackground": "black",
    "highlightcolor": "black",
    "highlightthickness": 0,
    "padx": 20,
    "pady": 2
}

dropdown_settings = {
    "background": "light gray",
    #"activebackground": "red",
    "highlightbackground": "black",
    "highlightcolor": "black",
    "foreground": "black",
    "font": 'TkDefaultFont 14'
}

row_settings = {
    "width": 200
}

#global parameters
# global picture_file_names, picture_voltage_values
# global topx, topy, botx, boty
# global rect_id
# global canvas

global scale_image, image_size_reworked
scale_image = 1
image_size_reworked = False

global picture_file_names, picture_voltage_values
picture_file_names, picture_voltage_values = [], []

global topx, topy, botx, boty, old_topx, old_topy
topx, topy, botx, boty, old_topx, old_topy = 0, 0, 0, 0, 0, 0

global rect_id
rect_id = None

global length_of_pixel
length_of_pixel = 0

global automatic_defect_detect, manually_chosen_borders
automatic_defect_detect = None
manually_chosen_borders = []

global CHANGING_IMG_DIR
CHANGING_IMG_DIR = "Altered_Images/"

global shown_img, auto_img_def, auto_img_good, plot_preview_img
shown_img, auto_img_def, auto_img_good, plot_preview_img = None, None, None, None

global default_defective_row_settings, other_default_settings

default_defective_row_settings = {
    "max_darker_area_height": 50,
    "gray_change_sensivity_ratio_horizontal": 0.2, 
    "gray_change_sensivity_ratio_vertical": 0.2,
    "compare_to_following": 3, 
    "compare_min_value": 10,
    "ignore_whitespace_faults": True,
    "remove_next_to_defective": 2
}

other_default_settings = {
    "show_image": False,
    "filetype": "tif",
    "check_images_individually": False,
    "pix_to_length": 1.5038, 
    "initial_values": [55,50,1],
    "lines_next_highest": 20,
    "volt_dep_method": "Mean",
    "calc_y_dep": True,
    "remove_at_max": 0.75,
    "reduce_by": 1.5
}

#implement functions for the ui interface

def check_image_size(path_to_directory, picture_filetype = "tif", max_width = 800, max_height = 640):
    """
    """
    global scale_image, image_size_reworked
    if image_size_reworked:
        return
    else:
        image_size_reworked = True

    files = os.listdir(path_to_directory)
    files = pa.remove_other_filetypes(copy.deepcopy(files), filetype=picture_filetype)

    scale_factors = []

    for filename in files:
        path_to_picture = path_to_directory + "/" + filename

        pic = (Image.open(path_to_picture))
        img_trash = ImageTk.PhotoImage(pic)
        img_width = img_trash.width()
        img_height = img_trash.height()
        del img_trash

        scale_height_factor = 1
        scale_width_factor = 1

        if img_width > max_width:
            scale_width_factor = max_width/img_width
        if img_height > max_height:
            scale_height_factor = max_height/img_height
        
        if scale_height_factor > scale_width_factor:
            scale = scale_width_factor
        else:
            scale = scale_height_factor
        
        scale_width = int(scale*img_width)
        scale_height = int(scale*img_height)
        scale_factors.append(scale)
        
        pic = pic.resize((scale_width, scale_height))
        pic.save(SHOW_IMAGES_DIRECTORY_NAME + filename)
    
    scale_image = min(scale_factors)


def open_directory(entry_field):
    """
    Function to collect path
    """
    reset_errors()
    #file = filedialog.askopenfile(mode='r', filetypes=[('Python Files', '*')])
    global intro_read
    if not intro_read:
        global introduction_frame, compute_error_label
        introduction_frame.config(highlightbackground="red", highlightthickness=2)
        compute_error_label.config(fg = "red", text="\n\nYou are not allowed to proceed until I am sure you know how to save your images.")
        return

    directory = filedialog.askdirectory()
    if directory:
        #filepath = os.path.abspath(file.name)
        filepath = os.path.abspath(directory)
        entry_field.delete(0, END)
        entry_field.insert(0, str(filepath))

    global picture_file_names, picture_voltage_values
    picture_file_names, picture_voltage_values = [], []


def retrieve_voltage(path_to_directory, picture_filetype = "tif"):
    """
    Bla
    """
    files = os.listdir(path_to_directory)
    files = pa.remove_other_filetypes(copy.deepcopy(files), filetype=picture_filetype)

    trash = len(picture_filetype)+1

    #retrieve voltage of every picture
    voltage = []
    for filename in files:
        name = filename[:-trash]
        in_number = False
        appended = False
        for char_pos in range(0, len(name)):
            if name[char_pos] in pa.string_integers and not in_number:
                start = char_pos
                in_number = True
            elif name[char_pos] not in pa.string_integers and in_number:
                voltage.append(float(name[start:char_pos]))
                appended = True
                break
        if not appended:
            if not in_number:
                print("Not appended")
            else:
                voltage.append(float(name[start:]))
    
    return files, voltage


#functions for drawing rectangle on canvas


def get_mouse_posn(event):
    global topy, topx
    topx, topy = event.x, event.y


def update_sel_rect(event):
    global botx, boty
    botx, boty = event.x, event.y
    #canvas.coords(rect_id, topx, topy, botx, boty)  # Update selection rect.


def update_rectangle(window, canvas):
    global topx, topy, botx, boty, rect_id, old_topx, old_topy
    canvas.bind('<Button-1>', get_mouse_posn)
    if topx != old_topx or topy != old_topy:
        botx = copy.deepcopy(topx)
        boty = copy.deepcopy(topy)
    canvas.bind('<B1-Motion>', update_sel_rect)
    canvas.delete(rect_id)
    rect_id = canvas.create_rectangle(topx, topy, botx, boty,
                                        dash=(2,2), fill='', outline='white')
    old_topy = copy.deepcopy(topy)
    old_topx = copy.deepcopy(topx)
    window.after(1, lambda: update_rectangle(window, canvas))


#window functions


def Exit_Pixel_length_window(length_direction, area_length, label, window, error_label):
    """
    Bla
    """
    global length_of_pixel, scale_image

    try:
        if length_direction == "left to right":
            length_of_pixel = float(area_length)/abs(topx-botx)
        else:
            length_of_pixel = float(area_length)/abs(topy-boty)
        error_label.config(text="No input errors detected.", fg="green")
        length_of_pixel *= scale_image
    except:
        error_label.config(text="Length of area entry invalid.", fg="red")
        return
    
    label.config(text="Length/Pixel = " + str(round(length_of_pixel,3)) + " \u03BCm")
    window.destroy()


def Pixel_length_window(picture_paths_widget, picture_filetype_widget, label):
    """
    Bla
    """
    #alter frame settings
    frame_settings["width"] = 800
    global picture_file_names, picture_voltage_values
    global topx, topy, botx, boty
    global other_default_settings
    topx, topy, botx, boty = 0, 0, 0, 0

    #check if settings are available
    reset_errors()

    global intro_read
    global browser_frame, compute_error_label, filetype_frame, reopen_prep_button, introduction_frame

    if not intro_read:
        introduction_frame.config(highlightbackground="red", highlightthickness=2)
        compute_error_label.config(fg = "red", text="\n\nYou are not allowed to proceed until I am sure you know how to save your images.")
        return

    try:
        directory_path = picture_paths_widget.get()
        check_image_size(directory_path, picture_filetype_widget.get())
        other_default_settings["filetype"] = picture_filetype_widget.get()
        if len(picture_voltage_values) == 0:
            picture_file_names, picture_voltage_values = retrieve_voltage(directory_path, picture_filetype=picture_filetype_widget.get())
        if len(picture_voltage_values) == 0:
            browser_frame.config(highlightbackground="red", highlightthickness=2)
            filetype_frame.config(highlightbackground="red", highlightthickness=2)
            compute_error_label.config(fg = "red", text="No meaningful image files could be found. There are multiple possible reasons for this to happen:\n\u2219Incorrect path to images\n\u2219Incorrect filetype chosen\n\u2219preparations were not correctly followed")
            reopen_prep_button.pack(padx=5, pady=5)
            return
    except:
        browser_frame.config(highlightbackground="red", highlightthickness=2)
        compute_error_label.config(fg = "red", text="\n\nSomething is off with the entered directory path. Did you type in anything at all?")
        return
    
    path_to_picture = SHOW_IMAGES_DIRECTORY_NAME + picture_file_names[picture_voltage_values.index(max(picture_voltage_values))]

    window_pixel = Toplevel()
    # Set window title
    window_pixel.title("Evaluation of pixel length")
    # Set window size
    window_pixel.geometry("810x865")
    #Set window background color
    window_pixel.config(background = window_bg)

    #introduction
    pixel_intro_frame = Frame(master=window_pixel, **frame_settings)
    pixel_intro_frame.grid(row=0, column=0, padx=5, pady=5)
    pixel_intro_frame.pack_propagate(False)
    Label(master=pixel_intro_frame, text="Choose an area in the picture below by click and drag of which you know the length.\nOnly the position of two parallel area borders matter, please be aware to choose the correct ones.\nOnce this is done and you entered the length, hit \"Confirm\" to finish the process.", **label_settings).pack(padx=5, pady=5)

    #canvas
    pixel_canvas_frame = Frame(master=window_pixel, bg="gray")
    pixel_canvas_frame.grid(row=1, column=0, padx=5, pady=5)

    pic = (Image.open(path_to_picture))
    img = ImageTk.PhotoImage(pic)

    canvas = Canvas(pixel_canvas_frame, width=img.width(), height=img.height(),
                    borderwidth=0, highlightthickness=0)
    canvas.pack(expand=True)
    canvas.img = img  # Keep reference in case this code is put into a function.
    canvas.create_image(0, 0, image=img, anchor=NW)

    #information and confirmation
    frame_settings["height"] = 120
    pixel_info_frame = Frame(master=window_pixel, **frame_settings)
    pixel_info_frame.grid(row=2, column=0, padx=5, pady=5)
    pixel_info_frame.pack_propagate(False)
    Label(master=pixel_info_frame, text="Enter length of area (in \u03BCm):", **label_settings).pack(padx=5, pady=5, side=LEFT, anchor="n")
    pixel_length_entry = Entry(master=pixel_info_frame, width=5, **entry_settings)
    pixel_length_entry.pack(side=LEFT, anchor="n", pady=5, padx=0)
    pixel_length_entry.insert(0, "200")
    OPTIONS_pixel = ["left to right", "down to up"]
    pixel_length_option = StringVar(window_pixel)
    pixel_length_option.set(OPTIONS_pixel[0]) # default value

    drop_pixel_length = OptionMenu(pixel_info_frame, pixel_length_option, *OPTIONS_pixel)
    drop_pixel_length.pack(padx=0, pady=5, side=RIGHT, anchor="n")

    for key in dropdown_settings:
        drop_pixel_length[key] = dropdown_settings[key]
    
    Label(master=pixel_info_frame, text="Length refers to:", **label_settings).pack(padx=5, pady=5, side=RIGHT, anchor="n")

    pixel_length_error = Label(master=pixel_info_frame, text="No input errors detected.", **label_settings)
    pixel_length_error.config(fg="green")
    pixel_length_error.pack(padx=5, pady=5, side=BOTTOM)
    
    finish_pixel_button = Button(pixel_info_frame, text = "Confirm", command = lambda: Exit_Pixel_length_window(pixel_length_option.get(), pixel_length_entry.get(), label, window_pixel, pixel_length_error), **button_settings)
    finish_pixel_button.pack(pady = 5, side=BOTTOM)

    window_pixel.after(1000, lambda: update_rectangle(window_pixel, canvas))
    window_pixel.mainloop()


def auto_confirm_button_function(max_dark_entry, gcsr_h_entry, gcsr_v_entry, ctf_entry, ctmv_entry, rntd_entry, iwf_option, cii_option, ram_entry, rb_entry, error_label, window):
    """
    """
    global default_defective_row_settings, other_default_settings

    try:
        this_setting = float(ram_entry.get())
        if this_setting < 0 or this_setting >= 1:
            error_label.config(text="\"remove_at_max\" must be a decimal number between 0 and 1!", fg="red")
            return
        other_default_settings["remove_at_max"] = this_setting
    except:
        error_label.config(text="\"remove_at_max\" must be a decimal number between 0 and 1!\nWould be a progress if all characters were numbers...", fg="red")
        return
    
    try:
        this_setting = float(rb_entry.get())
        if this_setting <= 1:
            error_label.config(text="\"reduce_by\" must be a decimal number higher than 1!", fg="red")
            return
        other_default_settings["reduce_by"] = this_setting
    except:
        error_label.config(text="\"reduce_by\" must be a decimal number higher than 1!\nWould be a progress if all characters were numbers...", fg="red")
        return

    try:
        this_setting = int(max_dark_entry.get())
        if this_setting < 0:
            error_label.config(text="\"max_darker_area_height\" must be a positive integer!", fg="red")
            return
        default_defective_row_settings["max_darker_area_height"] = this_setting
    except:
        error_label.config(text="\"max_darker_area_height\" must be a positive integer!\nWould be a progress if all characters were numbers...", fg="red")
        return
    
    try:
        this_setting = float(gcsr_h_entry.get())
        if this_setting < 0 or this_setting >= 1:
            error_label.config(text="\"gray_change_sensivity_ratio_horizontal\" must be a decimal number between 0 and 1!", fg="red")
            return
        default_defective_row_settings["gray_change_sensivity_ratio_horizontal"] = this_setting
    except:
        error_label.config(text="\"gray_change_sensivity_ratio_horizontal\" must be a decimal number between 0 and 1!\nWould be a progress if all characters were numbers...", fg="red")
        return
    
    try:
        this_setting = float(gcsr_v_entry.get())
        if this_setting < 0 or this_setting >= 1:
            error_label.config(text="\"gray_change_sensivity_ratio_vertical\" must be a decimal number between 0 and 1!", fg="red")
            return
        default_defective_row_settings["gray_change_sensivity_ratio_vertical"] = this_setting
    except:
        error_label.config(text="\"gray_change_sensivity_ratio_vertical\" must be a decimal number between 0 and 1!\nWould be a progress if all characters were numbers...", fg="red")
        return

    try:
        this_setting = int(ctf_entry.get())
        if this_setting < 0 or this_setting > 20:
            error_label.config(text="\"compare_to_following\" out of valid range!", fg="red")
            return
        default_defective_row_settings["compare_to_following"] = this_setting
    except:
        error_label.config(text="\"compare_to_following\" must be a positive integer!\nWould be a progress if all characters were numbers...", fg="red")
        return
    
    try:
        this_setting = int(ctmv_entry.get())
        if this_setting < 0 or this_setting > 30:
            error_label.config(text="\"compare_min_value\" out of valid range!", fg="red")
            return
        default_defective_row_settings["compare_min_value"] = this_setting
    except:
        error_label.config(text="\"compare_min_value\" must be a positive integer!\nWould be a progress if all characters were numbers...", fg="red")
        return
    
    try:
        this_setting = int(rntd_entry.get())
        if this_setting < 0:
            error_label.config(text="\"remove_next_to_defective\" out of valid range!", fg="red")
            return
        default_defective_row_settings["remove_next_to_defective"] = this_setting
    except:
        error_label.config(text="\"remove_next_to_defective\" must be a positive integer!\nWould be a progress if all characters were numbers...", fg="red")
        return
    
    if iwf_option.get() == "True":
        default_defective_row_settings["ignore_whitespace_faults"] = True
    else:
        default_defective_row_settings["ignore_whitespace_faults"] = False
    
    if cii_option.get() == "True":
        other_default_settings["check_images_individually"] = True
    else:
        other_default_settings["check_images_individually"] = False

    error_label.config(text="Everything is fine! Exiting...", fg="green")
    window.destroy()


def auto_preview_change_img_button_function(img_cont_1, canvas_1, path_1, img_cont_2, canvas_2, path_2, width, height):
    """
    """
    global auto_img_def, auto_img_good

    auto_img_def = ImageTk.PhotoImage(Image.open(path_1).resize([width, height]))
    canvas_1.itemconfig(img_cont_1, image=auto_img_def)

    auto_img_good = ImageTk.PhotoImage(Image.open(path_2).resize([width, height]))
    canvas_2.itemconfig(img_cont_2, image=auto_img_good)


def auto_preview_button_function(max_dark_entry, gcsr_h_entry, gcsr_v_entry, ctf_entry, ctmv_entry, rntd_entry, iwf_option, cii_option, ram_entry, rb_entry, error_label, dir, files, volts):
    """
    """
    global default_defective_row_settings, other_default_settings

    try:
        this_setting = float(ram_entry.get())
        if this_setting < 0 or this_setting >= 1:
            error_label.config(text="\"remove_at_max\" must be a decimal number between 0 and 1!", fg="red")
            return
        other_default_settings["remove_at_max"] = this_setting
    except:
        error_label.config(text="\"remove_at_max\" must be a decimal number between 0 and 1!\nWould be a progress if all characters were numbers...", fg="red")
        return
    
    try:
        this_setting = float(rb_entry.get())
        if this_setting <= 1:
            error_label.config(text="\"reduce_by\" must be a decimal number higher than 1!", fg="red")
            return
        other_default_settings["reduce_by"] = this_setting
    except:
        error_label.config(text="\"reduce_by\" must be a decimal number higher than 1!\nWould be a progress if all characters were numbers...", fg="red")
        return

    try:
        this_setting = int(max_dark_entry.get())
        if this_setting < 0:
            error_label.config(text="\"max_darker_area_height\" must be a positive integer!", fg="red")
            return
        default_defective_row_settings["max_darker_area_height"] = this_setting
    except:
        error_label.config(text="\"max_darker_area_height\" must be a positive integer!\nWould be a progress if all characters were numbers...", fg="red")
        return
    
    try:
        this_setting = float(gcsr_h_entry.get())
        if this_setting < 0 or this_setting >= 1:
            error_label.config(text="\"gray_change_sensivity_ratio_horizontal\" must be a decimal number between 0 and 1!", fg="red")
            return
        default_defective_row_settings["gray_change_sensivity_ratio_horizontal"] = this_setting
    except:
        error_label.config(text="\"gray_change_sensivity_ratio_horizontal\" must be a decimal number between 0 and 1!\nWould be a progress if all characters were numbers...", fg="red")
        return
    
    try:
        this_setting = float(gcsr_v_entry.get())
        if this_setting < 0 or this_setting >= 1:
            error_label.config(text="\"gray_change_sensivity_ratio_vertical\" must be a decimal number between 0 and 1!", fg="red")
            return
        default_defective_row_settings["gray_change_sensivity_ratio_vertical"] = this_setting
    except:
        error_label.config(text="\"gray_change_sensivity_ratio_vertical\" must be a decimal number between 0 and 1!\nWould be a progress if all characters were numbers...", fg="red")
        return

    try:
        this_setting = int(ctf_entry.get())
        if this_setting < 0 or this_setting > 20:
            error_label.config(text="\"compare_to_following\" out of valid range!", fg="red")
            return
        default_defective_row_settings["compare_to_following"] = this_setting
    except:
        error_label.config(text="\"compare_to_following\" must be a positive integer!\nWould be a progress if all characters were numbers...", fg="red")
        return
    
    try:
        this_setting = int(ctmv_entry.get())
        if this_setting < 0 or this_setting > 30:
            error_label.config(text="\"compare_min_value\" out of valid range!", fg="red")
            return
        default_defective_row_settings["compare_min_value"] = this_setting
    except:
        error_label.config(text="\"compare_min_value\" must be a positive integer!\nWould be a progress if all characters were numbers...", fg="red")
        return
    
    try:
        this_setting = int(rntd_entry.get())
        if this_setting < 0:
            error_label.config(text="\"remove_next_to_defective\" out of valid range!", fg="red")
            return
        default_defective_row_settings["remove_next_to_defective"] = this_setting
    except:
        error_label.config(text="\"remove_next_to_defective\" must be a positive integer!\nWould be a progress if all characters were numbers...", fg="red")
        return
    
    if iwf_option.get() == "True":
        default_defective_row_settings["ignore_whitespace_faults"] = True
    else:
        default_defective_row_settings["ignore_whitespace_faults"] = False
    
    if cii_option.get() == "True":
        other_default_settings["check_images_individually"] = True
    else:
        other_default_settings["check_images_individually"] = False

    error_label.config(text="Everything seems fine... yet.", fg="green")

    global auto_img_def, auto_img_good, CHANGING_IMG_DIR, scale_image

    if not os.path.isdir(SHOW_IMAGES_DIRECTORY_NAME + CHANGING_IMG_DIR):
        os.mkdir(SHOW_IMAGES_DIRECTORY_NAME + CHANGING_IMG_DIR)
    else:
        del_files = os.listdir(SHOW_IMAGES_DIRECTORY_NAME + CHANGING_IMG_DIR)
        for del_file in del_files:
            if os.path.exists(SHOW_IMAGES_DIRECTORY_NAME + CHANGING_IMG_DIR + del_file):
                os.remove(SHOW_IMAGES_DIRECTORY_NAME + CHANGING_IMG_DIR + del_file)

    if other_default_settings["check_images_individually"]:
        for filename in range(0, len(files)):
            path = dir + "/" + files[filename]
            this_image_array = pa.get_grayscale(path)
            new_auto_img_def, new_auto_img_good = pa.find_defective(this_image_array, ret_img=True, path=path, **default_defective_row_settings)

            def_path = SHOW_IMAGES_DIRECTORY_NAME + CHANGING_IMG_DIR + "def_" + str(volts[filename]) + ".tif"
            good_path = SHOW_IMAGES_DIRECTORY_NAME + CHANGING_IMG_DIR + "good_" + str(volts[filename]) + ".tif"
            new_auto_img_def.save(def_path)
            new_auto_img_good.save(good_path)

        factor = 560/len(this_image_array[0])
        width = int(factor*len(this_image_array[0]))
        height = int(factor*len(this_image_array))

        window_auto_preview = Toplevel()
        # Set window title
        window_auto_preview.title("Preview of automatic defect detection")
        # Set window size
        window_auto_preview.geometry(str(2*width+10) + "x" + str(height+140))
        #Set window background color
        window_auto_preview.config(background = window_bg)

        auto_preview_info_frame = Frame(master=window_auto_preview, **frame_settings)
        auto_preview_info_frame.pack(padx=5, pady=5)
        Label(master=auto_preview_info_frame, text="The left image shows the rows that did not have defects according to the algorithm (the other ones were replaced with red color).\nFor comparison the right image shows the rows that have defects in them according to the algorithm (the other ones were replaced with green color).", **label_settings).grid(row=0, column=0, pady=3)

        auto_canvas_frame = Frame(master=window_auto_preview, bg="gray")
        auto_canvas_frame.pack(padx=5, pady=5)
        
        auto_img_def = ImageTk.PhotoImage(Image.open(def_path).resize([width, height]))
        auto_img_good = ImageTk.PhotoImage(Image.open(good_path).resize([width, height]))

        auto_canvas_def = Canvas(auto_canvas_frame, width=auto_img_def.width(), height=auto_img_def.height(),
                        borderwidth=0, highlightthickness=0)
        auto_canvas_def.grid(row=0, column=0)
        auto_canvas_def.img = auto_img_def  # Keep reference in case this code is put into a function.
        image_container_def = auto_canvas_def.create_image(0, 0, image=auto_img_def, anchor=NW)

        auto_canvas_good = Canvas(auto_canvas_frame, width=auto_img_good.width(), height=auto_img_good.height(),
                        borderwidth=0, highlightthickness=0)
        auto_canvas_good.grid(row=0, column=1, padx=10)
        auto_canvas_good.img = auto_img_good  # Keep reference in case this code is put into a function.
        image_container_good = auto_canvas_good.create_image(0, 0, image=auto_img_good, anchor=NW)

        auto_preview_change_img_frame = Frame(master=window_auto_preview, **frame_settings)
        auto_preview_change_img_frame.pack(padx=5, pady=5)

        myscroll = Scrollbar(auto_preview_change_img_frame) 
        #myscroll.grid(row=0, column=1, padx=0) 
        
        mylist = Listbox(auto_preview_change_img_frame, yscrollcommand = myscroll.set, height=3, width=10)  
        for filename in volts: 
            mylist.insert(END, str(filename) + " V") 
        #mylist.grid(row=0, column=0, padx=0)    
        mylist.pack(side = LEFT, fill = BOTH)
        myscroll.pack(side = LEFT, fill = Y)
        myscroll.config(command = mylist.yview)

        change_img_button = Button(auto_preview_change_img_frame, text = "Change Image", command = lambda: auto_preview_change_img_button_function(image_container_def, auto_canvas_def, SHOW_IMAGES_DIRECTORY_NAME + CHANGING_IMG_DIR + "def_" + mylist.get(mylist.curselection())[:-2] + ".tif", image_container_good, auto_canvas_good, SHOW_IMAGES_DIRECTORY_NAME + CHANGING_IMG_DIR + "good_" + mylist.get(mylist.curselection())[:-2] + ".tif", width, height), **button_settings)
        #change_img_button.grid(row=0, column=3, padx=20)
        change_img_button.pack(side=RIGHT, padx=20)

    else:
        #the past was easier
        # path = dir + "/" + files[volts.index(max(volts))]
        # this_image_array = pa.get_grayscale(path)
        # new_auto_img_def, new_auto_img_good =  pa.find_defective(this_image_array, ret_img=True, path=path, **default_defective_row_settings)
        #the easy past stops here

        # start of difficult
        blub_image_arrays = []
        for blub_filename in files:
            blub_image_arrays.append(pa.get_grayscale(dir + "/" + blub_filename))
        blub_image_arrays = np.array(blub_image_arrays)

        blub_last_voltage = max(volts)
        blub_store_progress_volt = []
        blub_store_progress_ratio = []
        while True:
            blub_max_voltage_position = volts.index(blub_last_voltage)
            blub_reduced_image_array, blub_defective_rows = pa.find_defective(
                copy.deepcopy(blub_image_arrays[blub_max_voltage_position]), 
                **default_defective_row_settings)
            blub_def_real_ratio = len(blub_defective_rows)/len(blub_image_arrays[blub_max_voltage_position])
            blub_store_progress_volt.append(blub_last_voltage)
            blub_store_progress_ratio.append(blub_def_real_ratio)
            if blub_def_real_ratio<=other_default_settings["remove_at_max"]:
                break
            else:
                blub_new_voltage = pa.find_closest_value(blub_last_voltage/other_default_settings["reduce_by"], volts)
                if blub_new_voltage == blub_last_voltage:
                    blub_last_voltage = blub_store_progress_volt[blub_store_progress_ratio.index(min(blub_store_progress_ratio))]
                    blub_max_voltage_position = volts.index(blub_last_voltage)
                    break
                blub_last_voltage = blub_new_voltage
        
        path = dir + "/" + files[blub_max_voltage_position]
        this_image_array = pa.get_grayscale(path)
        new_auto_img_def, new_auto_img_good =  pa.find_defective(this_image_array, ret_img=True, path=path, **default_defective_row_settings)
        print("Picture taken at " + str(blub_last_voltage) + " will be used to evaluate defects.")
        #end of difficult

        def_path = SHOW_IMAGES_DIRECTORY_NAME + CHANGING_IMG_DIR + "def_" + str(max(volts)) + ".tif"
        good_path = SHOW_IMAGES_DIRECTORY_NAME + CHANGING_IMG_DIR + "good_" + str(max(volts)) + ".tif"
        new_auto_img_def.save(def_path)
        new_auto_img_good.save(good_path)

        factor = 560/len(this_image_array[0])
        width = int(factor*len(this_image_array[0]))
        height = int(factor*len(this_image_array))

        window_auto_preview = Toplevel()
        # Set window title
        window_auto_preview.title("Preview of automatic defect detection")
        # Set window size
        window_auto_preview.geometry(str(2*width+10) + "x" + str(height+80))
        #Set window background color
        window_auto_preview.config(background = window_bg)

        auto_preview_info_frame = Frame(master=window_auto_preview, **frame_settings)
        auto_preview_info_frame.pack(padx=5, pady=5)
        Label(master=auto_preview_info_frame, text="The left image shows the rows that did not have defects according to the algorithm (the other ones were replaced with red color).\nFor comparison the right image shows the rows that have defects in them according to the algorithm (the other ones were replaced with green color).", **label_settings).grid(row=0, column=0, pady=3)

        auto_canvas_frame = Frame(master=window_auto_preview, bg="gray")
        auto_canvas_frame.pack(padx=5, pady=5)
        
        auto_img_def = ImageTk.PhotoImage(Image.open(def_path).resize([width, height]))
        auto_img_good = ImageTk.PhotoImage(Image.open(good_path).resize([width, height]))

        auto_canvas_def = Canvas(auto_canvas_frame, width=auto_img_def.width(), height=auto_img_def.height(),
                        borderwidth=0, highlightthickness=0)
        auto_canvas_def.grid(row=0, column=0)
        auto_canvas_def.img = auto_img_def  # Keep reference in case this code is put into a function.
        image_container_def = auto_canvas_def.create_image(0, 0, image=auto_img_def, anchor=NW)

        auto_canvas_good = Canvas(auto_canvas_frame, width=auto_img_good.width(), height=auto_img_good.height(),
                        borderwidth=0, highlightthickness=0)
        auto_canvas_good.grid(row=0, column=1, padx=10)
        auto_canvas_good.img = auto_img_good  # Keep reference in case this code is put into a function.
        image_container_good = auto_canvas_good.create_image(0, 0, image=auto_img_good, anchor=NW)


def Automatic_defect_window(picture_paths_widget, picture_filetype_widget, this_button, other_button):
    """
    """
    global picture_file_names, picture_voltage_values

    #check if settings are available
    reset_errors()

    global intro_read
    global browser_frame, compute_error_label, filetype_frame, reopen_prep_button, introduction_frame
    global other_default_settings

    if not intro_read:
        introduction_frame.config(highlightbackground="red", highlightthickness=2)
        compute_error_label.config(fg = "red", text="\n\nYou are not allowed to proceed until I am sure you know how to save your images.")
        return

    try:
        directory_path = picture_paths_widget.get()
        check_image_size(directory_path, picture_filetype_widget.get())
        other_default_settings["filetype"] = picture_filetype_widget.get()
        if len(picture_voltage_values) == 0:
            picture_file_names, picture_voltage_values = retrieve_voltage(directory_path, picture_filetype=picture_filetype_widget.get())
        if len(picture_voltage_values) == 0:
            browser_frame.config(highlightbackground="red", highlightthickness=2)
            filetype_frame.config(highlightbackground="red", highlightthickness=2)
            compute_error_label.config(fg = "red", text="No meaningful image files could be found. There are multiple possible reasons for this to happen:\n\u2219Incorrect path to images\n\u2219Incorrect filetype chosen\n\u2219preparations were not correctly followed")
            reopen_prep_button.pack(padx=5, pady=5)
            return
    except:
        browser_frame.config(highlightbackground="red", highlightthickness=2)
        compute_error_label.config(fg = "red", text="\n\nSomething is off with the entered directory path. Did you type in anything at all?")
        return

    #change active button color
    this_button.config(highlightbackground="green")
    other_button.config(highlightbackground="red")

    global automatic_defect_detect
    automatic_defect_detect = True

    window_auto = Toplevel()
    # Set window title
    window_auto.title("Settings for automatic removal of defective rows")
    # Set window size
    window_auto.geometry("540x525")
    #Set window background color
    window_auto.config(background = window_bg)

    automatic_intro_frame = Frame(master=window_auto, **frame_settings)
    automatic_intro_frame.pack(padx=5, pady=5)
    Label(master=automatic_intro_frame, text="Here you can alter a few variables the algorithm uses to detect defects.\nIf you are not sure what each variable does you can open a description window\nvia the corresponding button.\nThe variables are already set with values that worked well for our images.\nYou can use the \"Preview\" button to see the result of the automatic evaluation.\nIf you are satisfied with the outcome hit \"Confirm\".", **label_settings).grid(row=0, column=0, pady=3)

    automatic_settings_frame = Frame(master=window_auto, **frame_settings)
    automatic_settings_frame.pack(padx=5, pady=5)

    label_settings["bg"] = "white"
    label_settings["fg"] = "black"
    label_settings["padx"] = 0

    Label(master=automatic_settings_frame, text="\u2219max_darker_area_height:", **label_settings).grid(row=0, column=0, pady=3)
    Label(master=automatic_settings_frame, text="\u2219gray_change_sensivity_ratio_horizontal:", **label_settings).grid(row=1, column=0, pady=3)
    Label(master=automatic_settings_frame, text="\u2219gray_change_sensivity_ratio_vertical:", **label_settings).grid(row=2, column=0, pady=3)
    Label(master=automatic_settings_frame, text="\u2219compare_to_following:", **label_settings).grid(row=3, column=0, pady=3)
    Label(master=automatic_settings_frame, text="\u2219compare_min_value:", **label_settings).grid(row=4, column=0, pady=3)
    Label(master=automatic_settings_frame, text="\u2219remove_next_to_defective:", **label_settings).grid(row=5, column=0, pady=3)
    Label(master=automatic_settings_frame, text="\u2219ignore_whitespace_faults:", **label_settings).grid(row=6, column=0, pady=3)
    Label(master=automatic_settings_frame, text="\u2219check_images_individually:", **label_settings).grid(row=7, column=0, pady=3)
    Label(master=automatic_settings_frame, text="\u2219remove_at_max:", **label_settings).grid(row=8, column=0, pady=3)
    Label(master=automatic_settings_frame, text="\u2219reduce_by:", **label_settings).grid(row=9, column=0, pady=3)

    Label(master=automatic_settings_frame, text="input \u2208 \u2115", **label_settings).grid(row=0, column=2, pady=3, padx=20)
    Label(master=automatic_settings_frame, text="input \u2208 [0,1)", **label_settings).grid(row=1, column=2, pady=3, padx=20)
    Label(master=automatic_settings_frame, text="input \u2208 [0,1)", **label_settings).grid(row=2, column=2, pady=3, padx=20)
    Label(master=automatic_settings_frame, text="input \u2208 \u2115, input < 21", **label_settings).grid(row=3, column=2, pady=3, padx=20)
    Label(master=automatic_settings_frame, text="input \u2208 \u2115, input < 31", **label_settings).grid(row=4, column=2, pady=3, padx=20)
    Label(master=automatic_settings_frame, text="input \u2208 \u2115", **label_settings).grid(row=5, column=2, pady=3, padx=20)
    Label(master=automatic_settings_frame, text="input \u2208 [0,1)", **label_settings).grid(row=8, column=2, pady=3, padx=20)
    Label(master=automatic_settings_frame, text="input > 1", **label_settings).grid(row=9, column=2, pady=3, padx=20)
    

    #ttk.Separator(automatic_settings_frame, orient='horizontal').grid(row=2, column=1)

    max_dark_entry = Entry(master=automatic_settings_frame, width=5, **entry_settings)
    max_dark_entry.grid(row=0, column=1)
    max_dark_entry.insert(0, "50")

    gcsr_h_entry = Entry(master=automatic_settings_frame, width=5, **entry_settings)
    gcsr_h_entry.grid(row=1, column=1)
    gcsr_h_entry.insert(0, "0.2")

    gcsr_v_entry = Entry(master=automatic_settings_frame, width=5, **entry_settings)
    gcsr_v_entry.grid(row=2, column=1)
    gcsr_v_entry.insert(0, "0.2")

    ctf_entry = Entry(master=automatic_settings_frame, width=5, **entry_settings)
    ctf_entry.grid(row=3, column=1)
    ctf_entry.insert(0, "3")

    ctmv_entry = Entry(master=automatic_settings_frame, width=5, **entry_settings)
    ctmv_entry.grid(row=4, column=1)
    ctmv_entry.insert(0, "10")

    rntd_entry = Entry(master=automatic_settings_frame, width=5, **entry_settings)
    rntd_entry.grid(row=5, column=1)
    rntd_entry.insert(0, "5")

    OPTIONS_iwf = ["True", "False"]
    iwf_option = StringVar(window_auto)
    iwf_option.set(OPTIONS_iwf[0]) # default value
    drop_iwf = OptionMenu(automatic_settings_frame, iwf_option, *OPTIONS_iwf)
    drop_iwf.grid(row=6, column=1)

    for key in dropdown_settings:
        drop_iwf[key] = dropdown_settings[key]

    OPTIONS_cii = ["True", "False"]
    cii_option = StringVar(window_auto)
    cii_option.set(OPTIONS_cii[1]) # default value
    drop_cii = OptionMenu(automatic_settings_frame, cii_option, *OPTIONS_cii)
    drop_cii.grid(row=7, column=1)

    for key in dropdown_settings:
        drop_cii[key] = dropdown_settings[key]
    
    ram_entry = Entry(master=automatic_settings_frame, width=5, **entry_settings)
    ram_entry.grid(row=8, column=1)
    ram_entry.insert(0, "0.75")

    rb_entry = Entry(master=automatic_settings_frame, width=5, **entry_settings)
    rb_entry.grid(row=9, column=1)
    rb_entry.insert(0, "1.5")
    
    automatic_confirmation_frame = automatic_intro_frame = Frame(master=window_auto, **frame_settings)
    automatic_confirmation_frame.pack(padx=5, pady=5)
    
    label_settings["fg"] = "green"
    automatic_error_frame = Frame(master=window_auto, **frame_settings)
    automatic_error_frame.pack(padx=5, pady=5)
    auto_error_label = Label(master=automatic_error_frame, text="Everything seems fine... yet. Wait until you hit a Button.", **label_settings)
    auto_error_label.grid(row=0, column=0, pady=3)
    label_settings["fg"] = "black"
    label_settings["bg"] = "light gray"
    label_settings["padx"] = 5

    auto_description_button = Button(automatic_confirmation_frame, text = "Description", command = Automatic_defect_description_window, **button_settings)
    auto_description_button.grid(row=0, column=0, padx=5)

    auto_preview_button = Button(automatic_confirmation_frame, text = "Preview", command = lambda: auto_preview_button_function(max_dark_entry, gcsr_h_entry, gcsr_v_entry, ctf_entry, ctmv_entry, rntd_entry, iwf_option, cii_option, ram_entry, rb_entry, auto_error_label, directory_path, picture_file_names, picture_voltage_values), **button_settings)
    auto_preview_button.grid(row=0, column=1, padx=110)

    auto_confirm_button = Button(automatic_confirmation_frame, text = "Confirm", command = lambda: auto_confirm_button_function(max_dark_entry, gcsr_h_entry, gcsr_v_entry, ctf_entry, ctmv_entry, rntd_entry, iwf_option, cii_option, ram_entry, rb_entry, auto_error_label, window_auto), **button_settings)
    auto_confirm_button.grid(row=0, column=2, padx=5)


    # auto_preview_frame = Frame(master=window_auto, **frame_settings)
    # auto_preview_frame.pack(padx=5, pady=5, side=RIGHT)
    # Label(master=auto_preview_frame, text="TESTITESTITEST", **label_settings).grid(row=0, column=0)


def Automatic_defect_description_window():
    """
    """
    window_auto = Toplevel()
    # Set window title
    window_auto.title("Description of settings for automatic removal of defective rows")
    # Set window size
    window_auto.geometry("660x862")
    #Set window background color
    window_auto.config(background = window_bg)

    automatic_description_frame = Frame(master=window_auto, **frame_settings)
    automatic_description_frame.grid(row=0, column=0, padx=5, pady=5)
    #Label(master=automatic_frame, text="Settings for automatic removal of defective rows:", **label_settings).pack(padx=5, pady=10, side=TOP)
    label_settings["bg"] = "white"
    label_settings["fg"] = "black"
    Label(master=automatic_description_frame, text="\u2219max_darker_area_height:", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "gray"
    Label(master=automatic_description_frame, text="There are a few lines at the bottom of the page which are darker than the others.\n\"max_darker_area_height\" is a failsafe variable that sets how many rows (in pixel)\nit has at most.", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "black"
    #Label(master=automatic_description_frame, text="", **label_settings).pack(padx=5, pady=0, side=TOP)
    Label(master=automatic_description_frame, text="\u2219gray_change_sensivity_ratio_horizontal:", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "gray"
    Label(master=automatic_description_frame, text="This value sets how much darker the next viewed pixel in horizontal direction must be\nto count as defective. If the next pixel is darker than:\n(1-\"gray_change_sensivity_ratio_horizontal\")\u00B7\"previous pixel brightness\"\nit counts as defective.", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "black"
    #Label(master=automatic_description_frame, text="", **label_settings).pack(padx=5, pady=0, side=TOP)
    Label(master=automatic_description_frame, text="\u2219gray_change_sensivity_ratio_vertical", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "gray"
    Label(master=automatic_description_frame, text="Same as above but in vertical direction.", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "black"
    #Label(master=automatic_description_frame, text="", **label_settings).pack(padx=5, pady=0, side=TOP)
    Label(master=automatic_description_frame, text="\u2219compare_to_following", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "gray"
    Label(master=automatic_description_frame, text="This variable sets how many pixel are skipped (in vertical and horizontal direction)\nbetween the above mentioned \"previous pixel\" and \"next viewed pixel\".\nThis variable was introduced as darkness of a defect sometimes increases continuously in small steps.", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "black"
    #Label(master=automatic_description_frame, text="", **label_settings).pack(padx=5, pady=0, side=TOP)
    Label(master=automatic_description_frame, text="\u2219compare_min_value", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "gray"
    Label(master=automatic_description_frame, text="This variable sets how bright a pixel must be in order to count as possible defect.", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "black"
    #Label(master=automatic_description_frame, text="", **label_settings).pack(padx=5, pady=0, side=TOP)
    Label(master=automatic_description_frame, text="\u2219remove_next_to_defective", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "gray"
    Label(master=automatic_description_frame, text="This variable sets how many lines neighboring a defective one will count as defective as well.\n(The algorithm will most likely not detect all defective lines. Next to a defective line\n you have a high possibility of finding other ones which were not detected)", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "black"
    #Label(master=automatic_description_frame, text="", **label_settings).pack(padx=5, pady=0, side=TOP)
    Label(master=automatic_description_frame, text="\u2219ignore_whitespace_faults", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "gray"
    Label(master=automatic_description_frame, text="This variable sets if defects in the space of maximum brightness shall be neglected (advisable).", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "black"
    #Label(master=automatic_description_frame, text="", **label_settings).pack(padx=5, pady=0, side=TOP)
    Label(master=automatic_description_frame, text="\u2219check_images_individually", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "gray"
    Label(master=automatic_description_frame, text="This variable sets whether every image is checked for defects.\nIf not, then the image taken at highest voltage is checked for defects.\nThe results are applied to the other images.\nSetting this to: \"True\" is not recommended, as it will take an ridiculous amount of time to compute\nand might even cause the program to fail (as this option was not practically tested well enough).", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "black"
    #Label(master=automatic_description_frame, text="", **label_settings).pack(padx=5, pady=0, side=TOP)
    Label(master=automatic_description_frame, text="\u2219remove_at_max", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "gray"
    Label(master=automatic_description_frame, text="The defects in the picture taken at highest voltage are easily findable by the algorithm.\nIf your sample shows a lot of defects, there might not be\nmany datarows left to evaluate the diffusion length from.\nA nice workaround is to check whether more than\n\"amount of defective rows\"/\"total amount of rows\" is higher than \"remove_at_max\".\nIf that is the case, a picture taken at less voltage is chosen\nfor evaluation until the mentioned ratio is smaller.\nIf there is no such picture findable, the one with the lowest ratio is chosen for evaluation.", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "black"
    #Label(master=automatic_description_frame, text="", **label_settings).pack(padx=5, pady=0, side=TOP)
    Label(master=automatic_description_frame, text="\u2219reduce_by", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "gray"
    Label(master=automatic_description_frame, text="Just looking at the picture with slightly less voltage in the method above will not change much\nand result in taking way to much time to compute.\nTherefore the current voltage value will be divided by \"reduce_by\"\nand the picture taken at the voltage value closest to the outcome will be chosen next.", **label_settings).pack(padx=5, pady=0, side=TOP)


def manual_add_button_function(img_cont, canvas, path, label, img_only = False):
    """
    """
    global manually_chosen_borders, shown_img

    if topy > boty:
        bigger = topy
        lower = boty
    else:
        bigger = boty
        lower = topy

    wrong = False
    for i in range(0, len(manually_chosen_borders)):
        if bigger > manually_chosen_borders[i][0] and bigger < manually_chosen_borders[i][1]:
            wrong = True
            break
        if lower > manually_chosen_borders[i][0] and lower < manually_chosen_borders[i][1]:
            wrong = True
            break
    
    if not wrong:
        if not img_only:
            manually_chosen_borders.append([lower, bigger])
    else:
        label.grid(row=1, column = 0, columnspan = 3)
        return

    try:
        label.grid_forget()
    except:
        print("", end="")

    #create directory
    if not os.path.isdir(SHOW_IMAGES_DIRECTORY_NAME + CHANGING_IMG_DIR):
        os.mkdir(SHOW_IMAGES_DIRECTORY_NAME + CHANGING_IMG_DIR)
    else:
        files = os.listdir(SHOW_IMAGES_DIRECTORY_NAME + CHANGING_IMG_DIR)
        for file in files:
            if os.path.exists(SHOW_IMAGES_DIRECTORY_NAME + CHANGING_IMG_DIR + file):
                os.remove(SHOW_IMAGES_DIRECTORY_NAME + CHANGING_IMG_DIR + file)

    color_positions = []
    for i in range(0, len(manually_chosen_borders)):
        color_positions.append([manually_chosen_borders[i][0], "all"])
        color_positions.append([manually_chosen_borders[i][1], "all"])
        for j in range(manually_chosen_borders[i][0], manually_chosen_borders[i][1]+1):
            color_positions.append([j, 0])
            color_positions.append([j, "last"])

    new_img = pa.edit_image(path, color=pa.color_green, ret_img=True, positions=color_positions)
    new_img.save(SHOW_IMAGES_DIRECTORY_NAME + CHANGING_IMG_DIR + "temp_manual.tif")
    del new_img
    shown_img = ImageTk.PhotoImage(Image.open(SHOW_IMAGES_DIRECTORY_NAME + CHANGING_IMG_DIR + "temp_manual.tif"))
    canvas.itemconfig(img_cont, image=shown_img)


def manual_confirm_button_function(window):
    """
    """
    window.destroy()


def manual_reset_button_function(img_cont, canvas, path, label):
    """
    """
    global manually_chosen_borders
    manually_chosen_borders = []

    manual_add_button_function(img_cont, canvas, path, label, img_only=True)


def Manual_defect_window(picture_paths_widget, picture_filetype_widget, this_button, other_button):
    """
    Bla
    """
    #alter frame settings
    global shown_img
    global other_default_settings
    global picture_file_names, picture_voltage_values
    global topx, topy, botx, boty
    topx, topy, botx, boty = 0, 0, 0, 0

    #check if settings are available
    reset_errors()

    global intro_read
    global browser_frame, compute_error_label, filetype_frame, reopen_prep_button, introduction_frame
    global manually_chosen_borders

    if not intro_read:
        introduction_frame.config(highlightbackground="red", highlightthickness=2)
        compute_error_label.config(fg = "red", text="\n\nYou are not allowed to proceed until I am sure you know how to save your images.")
        return

    try:
        directory_path = picture_paths_widget.get()
        check_image_size(directory_path, picture_filetype=picture_filetype_widget.get())
        other_default_settings["filetype"] = picture_filetype_widget.get()
        if len(picture_voltage_values) == 0:
            picture_file_names, picture_voltage_values = retrieve_voltage(directory_path, picture_filetype=picture_filetype_widget.get())
        if len(picture_voltage_values) == 0:
            browser_frame.config(highlightbackground="red", highlightthickness=2)
            filetype_frame.config(highlightbackground="red", highlightthickness=2)
            compute_error_label.config(fg = "red", text="No meaningful image files could be found. There are multiple possible reasons for this to happen:\n\u2219Incorrect path to images\n\u2219Incorrect filetype chosen\n\u2219preparations were not correctly followed")
            reopen_prep_button.pack(padx=5, pady=5)
            return
    except:
        browser_frame.config(highlightbackground="red", highlightthickness=2)
        compute_error_label.config(fg = "red", text="\n\nSomething is off with the entered directory path. Did you type in anything at all?")
        return
    
    #show active button
    this_button.config(highlightbackground="green")
    other_button.config(highlightbackground="red")

    global automatic_defect_detect
    automatic_defect_detect = False

    path_to_picture = SHOW_IMAGES_DIRECTORY_NAME + picture_file_names[picture_voltage_values.index(max(picture_voltage_values))]

    window_manual = Toplevel()
    # Set window title
    window_manual.title("Manually choosing areas without defects")
    # Set window size
    window_manual.geometry("810x780")
    #Set window background color
    window_manual.config(background = window_bg)

    frame_settings["width"] = 800
    frame_settings["height"] = 70
    #introduction
    manual_intro_frame = Frame(master=window_manual, **frame_settings)
    manual_intro_frame.pack(padx=5, pady=5)
    manual_intro_frame.pack_propagate(False)
    Label(master=manual_intro_frame, text="Choose an area in the picture below by click and drag which does not contain any defects (as far as you can judge).\nOnly the position of the lower and upper border matters. Hit \"Add\" to confirm the area. You can do this multiple times.\nIf you are finished hit \"Confirm\".", **label_settings).pack(padx=5, pady=5)

    #canvas
    manual_canvas_frame = Frame(master=window_manual, bg="gray")
    manual_canvas_frame.pack(padx=5, pady=5)

    pic = (Image.open(path_to_picture))
    shown_img = ImageTk.PhotoImage(pic)

    #shown_img = ImageTk.PhotoImage(Image.open(path_to_picture))
    canvas = Canvas(manual_canvas_frame, width=shown_img.width(), height=shown_img.height(),
                    borderwidth=0, highlightthickness=0)
    canvas.pack(expand=True)
    canvas.img = shown_img  # Keep reference in case this code is put into a function.
    image_container = canvas.create_image(0, 0, image=shown_img, anchor=NW)

    #information and confirmation
    frame_settings["width"] = 800
    frame_settings["height"] = 70
    manual_info_frame = Frame(master=window_manual, **frame_settings)
    manual_info_frame.pack(padx=5, pady=5)
    manual_info_frame.pack_propagate(False)

    manual_doc_label = Label(master=manual_info_frame, text="You can not choose an area inside an already existing area!", **label_settings)
    manual_doc_label.config(fg="red")
    
    manual_add_button = Button(manual_info_frame, text = "Add", command = lambda: manual_add_button_function(image_container, canvas, path_to_picture, manual_doc_label), **button_settings)
    manual_add_button.grid(row=0, column=0, pady = 5, padx=5)

    manual_confirm_button = Button(manual_info_frame, text = "Confirm", command = lambda: manual_confirm_button_function(window_manual), **button_settings)
    manual_confirm_button.grid(row=0, column=1, pady = 5, padx=5)

    manual_reset_button = Button(manual_info_frame, text = "Reset", command = lambda: manual_reset_button_function(image_container, canvas, path_to_picture, manual_doc_label), **button_settings)
    manual_reset_button.grid(row=0, column=2, pady = 5, padx=5)

    if len(manually_chosen_borders) != 0:
        manual_add_button_function(image_container, canvas, path_to_picture, manual_doc_label, img_only = True)

    window_manual.after(1000, lambda: update_rectangle(window_manual, canvas))
    window_manual.mainloop()


def exp_fit_settings_window():
    window_exp_fit = Toplevel()
    # Set window title
    window_exp_fit.title("Description of settings for exponential fitting")
    # Set window size
    window_exp_fit.geometry("623x675")
    #Set window background color
    window_exp_fit.config(background = window_bg)

    automatic_description_frame = Frame(master=window_exp_fit, **frame_settings)
    automatic_description_frame.grid(row=0, column=0, padx=5, pady=5)
    #Label(master=automatic_frame, text="Settings for automatic removal of defective rows:", **label_settings).pack(padx=5, pady=10, side=TOP)
    label_settings["bg"] = "white"
    label_settings["fg"] = "black"
    Label(master=automatic_description_frame, text="Calculate diffusion length by:", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "gray"
    Label(master=automatic_description_frame, text="\u2219Mean:\nDiffusion length will be evaluated for every row (without defects).\nFinal diffusion length of an image (voltage value) will be the mean.", **label_settings).pack(padx=5, pady=0, side=TOP)
    Label(master=automatic_description_frame, text="\u2219Highest (row variable):\nDiffusion length will be evaluated for every row (without defects).\nHighest evaluated diffusion length will be the final diffusion length of an image.", **label_settings).pack(padx=5, pady=0, side=TOP)
    Label(master=automatic_description_frame, text="\u2219Highest (row fixed):\nDiffusion length will be evaluated for every row (without defects).\nAfterwards the diffusion length in all images will be summed up for every row,\nobviously resulting in a specific row, that has the highest diffusion length across all images.\nThe final diffusion length of every image, is the diffusion length of this row.", **label_settings).pack(padx=5, pady=0, side=TOP)
    Label(master=automatic_description_frame, text="\u2219[gray]:\nIf you see this behind an option, the same rows will be used for evaluation\nbut the mean of their gray values will be calculated and from that the diffusion length.", **label_settings).pack(padx=5, pady=0, side=TOP)
    Label(master=automatic_description_frame, text="\u2219All variants:\nDiffusion length will be evaluated with every method described above.\nNice option for comparing the different results.", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "black"
    Label(master=automatic_description_frame, text="Hint:", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "gray"
    Label(master=automatic_description_frame, text="If you want to choose yourself from which area the diffusion length will be calculated\nyou just have to choose this area via \"Manual removal\" and afterwards select \"Mean\".", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "black"
    Label(master=automatic_description_frame, text="", **label_settings).pack(padx=5, pady=5, side=TOP)
    Label(master=automatic_description_frame, text="\u2219Include lines next to Highest:", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "gray"
    Label(master=automatic_description_frame, text="Matters only if \"Highest\" is used to evaluate final diffusion length.\nValue sets how many connected lines\nnext to the final diffusion length will be looked at as well.\nDiffusion length for all of them will be calculated.\nThe final diffusion length is the mean.", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "black"
    Label(master=automatic_description_frame, text="", **label_settings).pack(padx=5, pady=5, side=TOP)
    Label(master=automatic_description_frame, text="\u2219Initial values for exponential fitting:", **label_settings).pack(padx=5, pady=0, side=TOP)
    label_settings["fg"] = "gray"
    Label(master=automatic_description_frame, text="The formula that is used for the exponential fit looks like:\nmultiplier * exp{position / diffusion length} + summand.\nThe algorithm that evaluates the best fitting parameters needs initial values for them.", **label_settings).pack(padx=5, pady=0, side=TOP)


def kill(window, resize = ""):
    """
    """
    window.destroy()
    try:
        resize.geometry("722x770")

        global intro_read
        intro_read = True

        reset_errors()
    except:
        return


def Introduction_Window(main_window, main_frame, change=True):
    """
    """
    if change:
        reset_errors()

        global intro_read
        intro_read = True

        main_window.geometry("722x770")
        main_frame.destroy()

    window_intro = Toplevel()

    # Set window title
    window_intro.title("File Preparations")

    # Set window size
    window_intro.geometry("635x460")
    
    #Set window background color
    window_intro.config(background = window_bg)

    # File browser section
    intro_frame = Frame(master=window_intro, **frame_settings)
    intro_frame.pack(padx=5, pady=5)
    #intro_frame.pack_propagate(False)

    # warn_label = Label(master=intro_frame, text="WARNING: Read before you proceed", **label_settings)
    # warn_label.pack(padx=5, pady=5)
    # warn_label.config(fg="red")

    int_label = Label(master=intro_frame, text="This program requieres you to store all images you made into one folder.\nThe name of each image needs to contain a number (examples: 23, 2.1).\nThis number represents the voltage the image was taken with.\nThe number must represent the same unit in every image.\nThe algorithm will not check if you added V, mV, etc. anywhere in the name.\nYou can later set what unit corresponds to all numbers.\nExample:\n\u2219If you measured one image with 2V and another with 100mV, the name\nof the images should contain 2 and 0.1 if the unit is later set to V.\n\u2219If the unit is set to mV, the names must contain 2000 and 100.\nAn image must never contain two or more separate numbers.\nExample:\n\u2219bla_20_bla is valid, bla_2_0_bla and bla_20_.bla are not\nKeep attention that the comma \",\" does not indicate a decimal number in the name, a dot \".\" does!\nExamples for a valid name:\nMuster2.01Mayer, Muster_2.01_Mayer, etc. \n... You get the deal.", **label_settings)
    int_label.pack(padx=5, pady=5)
    int_label.config(bg="white")

    blank_label = Label(master=intro_frame, text="Blanko Bianko", **label_settings)
    blank_label.pack(padx=5, pady=5)
    blank_label.config(fg="white", bg="white")

    blank_label = Label(master=intro_frame, text="Another important aspect is the length scale on your images.\nAll your images must have the same Length/Pixel ratio.\nThis should always apply so do not worry about it.\nJust saying we don't take the responsibility if it does occur.", **label_settings)
    blank_label.pack(padx=5, pady=5)
    blank_label.config(bg="white")

    Button(master=intro_frame, text="Yeah, yeah... I got it.", command = lambda: kill(window_intro), **button_settings).pack(padx=5, pady=5, side=RIGHT)
    window_intro.mainloop()


def forget_all():
    """
    """
    global introduction_frame, browser_frame, filetype_frame, pixel_length_window_frame, area_frame, exp_fit_frame, error_report_frame
    try:
        introduction_frame.grid_forget()
    except:
        print("", end="")
    browser_frame.grid_forget()
    filetype_frame.grid_forget()
    pixel_length_window_frame.grid_forget()
    area_frame.grid_forget()
    exp_fit_frame.grid_forget()
    error_report_frame.grid_forget()


def final_plot_preview_change_img_button(img_cont, canvas, path, width, height):
    """
    """
    global plot_preview_img

    plot_preview_img = ImageTk.PhotoImage(Image.open(path).resize([width, height]))
    canvas.itemconfig(img_cont, image=plot_preview_img)


def quit_appi():
    sys.exit("")


def final_plot_preview():
    """
    """
    global plot_preview_img

    if not os.path.isdir(TEMP_PLOTS_DIRECTORY_NAME):
        os.mkdir(TEMP_PLOTS_DIRECTORY_NAME)

    files = os.listdir(TEMP_PLOTS_DIRECTORY_NAME)
    files = pa.remove_other_filetypes(files, "png")
    
    try:
        trash_pic = Image.open(TEMP_PLOTS_DIRECTORY_NAME + files[0])
        trash_img = ImageTk.PhotoImage(trash_pic)
    except:
        return
    trash_plot_width=trash_img.width()
    trash_plot_height=trash_img.height()
    del trash_img
    final_height_factor = 640/trash_plot_height
    final_width_factor = 800/trash_plot_width
    if final_height_factor > final_width_factor:
        final_plot_factor = final_width_factor
    else:
        final_plot_factor = final_height_factor
    plot_width=int(trash_plot_width*final_plot_factor)+20
    plot_height=int(trash_plot_height*final_plot_factor)
    trash_pic = trash_pic.resize((plot_width, plot_height))
    plot_preview_img = ImageTk.PhotoImage(trash_pic)

    window_plot_preview = Toplevel()
    # Set window title
    window_plot_preview.title("Plot Preview")
    # Set window size
    window_plot_preview.geometry(str(plot_width+40) + "x" + str(plot_height+80))
    #Set window background color
    window_plot_preview.config(background = window_bg)

    plot_preview_frame = Frame(master=window_plot_preview, bg="white")
    plot_preview_frame.pack(padx=5, pady=5)

    plot_preview_canvas = Canvas(plot_preview_frame, width=plot_width, height=plot_height,
                    borderwidth=0, highlightthickness=0, background="snow")
    plot_preview_canvas.grid(row=0, column=0)
    plot_preview_canvas.img = plot_preview_img  # Keep reference in case this code is put into a function.
    plot_image_container = plot_preview_canvas.create_image(0, 0, image=plot_preview_img, anchor=NW)

    plot_preview_change_img_frame = Frame(master=window_plot_preview, **frame_settings)
    plot_preview_change_img_frame.pack(padx=5, pady=5)

    plot_scroll = Scrollbar(plot_preview_change_img_frame) 
    #plot_scroll.grid(row=0, column=1, padx=0) 

    plot_list = Listbox(plot_preview_change_img_frame, yscrollcommand = plot_scroll.set, height=3, width=30)  
    for filename in files: 
        plot_list.insert(END, str(filename)) 
    #plot_list.grid(row=0, column=0, padx=0)    
    plot_list.pack(side = LEFT, fill = BOTH)
    plot_scroll.config(command = plot_list.yview)
    plot_scroll.pack(side = LEFT, fill = Y)

    #Button(plot_preview_change_img_frame, text = "Quit Application", command = lambda: quit_appi(), **button_settings).pack(side=RIGHT, padx=20)

    plot_change_img_button = Button(plot_preview_change_img_frame, text = "Change Image", command = lambda: final_plot_preview_change_img_button(plot_image_container, plot_preview_canvas, TEMP_PLOTS_DIRECTORY_NAME + plot_list.get(plot_list.curselection()), plot_width, plot_height), **button_settings)
    #plot_change_img_button.grid(row=0, column=3, padx=20)
    plot_change_img_button.pack(side=RIGHT, padx=20)


def final_compute_button(
    volt_dep_option, 
    lines_highest, 
    diff_length_iv, 
    multiplier_iv, 
    constant_iv,
    picture_paths_widget,
    # dir_name_junction,
    # dir_name_volt, 
    # file_name_junction, 
    # file_name_volt,
    volt_unit,
    all_done_frame, 
    all_done_label, 
    all_done_button,
    window
    ):
    """
    """
    global automatic_defect_detect
    global browser_frame, filetype_frame, pixel_length_window_frame, area_frame, exp_fit_frame, compute_error_label
    global picture_file_names, picture_voltage_values, manually_chosen_borders, length_of_pixel
    global default_defective_row_settings, other_default_settings
    
    mistakes_found = False
    reset_errors()

    if automatic_defect_detect == None:
        area_frame.config(highlightbackground="red", highlightthickness=2)
        mistakes_found = True
    
    if length_of_pixel == 0:
        pixel_length_window_frame.config(highlightbackground="red", highlightthickness=2)
        mistakes_found = True
    
    if mistakes_found:
        compute_error_label.config(fg="red", text="\n\nYou did not complete necessary steps.")
        return
    
    try:
        this_setting = int(lines_highest.get())
        if this_setting < 0 or this_setting > 100:
            compute_error_label.config(text="\n\nOne or more of your inputs is out of range", fg="red")
            exp_fit_frame.config(highlightbackground="red", highlightthickness=2)
            return
        other_default_settings["lines_next_highest"] = this_setting
    except:
        exp_fit_frame.config(highlightbackground="red", highlightthickness=2, bg="red")
        compute_error_label.config(text="\n\nOne or more of your inputs contains invalid symbols.", fg="red")
        return
    
    try:
        this_setting = float(diff_length_iv.get())
        other_default_settings["initial_values"][0] = this_setting
    except:
        compute_error_label.config(text="\n\nOne or more of your inputs contains invalid symbols.", fg="red")
        exp_fit_frame.config(highlightbackground="red", highlightthickness=2)
        return
    
    try:
        this_setting = float(multiplier_iv.get())
        other_default_settings["initial_values"][1] = this_setting
    except:
        compute_error_label.config(text="\n\nOne or more of your inputs contains invalid symbols.", fg="red")
        exp_fit_frame.config(highlightbackground="red", highlightthickness=2)
        return
    
    try:
        this_setting = float(constant_iv.get())
        other_default_settings["initial_values"][2] = this_setting
    except:
        compute_error_label.config(text="\n\nOne or more of your inputs contains invalid symbols.", fg="red")
        exp_fit_frame.config(highlightbackground="red", highlightthickness=2)
        return
    
    this_setting = volt_dep_option.get()
    if this_setting == "Mean":
        other_default_settings["volt_dep_method"] = "mean_normal"
    elif this_setting == "Highest (row variable)":
        other_default_settings["volt_dep_method"] = "highest_variable_normal"
    elif this_setting == "Highest (row fixed)":
        other_default_settings["volt_dep_method"] = "highest_fixed_normal"
    if this_setting == "Mean [gray]":
        other_default_settings["volt_dep_method"] = "mean_gray"
    elif this_setting == "Highest (row variable) [gray]":
        other_default_settings["volt_dep_method"] = "highest_variable_gray"
    elif this_setting == "Highest (row fixed) [gray]":
        other_default_settings["volt_dep_method"] = "highest_fixed_gray"
    elif this_setting == "All variants":
        other_default_settings["volt_dep_method"] = "all"
    
    other_default_settings["pix_to_length"] = length_of_pixel

    if not automatic_defect_detect and len(manually_chosen_borders) == 0:
        area_frame.config(highlightbackground="red", highlightthickness=2)
        compute_error_label.config(text="\n\nYou want to use manually chosen borders but you did not define any.\nYou might see this error if you did not add any areas before exiting the window.", fg="red")
        return
    
    if not automatic_defect_detect:
        global scale_image
        for manual_border_index in range(0, len(manually_chosen_borders)):
            for bordi in range(0, len(manually_chosen_borders[manual_border_index])):
                manually_chosen_borders[manual_border_index][bordi] /= scale_image
                manually_chosen_borders[manual_border_index][bordi] = int(manually_chosen_borders[manual_border_index][bordi])

    directory_path = picture_paths_widget.get()

    #now its getting interesting
    # print(other_default_settings)
    # print(default_defective_row_settings)

    forget_all()

    all_done_frame.pack(padx=5, pady=5)
    all_done_label.pack(padx=5, pady=5, side=TOP)
    window.geometry("370x80")
    window.update()

    if other_default_settings["check_images_individually"] == True:
        print("You chose to check every image individually for defects. This might cause a \"VisibleDeprecationWarning\". Do not worry about it, it will compile nevertheless. It is gonna take quite a while though.")

    pa.final_computation_interface(
        automatic_defect_detect,
        directory_path,
        picture_file_names,
        picture_voltage_values,
        manually_chosen_borders,
        pickle_name_y = SAVE_POSITION_DIRECTORY + SAVE_POSITION_FILE + ".pkl",
        pickle_name_volt = SAVE_VOLT_DIRECTORY + SAVE_VOLT_FILE,
        pickle_name_exp = SAVE_EXP_DIRECTORY + SAVE_EXP_FILE,
        voltage_unit=volt_unit.get(),
        **default_defective_row_settings,
        **other_default_settings
    )
    
    window.geometry("640x290")
    all_done_label.config(fg="green", text="Computation finished successfully.\n\nIn case you want to export the data (for documentation, further analysis or different plotting),\ntext files containing the data were created in \"" + Temp_TEXT_DIRECTORY_NAME[:-1] + "\" - directory.\nThere you will always find 3 different versions of the same dataset:\n\u2219variant_1: table like presentation of data, cell items are centered                           \n\u2219variant_2: table like presentation of data, cell items are left aligned                       \n\u2219variant_3: cell items in a row are only separated by 1 blankspace, therefore cells \n     belonging to the same column might not be aligned vertically.\n\nWhy do we provide 3 different variants you ask?\nWell, we don't know how copy and paste into a table works on your computer.\nSome need a vertical alignment of the column cells (pages on mac for example),\nsome directly interpret 1 blankspace as column separation.")
    all_done_button.pack(padx=5, pady=5, side=TOP)


def reset_errors():
    global introduction_frame, browser_frame, filetype_frame, pixel_length_window_frame, area_frame, exp_fit_frame, compute_error_label, reopen_prep_button
    try:
        introduction_frame.config(highlightbackground="black", highlightthickness=1)
    except:
        print("", end="")
    browser_frame.config(highlightbackground="black", highlightthickness=1)
    filetype_frame.config(highlightbackground="black", highlightthickness=1)
    pixel_length_window_frame.config(highlightbackground="black", highlightthickness=1)
    area_frame.config(highlightbackground="black", highlightthickness=1)
    exp_fit_frame.config(highlightbackground="black", highlightthickness=1)

    compute_error_label.config(fg="green", text="This section serves as error documentation.\n\n\nNo errors were detected in your input.")
    try:
        reopen_prep_button.pack_forget()
    except:
        print("", end="")


global introduction_frame, browser_frame, filetype_frame, pixel_length_window_frame, area_frame, exp_fit_frame
introduction_frame, browser_frame, filetype_frame, pixel_length_window_frame, area_frame, exp_fit_frame = None, None, None, None, None, None

global compute_error_label, reopen_prep_button
compute_error_label, reopen_prep_button = None, None

global intro_read
intro_read = False


def MainWindow():
    """
    Bla
    """
    global introduction_frame, browser_frame, filetype_frame, pixel_length_window_frame, area_frame, exp_fit_frame, error_report_frame
    global compute_error_label, reopen_prep_button

    window = Tk()

    # Set window title
    window.title("automized evaluation of diffusion length")

    # Set window size
    window.geometry("722x730")
    
    #Set window background color
    window.config(background = window_bg)

    #Set rows and columns
    # window.columnconfigure(0, weight=1, minsize=5)
    # window.columnconfigure(1, weight=1, minsize=5)
    # window.rowconfigure(0, weight=1, minsize=5)
    # window.rowconfigure(1, weight=1, minsize=5)
    # window.rowconfigure(2, weight=1, minsize=5)
    # window.rowconfigure(3, weight=1, minsize=5)

    #intro frame
    introduction_frame = Frame(master=window, **frame_settings)
    introduction_frame.grid(row=0, column=0, padx=5, pady=5)
    introduction_frame.config(height=90)
    introduction_frame.pack_propagate(False)
    i_lab = Label(master=introduction_frame, text="WARNING: In order for this program to work you must have completed a few preparations.\nRead before you proceed.", **label_settings)
    i_lab.pack(padx=5, pady=5)
    i_lab.config(fg="red", bg="white")
    Button(master=introduction_frame, text="Preparations?", command = lambda: Introduction_Window(window, introduction_frame), **button_settings).pack(side=LEFT, padx=80)
    Button(master=introduction_frame, text="Already done!", command = lambda: kill(introduction_frame, window), **button_settings).pack(side=RIGHT, padx=80)

    # File browser section
    browser_frame = Frame(master=window, **frame_settings)
    browser_frame.grid(row=1, column=0, padx=5, pady=5)
    browser_frame.pack_propagate(False)
    Label(master=browser_frame, text="Path to directory:", **label_settings).pack(padx=5, pady=5)
    browser_entry = Entry(master=browser_frame, width=40, **entry_settings)
    browser_entry.pack(side=LEFT, padx=5)
    Button(master=browser_frame, text="Browse", command = lambda: open_directory(browser_entry), **button_settings).pack(side=LEFT)

    # File type section
    frame_settings["height"] = 40
    frame_settings["width"] = 455

    filetype_frame = Frame(master=window, **frame_settings)
    filetype_frame.grid(row=2, column=0, padx=5, pady=5)
    filetype_frame.grid_propagate(False)
    sneaky_blank_space = Label(master=filetype_frame, text="BiankoBla", **label_settings)
    sneaky_blank_space.grid(padx=5, pady=5, row=0, column=0)
    sneaky_blank_space.config(fg="white", bg="white")
    Label(master=filetype_frame, text="Filetype of Images:", **label_settings).grid(padx=5, pady=5, row=0, column=1)
    # filetype_entry = Entry(master=filetype_frame, width=5, **entry_settings)
    # filetype_entry.pack(side=LEFT)
    OPTIONS_filetype = ["tif", "jpeg", "pdf", "png"]
    filetype_option = StringVar(window)
    filetype_option.set(OPTIONS_filetype[0]) # default value

    drop = OptionMenu(filetype_frame, filetype_option, *OPTIONS_filetype)
    drop.grid(padx=5, pady=5, row=0, column=2)

    for key in dropdown_settings:
        drop[key] = dropdown_settings[key]

    # set what actual length a pixel represents
    frame_settings["height"] = 75

    pixel_length_window_frame = Frame(master=window, **frame_settings)
    pixel_length_window_frame.grid(row=3, column=0, padx=5, pady=5)
    pixel_length_window_frame.pack_propagate(False)
    Label(master=pixel_length_window_frame, text="Evaluating what length a pixel represents:", **label_settings).pack(padx=5, pady=5)

    pixel_length_label = Label(master=pixel_length_window_frame, text="Length/Pixel = ???", **label_settings)
    pixel_length_label.config(bg="white")
    pixel_length_label.pack(padx=10, pady=5, side=RIGHT)

    mybutton = Button(pixel_length_window_frame, text = "Evaluate", command = lambda: Pixel_length_window(browser_entry, filetype_option, pixel_length_label), **button_settings)
    mybutton.pack(pady = 5, side=LEFT, padx=10)

    # set in which area the pictures are examined
    area_frame = Frame(master=window, **frame_settings)
    area_frame.grid(row=4, column=0, padx=5, pady=5)
    Label(master=area_frame, text="Choose how you want to remove defective rows from the images:", **label_settings).pack(padx=5, pady=5)
    manual_defect_button = Button(area_frame, text = "Manual removal", command = lambda: Manual_defect_window(browser_entry, filetype_option, manual_defect_button, automatic_defect_button), **button_settings)
    manual_defect_button.pack(pady=5, side=LEFT)
    automatic_defect_button = Button(area_frame, text = "Automatic removal", command = lambda: Automatic_defect_window(browser_entry, filetype_option, automatic_defect_button, manual_defect_button), **button_settings)
    automatic_defect_button.pack(pady=5, side=RIGHT)

    # exponential fit frame
    frame_settings["height"] = 320
    frame_settings["width"] = 710
    exp_fit_frame = Frame(master=window, **frame_settings)
    exp_fit_frame.grid(row=5, column=0, padx=5, pady=5)
    exp_fit_frame.grid_propagate(False)
    Label(master=exp_fit_frame, text="Adjust settings for exponential fitting:", **label_settings).grid(padx=5, pady=5, row=0, column=0, columnspan=3)
    label_settings["bg"] = "white"
    Label(master=exp_fit_frame, text="Calculate diffusion length for voltage by: ", **label_settings).grid(row=1, column=0)

    OPTIONS_volt_dep = ["Mean", "Highest (row variable)", "Highest (row fixed)", "Mean [gray]", "Highest (row variable) [gray]", "Highest (row fixed) [gray]", "All variants"]
    volt_dep_option = StringVar(window)
    volt_dep_option.set(OPTIONS_volt_dep[2]) # default value

    drop_volt_dep = OptionMenu(exp_fit_frame, volt_dep_option, *OPTIONS_volt_dep)
    drop_volt_dep.grid(padx=5, column=1, row=1)

    for key in dropdown_settings:
        drop_volt_dep[key] = dropdown_settings[key]
    
    Label(master=exp_fit_frame, text="Include lines next to Highest: ", **label_settings).grid(row=2, column=0)
    lines_highest = Entry(master=exp_fit_frame, width=5, **entry_settings)
    lines_highest.grid(row=2, column=1, pady=5)
    lines_highest.insert(0, "20")
    Label(master=exp_fit_frame, text="input \u2208 \u2115, input < 100", **label_settings).grid(row=2, column=2)

    Label(master=exp_fit_frame, text="Voltage unit chosen in pictures: ", **label_settings).grid(row=3, column=0)
    voltage_unit = Entry(master=exp_fit_frame, width=5, **entry_settings)
    voltage_unit.grid(row=3, column=1, pady=5)
    voltage_unit.insert(0, "V")

    Label(master=exp_fit_frame, text="", **label_settings).grid(row=4, column=0)

    Label(master=exp_fit_frame, text="Initial values for exponential fitting:", **label_settings).grid(row=5, column=0)
    Label(master=exp_fit_frame, text="\u2219diffusion length:", **label_settings).grid(row=5, column=1)
    Label(master=exp_fit_frame, text="\u2219multiplier:", **label_settings).grid(row=6, column=1)
    Label(master=exp_fit_frame, text="\u2219summand:", **label_settings).grid(row=7, column=1)
    diff_length_iv = Entry(master=exp_fit_frame, width=5, **entry_settings)
    diff_length_iv.grid(row=5, column=2)
    diff_length_iv.insert(0, "55")

    multiplier_iv = Entry(master=exp_fit_frame, width=5, **entry_settings)
    multiplier_iv.grid(row=6, column=2, pady=5)
    multiplier_iv.insert(0, "50")

    constant_iv = Entry(master=exp_fit_frame, width=5, **entry_settings)
    constant_iv.grid(row=7, column=2, pady=5)
    constant_iv.insert(0, "1")
    
    # Label(master=exp_fit_frame, text="", **label_settings).grid(row=9, column=0)

    # Label(master=exp_fit_frame, text="Directory name:", **label_settings).grid(row=11, column=0)
    # Label(master=exp_fit_frame, text="File name:", **label_settings).grid(row=12, column=0)
    # label_settings["fg"] = "gray"
    # Label(master=exp_fit_frame, text="Diffusion length\nparallel to pn junction", **label_settings).grid(row=10, column=1)
    # Label(master=exp_fit_frame, text="Diffusion length\nper voltage", **label_settings).grid(row=10, column=2)
    # label_settings["fg"] = "black"
    # parallel_directory_name = Entry(master=exp_fit_frame, width=17, **entry_settings)
    # parallel_directory_name.grid(row=11, column=1, pady=5)
    # parallel_directory_name.insert(0, "Diffusion_parallel_to_junction")
    # parallel_file_name = Entry(master=exp_fit_frame, width=17, **entry_settings)
    # parallel_file_name.grid(row=12, column=1, pady=5)
    # parallel_file_name.insert(0, "first_try")
    # diff_volt_directory_name = Entry(master=exp_fit_frame, width=17, **entry_settings)
    # diff_volt_directory_name.grid(row=11, column=2, pady=5)
    # diff_volt_directory_name.insert(0, "Diffusion_per_volt")
    # diff_volt_file_name = Entry(master=exp_fit_frame, width=17, **entry_settings)
    # diff_volt_file_name.grid(row=12, column=2, pady=5)
    # diff_volt_file_name.insert(0, "please_work")

    all_done_frame = Frame(master=window, **frame_settings)
    
    all_done_label = Label(master=all_done_frame, text="Computation in progress.\nDepending on your settings and the amount of images\nthis may take a while.", **label_settings)
    all_done_label.config(bg="white", fg="red")
    all_done_button = Button(master=all_done_frame, text="Plot Preview", command = lambda: final_plot_preview(), **button_settings)

    Label(master=exp_fit_frame, text="", **label_settings).grid(row=8, column=0)

    Button(master=exp_fit_frame, text="Declaration of variables", command = exp_fit_settings_window, **button_settings).grid(row=9, column=0, pady=5)
    #Button(master=exp_fit_frame, text="Compute", command = lambda: final_compute_button(volt_dep_option, lines_highest, diff_length_iv, multiplier_iv, browser_entry, parallel_directory_name, diff_volt_directory_name, parallel_file_name, diff_volt_file_name, voltage_unit, all_done_frame, all_done_label, all_done_button, window), **button_settings).grid(row=14, column=2)
    Button(master=exp_fit_frame, text="Compute", command = lambda: final_compute_button(volt_dep_option, lines_highest, diff_length_iv, multiplier_iv, constant_iv, browser_entry, voltage_unit, all_done_frame, all_done_label, all_done_button, window), **button_settings).grid(row=9, column=2)

    #error frame
    frame_settings["height"] = 130
    frame_settings["width"] = 622.1

    error_report_frame = Frame(master=window, **frame_settings)
    error_report_frame.grid(row=6, column=0, padx=5, pady=5)
    #error_report_frame.grid_propagate(False)
    error_report_frame.pack_propagate(False)

    compute_error_label = Label(master=error_report_frame, text="This section serves as error documentation.\n\n\nNo errors were detected in your input.", **label_settings)
    compute_error_label.pack(padx=5, pady=5)
    compute_error_label.config(fg="green")
    reopen_prep_button = Button(master=error_report_frame, text="Reopen Preparations", command = lambda: Introduction_Window(window, introduction_frame, change=False), **button_settings)

    frame_settings["height"] = 70

    #retrieve settings
    window.mainloop()

MainWindow()