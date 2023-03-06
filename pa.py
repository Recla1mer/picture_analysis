#main file

from PIL import Image, ImageOps
import numpy as np
import os
import copy
import scipy
import pickle
import pa_plot

# RGB colors (0-255)
color_blue = [0, 0, 255]
color_green = [0, 255, 0]
color_red = [255, 0, 0]

#default settings

PICKLE_DIRECTORY_NAME = "Pickle_data/"
TEMP_PLOTS_DIRECTORY_NAME = "Temporary_Plots/"
Temp_TEXT_DIRECTORY_NAME = "Temporary_txt_Files/"

if not os.path.isdir(PICKLE_DIRECTORY_NAME):
    os.mkdir(PICKLE_DIRECTORY_NAME)
if not os.path.isdir(TEMP_PLOTS_DIRECTORY_NAME):
    os.mkdir(TEMP_PLOTS_DIRECTORY_NAME)
if not os.path.isdir(Temp_TEXT_DIRECTORY_NAME):
    os.mkdir(Temp_TEXT_DIRECTORY_NAME)

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
    "volt_dep_method": "all",
    "calc_y_dep": True,
    "remove_at_max": 0.75,
    "reduce_by": 1.5
}

string_integers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]

def search_fora(file_name_array, include, app_others = False):
    """
    """
    new_name = []
    if app_others:
        for name in file_name_array:
            if include not in name:
                new_name.append(name)
    else:
        for name in file_name_array:
            if include in name:
                new_name.append(name)
    return new_name


def get_directorya(string, ret_after = False):
    """
    SIDE FUNCTION

    Tries to separate the string (path) into filename and directories. Returns directories
    if existing.

    ARGUMENTS:
    - string: (string)
    """
    position = -1
    for i in range(0, len(string)):
        if string[i] == "/":
            position = i
    if position == -1:
        return ""
    else:
        if ret_after:
            return string[position+1:]
        else:
            return string[0:position+1]


def remove_other_filetypes(file_name_array, filetype = "tif"):
    """
    removes files from 'file_name_array' which are not of type: 'filetype'
    """
    delete_names = []
    for name in file_name_array:
        type_name = ""
        for char_position in range(len(name)-1, -1, -1):
            if name[char_position] == ".":
                type_name = name[char_position+1:len(name)]
                break
        if type_name != filetype:
            delete_names.append(name)
    
    for name in delete_names:
        file_name_array.remove(name)

    return file_name_array


def get_directory(string):
    """
    SIDE FUNCTION

    Tries to separate the string (path) into filename and directories. Returns directories
    if existing.

    ARGUMENTS:
    - string: (string)
    """
    position = -1
    for i in range(0, len(string)):
        if string[i] == "/":
            position = i
    if position == -1:
        return ""
    else:
        return string[0:position+1]
        

def check_directory(directory, filetype = "tif"):
    """
    function that checks if user given directory is valid
    """
    if os.path.isdir(directory):
        files = os.listdir(directory)
        files = remove_other_filetypes(copy.deepcopy(files))
        if len(files) > 0:
            return True
    return False


def get_grayscale(path):
    """
    SIDE FUNCTION
    """
    og_image = Image.open(path)
    #gray_img = og_image.convert("L")
    gray_image = ImageOps.grayscale(og_image)
    return np.array(gray_image)


def edit_image(
    path: str, 
    positions = [[]], 
    color=[255,255,255], 
    width=1,
    ret_img = False
    ):
    """
    SIDE FUNCTION
    """
    im = Image.open(path)
    rgb_im = im.convert('RGB')
    image_array = np.array(rgb_im)
    img_width = len(image_array[0]) - 1
    img_height = len(image_array) - 1

    width -= 1
    below = int(width/2)
    above = width-below
    position_pixel = []

    for i in range(len(positions)):
        if positions[i][0] == "last":
            positions[i][0] = img_height
        if positions[i][1] == "last":
            positions[i][1] = img_width
        
    for i in range(len(positions)):
        if positions[i][0] == "all":
            other = positions[i][1]
            for j in range(len(image_array)):
                position_pixel.append([j, other])
                for k in range(1, above):
                    position_pixel.append([j, other+k])
                for k in range(1, below):
                    position_pixel.append([j, other-k])
        elif positions[i][1] == "all":
            other = positions[i][0]
            for j in range(len(image_array[0])):
                position_pixel.append([other, j])
                for k in range(0, above):
                    position_pixel.append([other+k, j])
                for k in range(0, below):
                    position_pixel.append([other-k, j])
        else:
            position_pixel.append(positions[i])
    
    del positions
    
    for pixel in position_pixel:
        image_array[pixel[0], pixel[1], 0] = color[0]
        image_array[pixel[0], pixel[1], 1] = color[1]
        image_array[pixel[0], pixel[1], 2] = color[2]
    
    img = Image.fromarray(image_array, 'RGB')
    # img.save('my.png')
    if ret_img:
        return img
    else:
        img.show()


def remove_multiple_elements(arr:list):
    """
    """
    new = []
    for el in arr:
        if el not in new:
            new.append(el)
    return new


def matrix_add_to_every_entry(arr:list, add: float):
    """
    """
    for i in range(0, len(arr)):
        for j in range(0, len(arr[i])):
            arr[i][j] += add
    return arr


def remove_legend(
    image_array, 
    max_darker_area_height = 50,
    extract_image_array = True,
    show_image = False
    ):
    """
    """
    mean_gray = []
    for row_num in range(0, len(image_array)):
        mean_gray.append(np.mean(image_array[row_num]))

    max_difference = 0
    max_difference_position = 0
    for row_num in range(0, len(mean_gray)-1):
        this_difference = abs(mean_gray[row_num]-mean_gray[row_num+1])
        if this_difference > max_difference:
            max_difference = this_difference
            max_difference_position = row_num + 1
    
    if len(mean_gray) - max_difference_position > max_darker_area_height:
        max_difference_position = len(mean_gray)-max_darker_area_height
    
    reduced_image_array = image_array[:max_difference_position]
    
    if show_image:
        reduced_image = Image.fromarray(reduced_image_array)
        reduced_image.show()
        del reduced_image
    
    if extract_image_array:
        return reduced_image_array
    else:
        return max_difference_position


def max_gray_value(image_array):
    """
    """
    max_white = image_array[0][0]
    for row_num in range(0, len(image_array)):
        for col_num in range(1, len(image_array[row_num])):
            if image_array[row_num][col_num] >= max_white:
                max_white = image_array[row_num][col_num]
    return max_white


def start_white_boarder(image_array, max_white, ignore_whitespace_faults = True):
    """
    """
    stop_looking_for_faults = []
    for row_num in range(0, len(image_array)):
        start_white = 0
        for col_num in range(1, len(image_array[row_num])):
            if image_array[row_num][col_num] == max_white:
                if start_white == 0:
                    start_white = col_num
                    end_white = col_num
                else:
                    end_white = col_num
        if ignore_whitespace_faults:
            stop_looking_for_faults.append(start_white)
        else:
            stop_looking_for_faults.append(end_white)
    return stop_looking_for_faults


def widen_border(array, widen, low_border = 0, high_border = 10000):
    """
    """
    collect = []
    for i in range(0, len(array)):
        for j in range(array[i]-widen, array[i]+widen+1):
            if j > low_border and j < high_border:
                collect.append(j)
    
    return remove_multiple_elements(collect)


def find_defective(
    image_array, 
    max_darker_area_height = 50,
    gray_change_sensivity_ratio_horizontal = 0.15, 
    gray_change_sensivity_ratio_vertical = 0.2,
    compare_to_following = 3, 
    compare_min_value = 10,
    ignore_whitespace_faults = True,
    remove_next_to_defective = 0,
    show_image = False,
    ret_img = False,
    path = ""):
    """
    SIDE FUNCTION
    """
    #remove darker area at bottom
    reduced_image_array = remove_legend(image_array, max_darker_area_height)

    #get whitest pixel
    max_white = max_gray_value(copy.deepcopy(reduced_image_array))

    #search start and end of whitespace
    stop_looking_for_faults = start_white_boarder(reduced_image_array, max_white, ignore_whitespace_faults)

    #evaluate defective rows
    if compare_min_value < 1:
        compare_min_value = compare_min_value*max_white

    defective_rows = []
    fault_detect_location_horizontal = []
    reduced_image_array = matrix_add_to_every_entry(reduced_image_array, add=1)
    
    #horizontal elimination
    for row_num in range(0, len(reduced_image_array)):
        last_gray = reduced_image_array[row_num][0]
        for col_num in range(1, stop_looking_for_faults[row_num]-compare_to_following):
            this_gray = reduced_image_array[row_num][col_num+compare_to_following]
            if this_gray < last_gray*(1-gray_change_sensivity_ratio_horizontal) and last_gray >= compare_min_value:
                defective_rows.append(row_num)
                fault_detect_location_horizontal.append([row_num, col_num])
            last_gray = this_gray
    
    if show_image:
        edit_image(path, positions=fault_detect_location_horizontal, color=color_red)
    
    #vertical elimination
    for i in range(0, len(reduced_image_array)):
        if i not in defective_rows:
            begin_search = i
            break
    
    fault_detect_location_vertical = []
    
    for col_num in range(0, len(reduced_image_array[0])):
        last_gray = reduced_image_array[begin_search][col_num]
        for row_num in range(begin_search, len(reduced_image_array)-compare_to_following):
            if col_num >= stop_looking_for_faults[row_num]-2:
                continue
            this_gray = reduced_image_array[row_num+compare_to_following][col_num]
            if this_gray < last_gray*(1-gray_change_sensivity_ratio_vertical) and last_gray >= compare_min_value:
                defective_rows.append(row_num)
                fault_detect_location_vertical.append([row_num,col_num])
            else:
                last_gray = this_gray
    
    for col_num in range(0, len(reduced_image_array[0])):
        last_gray = reduced_image_array[begin_search][col_num]
        for row_num in range(begin_search, -1, -1):
            if col_num >= stop_looking_for_faults[row_num]-2:
                continue
            this_gray = reduced_image_array[row_num+compare_to_following][col_num]
            if this_gray < last_gray*(1-gray_change_sensivity_ratio_vertical) and last_gray >= compare_min_value:
                defective_rows.append(row_num)
                fault_detect_location_vertical.append([row_num,col_num])
            else:
                last_gray = this_gray
    
    if show_image:
        fault_detect_location_vertical = remove_multiple_elements(fault_detect_location_vertical)
        edit_image(path, positions=fault_detect_location_vertical, color=color_red)
    
    #remove multiple
    defective_rows = remove_multiple_elements(copy.deepcopy(defective_rows))
    defective_rows = widen_border(copy.deepcopy(defective_rows), remove_next_to_defective, high_border=len(reduced_image_array))

    # reduced_image_array = matrix_add_to_every_entry(reduced_image_array, add=-1)
    # for fault in fault_detect_location_horizontal:
    #     fault_detect_location_vertical.append(fault)
    # choose_starting_point(copy.deepcopy(reduced_image_array),0.8,fault_detect_location_vertical,0.5,stop_looking_for_faults)

    if show_image or ret_img:
        show_defective_rows = []
        for row_num in range(0, len(reduced_image_array)):
            if row_num not in defective_rows:
                show_defective_rows.append([row_num, "all"])
        show_suitable_rows = []
        for row_num in range(0, len(defective_rows)):
            show_suitable_rows.append([defective_rows[row_num], "all"])
        if show_image:
            edit_image(path, positions=show_suitable_rows, color=color_red)
            edit_image(path, positions=show_defective_rows, color=color_green)
        if ret_img:
            return edit_image(path, positions=show_suitable_rows, color=color_red, ret_img=True), edit_image(path, positions=show_defective_rows, color=color_green, ret_img=True)
        del show_defective_rows
        del show_suitable_rows
    
    reduced_image_array = matrix_add_to_every_entry(reduced_image_array, add=-1)
    
    return reduced_image_array, defective_rows


def find_closest_value(value, array):
    distance = []
    for i in range(0, len(array)):
        distance.append(abs(array[i]-value))
    return array[distance.index(min(distance))]


def remove_defective_rows(
    image_arrays,
    voltages,
    check_images_individually = False,
    remove_at_max = 0.75,
    reduce_by = 1.5,
    **kwargs
    ):
    """
    """
    find_defective_rows_settings = dict()

    for keys in default_defective_row_settings:
        #kwargs.setdefault(keys, default_defective_row_settings[keys])
        find_defective_rows_settings[keys] = kwargs[keys]

    undefective_image_arrays = []
    row_positions = []

    if check_images_individually:
        for i in range(0, len(image_arrays)):
            red_im_arr, def_rows = find_defective(image_arrays[i], **find_defective_rows_settings)
            undefective_image_arrays.append(np.delete(red_im_arr, def_rows, axis=0))
            this_row_positions = np.array([i for i in range(0, len(red_im_arr))])
            row_positions.append(np.delete(this_row_positions, def_rows, axis=0))
    else:
        last_voltage = max(voltages)
        store_progress_volt = []
        store_progress_ratio = []
        while True:
            max_voltage_position = voltages.index(last_voltage)
            reduced_image_array, defective_rows = find_defective(
                copy.deepcopy(image_arrays[max_voltage_position]), 
                **find_defective_rows_settings)
            def_real_ratio = len(defective_rows)/len(image_arrays[max_voltage_position])
            store_progress_volt.append(last_voltage)
            store_progress_ratio.append(def_real_ratio)
            if def_real_ratio<=remove_at_max:
                break
            else:
                new_voltage = find_closest_value(last_voltage/reduce_by, voltages)
                if new_voltage == last_voltage:
                    last_voltage = store_progress_volt[store_progress_ratio.index(min(store_progress_ratio))]
                    max_voltage_position = voltages.index(last_voltage)
                    reduced_image_array, defective_rows = find_defective(
                        copy.deepcopy(image_arrays[max_voltage_position]), 
                        **find_defective_rows_settings)
                    break
                last_voltage = new_voltage

        this_row_positions = np.array([i for i in range(0, len(reduced_image_array))])
        this_row_positions = np.delete(this_row_positions, defective_rows, axis=0)

        legend_start = remove_legend(copy.deepcopy(image_arrays[max_voltage_position]), kwargs["max_darker_area_height"], extract_image_array=False)
        
        for i in range(0, len(image_arrays)):
            if i != max_voltage_position:
                red_im_arr = image_arrays[i][:legend_start]
            else:
                red_im_arr = reduced_image_array
            
            undefective_image_arrays.append(np.delete(red_im_arr, defective_rows, axis=0))
            row_positions.append(this_row_positions)
    
    return np.array(undefective_image_arrays), np.array(row_positions)


"""

Exponential Fit

"""

def lifetime(x,L,n0,c):
    """
    Parameters
    ----------
    x : float
        distance from pn-junction
    L : float
        diffusion length
    n0 : float
        initial concentration of chare carriers

    Returns
    -------
    float
        charge carrier concentration at position x for carriers with diffusion length L

    """
    return n0*np.exp(x/L) + c


def cut_array(signal):
    """
    Cuts parts from signal not wanted for fitting
    """
    low = 0
    high = 0
    n = len(signal)
    max_value = max(signal)
    
    for i in range(n):
        if signal[i] > 0:
            low = i
            break
    for i in range(low,n):
        if signal[i] == max_value:
            high = i
            break
    
    result = np.empty(high-low)
    for i in range(high-low): #build new signal
        result[i] = signal[low + i]
    return result, low, high


def calc_diffusion_length(
    signal, 
    pix_to_length = 1.5038, 
    initial_values = [55,50,1]):
    """
    Parameters
    ----------
    signal : int array
        grey values for row y
    factor : float
        ratio of pixels to micrometers
    p : array [x0,L0]
        initial values for fit

    Returns
    -------
    float
        diffusionlength in micrometers

    """

    signal_fit = cut_array(signal)
    dist = np.linspace(signal_fit[1], signal_fit[2]-1, signal_fit[2] - signal_fit[1])
    #plt.plot(dist,signal_fit[0])

    popt, pcov = scipy.optimize.curve_fit(lifetime, dist, signal_fit[0], p0=initial_values)
    
    return popt[0]*pix_to_length


def calc_fit_params(
    signal, 
    initial_values = [55,50,1]):
    """
    Parameters
    ----------
    signal : int array
        grey values for row y
    factor : float
        ratio of pixels to micrometers
    p : array [x0,L0]
        initial values for fit

    Returns
    -------
    float
        diffusionlength in micrometers

    """

    signal_fit = cut_array(signal)
    dist = np.linspace(signal_fit[1], signal_fit[2]-1, signal_fit[2] - signal_fit[1])
    #plt.plot(dist,signal_fit[0])

    popt, pcov = scipy.optimize.curve_fit(lifetime, dist, signal_fit[0], p0=initial_values)
    
    return popt[0], popt[1], popt[2]

"""

Combining Functions

"""


def evaluate_images(
    path_to_directory, 
    provided_voltages = [],
    voltage_unit = "V",
    calc_y_dependence = True,
    pickle_name_y = "Diff_L_y/dly_last_pickle.pkl",
    calc_volt_dependence = "all", #mean, highest, largest_connected
    lines_for_evaluation = 20,
    deviation_for_highest = 0.05,
    pickle_name_volt = "Diff_L_volt/dlv_last_pickle.pkl",
    **kwargs
    ):
    """
    MAIN FUNCTION

    ARGUMENTS:
    - path:
    - backup_rows:
    - use_backup:

    KEYWORD - ARGUMENTS:
    - max_darker_area_height:
    - gray_change_sensivity_ratio_horizontal:
    - gray_change_sensivity_ratio_vertical:
    - compare_to_following:
    - compare_min_value:
    - ignore_whitespace_faults:
    """
    #check if directory exists:
    if not os.path.isdir(PICKLE_DIRECTORY_NAME + get_directory(pickle_name_y)):
        os.mkdir(PICKLE_DIRECTORY_NAME + get_directory(pickle_name_y))
    if not os.path.isdir(PICKLE_DIRECTORY_NAME + get_directory(pickle_name_volt)):
        os.mkdir(PICKLE_DIRECTORY_NAME + get_directory(pickle_name_volt))
    
    #retrieve default settings if not set manually
    remove_defective_rows_settings = dict()

    for keys in default_defective_row_settings:
        kwargs.setdefault(keys, default_defective_row_settings[keys])
        remove_defective_rows_settings[keys] = kwargs[keys]

    for keys in other_default_settings:
        kwargs.setdefault(keys, other_default_settings[keys])
    
    remove_defective_rows_settings["check_images_individually"] = kwargs["check_images_individually"]
    
    #retrieve picture file locations
    files = os.listdir(path_to_directory)
    files = remove_other_filetypes(copy.deepcopy(files), filetype=kwargs["filetype"])

    #retrieve voltage of every picture
    if len(provided_voltages) == 0:
        voltage = []
        for filename in files:
            in_number = False
            for char_pos in range(0, len(filename)):
                if filename[char_pos] in string_integers and not in_number:
                    start = char_pos
                    in_number = True
                elif filename[char_pos] not in string_integers and in_number:
                    voltage.append(float(filename[start:char_pos]))
                    break
            if not in_number:
                print("Not appended")
    else:
        voltage = provided_voltages

    #print(voltage)
    
    #retrieve image arrays
    image_arrays = []
    for filename in files:
        image_arrays.append(get_grayscale(path_to_directory + "/" + filename))
    image_arrays = np.array(image_arrays)

    #print(len(image_arrays), len(image_arrays[0]), len(image_arrays[0][0]))

    #remove defective rows from image arrays
    image_arrays, row_positions = remove_defective_rows(
        copy.deepcopy(image_arrays), 
        voltages=voltage,
        **remove_defective_rows_settings)
    
    # print(len(image_arrays), len(image_arrays[0]), len(image_arrays[0][0]))
    # print(len(row_positions), len(row_positions[0]))

    #calculate y dependence for every image
    diffusion_length_y = []
    for image_index in range(0, len(image_arrays)):
        this_diffusion_length_y = []
        for row_index in range(0, len(image_arrays[image_index])):
            this_diffusion_length_y.append(calc_diffusion_length(
                image_arrays[image_index][row_index],
                kwargs["pix_to_length"], 
                kwargs["initial_values"])
                )
        diffusion_length_y.append(this_diffusion_length_y)
    
    if calc_y_dependence:
        pickle_data_save = dict()
        pickle_data_save["voltage"] = voltage
        pickle_data_save["diffusion_length_y"] = diffusion_length_y
        pickle_data_save["row_positions"] = row_positions
        pickle_data_save["voltage_unit"] = voltage_unit
        with open(PICKLE_DIRECTORY_NAME + pickle_name_y, "wb") as fid:
            pickle.dump(pickle_data_save, fid)
    
    #calculate voltage dependence
    if calc_volt_dependence == "mean_all" or calc_volt_dependence == "all":
        diffusion_length = np.mean(np.array(diffusion_length_y), axis=1)
        
        pickle_data_save = dict()
        pickle_data_save["voltage"] = voltage
        pickle_data_save["diffusion_length"] = diffusion_length
        pickle_data_save["voltage_unit"] = voltage_unit

        this_name = pickle_name_volt[:len(pickle_name_volt)-4] + "_mean_all.pkl"
        with open(PICKLE_DIRECTORY_NAME + this_name, "wb") as fid:
            pickle.dump(pickle_data_save, fid)
    
    if calc_volt_dependence == "gray_mean_all" or calc_volt_dependence == "all":
        diffusion_length = []
        for image_index in range(0, len(image_arrays)):
            mean_gray = np.mean(np.array(image_arrays[image_index]), axis=0)
            diffusion_length.append(calc_diffusion_length(
                    mean_gray,
                    kwargs["pix_to_length"], 
                    kwargs["initial_values"]))
        
        del mean_gray

        pickle_data_save = dict()
        pickle_data_save["voltage"] = voltage
        pickle_data_save["diffusion_length"] = diffusion_length
        pickle_data_save["voltage_unit"] = voltage_unit

        this_name = pickle_name_volt[:len(pickle_name_volt)-4] + "_gray_mean_all.pkl"
        with open(PICKLE_DIRECTORY_NAME + this_name, "wb") as fid:
            pickle.dump(pickle_data_save, fid)
    
    if calc_volt_dependence == "highest_value_mean" or calc_volt_dependence == "all":
        diffusion_length = []
        for image_index in range(0, len(image_arrays)):
            highest_diff_L = []
            highest_diff_L_pos = []
            all_app_pos = []

            max_diff_L = max(diffusion_length_y[image_index])
            upper_border = max_diff_L*(1+deviation_for_highest)
            lower_border = max_diff_L*(1-deviation_for_highest)

            for diff_L in range(0, len(diffusion_length_y[image_index])):
                this_value = diffusion_length_y[image_index][diff_L]
                if this_value >= lower_border and this_value <= upper_border:
                    try:
                        if row_positions[diff_L] == row_positions[all_app_pos[-1]]+1:
                            if this_value > highest_diff_L[-1]:
                                highest_diff_L[-1] = this_value
                                highest_diff_L_pos[-1] = diff_L
                        else:
                            highest_diff_L.append(this_value)
                            highest_diff_L_pos.append(diff_L)
                        all_app_pos.append(diff_L)
                    except:
                        highest_diff_L.append(this_value)
                        highest_diff_L_pos.append(diff_L)
                        all_app_pos.append(diff_L)
            
            lines_for_evaluation = int(lines_for_evaluation/2)+1
            multiple_diff_L = []

            for i in range(0, len(highest_diff_L_pos)):
                last = highest_diff_L_pos[i]
                this_section = [last]
                for j in range(last+1, last+lines_for_evaluation+1):
                    if row_positions[j] == row_positions[last]+1:
                        this_section.append(j)
                        last = j
                    else:
                        break
                last = highest_diff_L_pos[i]
                for j in range(last-1,last-lines_for_evaluation-1,-1):
                    if row_positions[j] == row_positions[last]-1:
                        this_section.append(j)
                        last = j
                    else:
                        break
                multiple_diff_L.append(this_section)
            
            del highest_diff_L
            del highest_diff_L_pos
            del all_app_pos

            for i in range(0, len(multiple_diff_L)):
                for j in range(0, len(multiple_diff_L[i])):
                    multiple_diff_L[i][j] = diffusion_length_y[i][j]
            
            diffusion_length.append(np.mean(np.array(multiple_diff_L), axis=1))


    #nutzer, mittelwert, maximum



    
    # pickle_data_save = dict()
    # pickle_data_save["strings"] = copy_strings
    # with open(PICKLE_DIRECTORY_NAME + pickle_name + "/" + data_path_name + "_" + setting_name + ".pkl", "wb") as fid:
    #     pickle.dump(pickle_data_save, fid)

# a = np.array([])
# print(np.mean(np.array([[1,2,3],[1,2,3]]), axis=1))
# print(np.mean(np.array([1,2,3]), axis=0))


def sort_multiple(volts, others):
    """
    """
    sort_volt = [volts[0]]
    sort_others = []

    for i in range(0, len(others)):
        sort_others.append([others[i][0]])
    
    for i in range(1, len(volts)):
        appended = False
        for j in range(0, len(sort_volt)):
            if volts[i] < sort_volt[j]:
                sort_volt.insert(j, volts[i])
                for k in range(0, len(others)):
                    sort_others[k].insert(j, others[k][i])
                appended = True
                break
        if not appended:
            sort_volt.append(volts[i])
            for k in range(0, len(others)):
                sort_others[k].append(others[k][i])
    
    return sort_volt, sort_others


def create_nice_table(stuff, distance_to_first = 0, centered=False, max_cols = 0):
    """
    """
    lines = []

    col_size = []
    for i in range(0, len(stuff)):
        col_size.append(0)

    col_length = []
    for i in range(0, len(stuff)):
        col_length.append(len(stuff[i]))
        for j in range(0, len(stuff[i])):
            if len(str(stuff[i][j])) > col_size[i]:
                col_size[i] = len(str(stuff[i][j]))
    
    longest_col_length = max(col_length)

    if max_cols >= len(stuff):
        max_cols = 0
    
    if max_cols == 0:
        for row in range(0, longest_col_length):
            line = ""
            if row == 1:
                for i in range(0, distance_to_first):
                    lines.append("\n")
            for col in range(0, len(stuff)):
                try:
                    this_item = str(stuff[col][row])
                except:
                    continue
                this_item_length = len(this_item)
                if centered:
                    left = int((col_size[col]-this_item_length)/2)
                    right = col_size[col]-left-this_item_length
                else:
                    left = 0
                    right = col_size[col]-this_item_length
                line += left*" " + this_item + right*" " + " "
            line += "\n"
            lines.append(line)
    else:
        count_cols = max_cols
        last_start = 0

        while count_cols <= len(stuff):
            for row in range(0, longest_col_length):
                line = ""
                if row == 1:
                    for i in range(0, distance_to_first):
                        lines.append("\n")
                for col in range(last_start, count_cols):
                    try:
                        this_item = str(stuff[col][row])
                    except:
                        continue
                    this_item_length = len(this_item)
                    if centered:
                        left = int((col_size[col]-this_item_length)/2)
                        right = col_size[col]-left-this_item_length
                    else:
                        left = 0
                        right = col_size[col]-this_item_length
                    line += left*" " + this_item + right*" " + " "
                line += "\n"
                lines.append(line)
            lines.append("\n\n")
            
            if count_cols == len(stuff):
                break

            last_start = count_cols
            count_cols += max_cols
            if count_cols > len(stuff):
                count_cols = len(stuff)

    return lines


def create_text_file(pickle_path, save_path, volt_dep = True, round_decis = 2):
    """
    """
    with open(pickle_path, "rb") as fid:
        pickle_data_loaded = pickle.load(fid)

    if volt_dep:
        this_volt, this_others = sort_multiple(pickle_data_loaded["voltage"], [pickle_data_loaded["diffusion_length"], pickle_data_loaded["diffusion_std"]])
        this_diff_l = this_others[0]
        this_diff_std = this_others[1]

        txt_file = open(save_path + "_variant_3.txt", "w")
        txt_file.write("Explanation of data:")
        txt_file.write("\n\nLeft column: voltage (in " + pickle_data_loaded["voltage_unit"] + ")")
        txt_file.write("\nMiddle column: diffusion length (in \u00B5m)")
        txt_file.write("\nRight column: standard deviation of diffusion length (in \u00B5m)\n\n")

        for i in range(0, len(this_volt)):
            this_diff_l[i] = round(this_diff_l[i], round_decis)
            this_diff_std[i] = round(this_diff_std[i], round_decis)

        for i in range(0, len(this_volt)):
            txt_file.write(str(this_volt[i]) + " " + str(this_diff_l[i]) + " " + str(this_diff_std[i]) + "\n")
        txt_file.close()

        # txt_file = open(save_path + "_variant_3_plain.txt", "w")
        # for i in range(0, len(this_volt)):
        #     txt_file.write(str(this_volt[i]) + " " + str(this_diff_l[i]) + " " + str(this_diff_std[i]) + "\n")
        # txt_file.close()

        txt_file = open(save_path + "_variant_2.txt", "w")
        txt_file.write("Explanation of data:")
        txt_file.write("\n\nLeft column: voltage (in " + pickle_data_loaded["voltage_unit"] + ")")
        txt_file.write("\nMiddle column: diffusion length (in \u00B5m)")
        txt_file.write("\nRight column: standard deviation of diffusion length (in \u00B5m)\n\n")
        txt_file_lines = create_nice_table([this_volt, this_diff_l, this_diff_std])
        for line in txt_file_lines:
            txt_file.write(line)
        txt_file.close()

        # txt_file = open(save_path + "_variant_2_plain.txt", "w")
        # for line in txt_file_lines:
        #     txt_file.write(line)
        # txt_file.close()

        txt_file = open(save_path + "_variant_1.txt", "w")
        txt_file.write("Explanation of data:")
        txt_file.write("\n\nLeft column: voltage (in " + pickle_data_loaded["voltage_unit"] + ")")
        txt_file.write("\nMiddle column: diffusion length (in \u00B5m)")
        txt_file.write("\nRight column: standard deviation of diffusion length (in \u00B5m)\n\n")
        txt_file_lines = create_nice_table([this_volt, this_diff_l, this_diff_std], centered=True)
        for line in txt_file_lines:
            txt_file.write(line)
        txt_file.close()

        # txt_file = open(save_path + "_variant_1_plain.txt", "w")
        # txt_file_lines = create_nice_table([this_volt, this_diff_l, this_diff_std], centered=True)
        # for line in txt_file_lines:
        #     txt_file.write(line)
        # txt_file.close()

    else:
        this_volt, this_others = sort_multiple(pickle_data_loaded["voltage"], [pickle_data_loaded["diffusion_length_y"], pickle_data_loaded["row_positions"]])
        this_diff_l = this_others[0]
        this_row_pos = this_others[1]

        txt_file = open(save_path + "_variant_3.txt", "w")
        txt_file.write("You should see twice as much columns as images correctly provided to this program:")
        txt_file.write("\nIn other words: two columns per voltage.")
        txt_file.write("\n\u2219 Each left column (columns with unequal number if you start counting at one)\n  provide the position (row) parallel to the pn junction.\n  0 would be the top row of the image, the highest would refer to the bottom row of the image.")
        txt_file.write("\n\u2219 Each right column (columns with equal number if you start counting at one)\n  provide the diffusion length of the corresponding row (in \u00B5m).")

        txt_file.write("\n\nCorresponding voltage values from left to rigth (in " + pickle_data_loaded["voltage_unit"] + "):\n")
        for i in range(0, len(this_volt)):
            if i == len(this_volt)-1:
                txt_file.write(str(this_volt[i]))
            else:
                txt_file.write(str(this_volt[i]) + " ")

        txt_file.write("\n\n")

        collected_lengths = []
        for i in range(0, len(this_diff_l)):
            collected_lengths.append(len(this_diff_l[i]))

        for i in range(0, max(collected_lengths)):
            for j in range(0, len(this_volt)):
                try:
                    txt_file.write(str(round(this_row_pos[j][i],round_decis)) + " ")
                    txt_file.write(str(round(this_diff_l[j][i],round_decis)) + " ")
                except:
                    continue
            txt_file.write("\n")

        txt_file.close()

        # txt_file = open(save_path + "_variant_3_plain.txt", "w")

        # collected_lengths = []
        # for i in range(0, len(this_diff_l)):
        #     collected_lengths.append(len(this_diff_l[i]))

        # for i in range(0, max(collected_lengths)):
        #     for j in range(0, len(this_volt)):
        #         try:
        #             txt_file.write(str(round(this_row_pos[j][i],round_decis)) + " ")
        #             txt_file.write(str(round(this_diff_l[j][i],round_decis)) + " ")
        #         except:
        #             continue
        #     txt_file.write("\n")

        # txt_file.close()

        #prepare data
        new_diff_L = []
        new_row_pos = []
        for i in range(0, len(this_volt)):
            new_arr = []
            for j in range(0, len(this_diff_l[i])):
                new_arr.append(round(this_diff_l[i][j], round_decis))
            new_diff_L.append(new_arr)
            del new_arr
            new_arr = []
            for j in range(0, len(this_row_pos[i])):
                new_arr.append(round(this_row_pos[i][j], round_decis))
            new_row_pos.append(new_arr)
            del new_arr

        for i in range(0, len(this_volt)):
            # this_text = "U=" + str(this_volt[i]) + pickle_data_loaded["voltage_unit"]
            new_diff_L[i].insert(0, "U=" + str(this_volt[i]) + pickle_data_loaded["voltage_unit"])
            new_row_pos[i].insert(0, "U=" + str(this_volt[i]) + pickle_data_loaded["voltage_unit"])
        
        transfrom = []
        for i in range(0, len(new_diff_L)):
            transfrom.append(new_row_pos[i])
            transfrom.append(new_diff_L[i])
        
        txt_file_lines = create_nice_table(transfrom, max_cols=14)

        txt_file = open(save_path + "_variant_2.txt", "w")
        txt_file.write("You should see twice as much columns as images correctly provided to this program (the remaining might hide below the ones you see):")
        txt_file.write("\nIn other words: two columns per voltage.")
        txt_file.write("\n\u2219 Each left column (columns with unequal number if you start counting at one)\n  provide the position (row) parallel to the pn junction.\n  0 would be the top row of the image, the highest would refer to the bottom row of the image.")
        txt_file.write("\n\u2219 Each right column (columns with equal number if you start counting at one)\n  provide the diffusion length of the corresponding row (in \u00B5m).\n\n")

        for line in txt_file_lines:
            txt_file.write(line)
        txt_file.close()

        # txt_file = open(save_path + "_variant_2_plain.txt", "w")
        # for line in range(0, len(txt_file_lines)):
        #     txt_file.write(txt_file_lines[line])
        # txt_file.close()

        txt_file = open(save_path + "_variant_1.txt", "w")
        txt_file.write("You should see twice as much columns as images correctly provided to this program (the remaining might hide below the ones you see):")
        txt_file.write("\nIn other words: two columns per voltage.")
        txt_file.write("\n\u2219 Each left column (columns with unequal number if you start counting at one)\n  provide the position (row) parallel to the pn junction.\n  0 would be the top row of the image, the highest would refer to the bottom row of the image.")
        txt_file.write("\n\u2219 Each right column (columns with equal number if you start counting at one)\n  provide the diffusion length of the corresponding row (in \u00B5m).\n\n")

        txt_file_lines = create_nice_table(transfrom, centered=True, max_cols=14)

        for line in txt_file_lines:
            txt_file.write(line)
        txt_file.close()

        # txt_file = open(save_path + "_variant_1_plain.txt", "w")
        # for line in range(0, len(txt_file_lines)):
        #     txt_file.write(txt_file_lines[line])
        # txt_file.close()


def final_computation_interface(
    automatic_defect_detect,
    directory,
    picture_file_names, 
    picture_voltage_values, 
    manually_chosen_borders, 
    pickle_name_y = "Diff_L_y/dly_last_pickle.pkl",
    pickle_name_volt = "Diff_L_volt/dlv_last_pickle",
    pickle_name_exp = "Exp_fit/ef_last_pickle",
    voltage_unit = "V",
    remove_unnecessary = True,
    **kwargs
    ):
    """
    """
    #check if directory exists:
    if not os.path.isdir(PICKLE_DIRECTORY_NAME + get_directory(pickle_name_y)):
        os.mkdir(PICKLE_DIRECTORY_NAME + get_directory(pickle_name_y))
    else:
        if remove_unnecessary:
            delete_these = os.listdir(PICKLE_DIRECTORY_NAME + get_directory(pickle_name_y))
            for delete_this in delete_these:
                os.remove(PICKLE_DIRECTORY_NAME + get_directory(pickle_name_y) + delete_this)
    if not os.path.isdir(PICKLE_DIRECTORY_NAME + get_directory(pickle_name_volt)):
        os.mkdir(PICKLE_DIRECTORY_NAME + get_directory(pickle_name_volt))
    else:
        if remove_unnecessary:
            delete_these = os.listdir(PICKLE_DIRECTORY_NAME + get_directory(pickle_name_volt))
            for delete_this in delete_these:
                os.remove(PICKLE_DIRECTORY_NAME + get_directory(pickle_name_volt) + delete_this)
    if not os.path.isdir(PICKLE_DIRECTORY_NAME + get_directory(pickle_name_exp)):
        os.mkdir(PICKLE_DIRECTORY_NAME + get_directory(pickle_name_exp))
    else:
        if remove_unnecessary:
            delete_these = os.listdir(PICKLE_DIRECTORY_NAME + get_directory(pickle_name_exp))
            for delete_this in delete_these:
                os.remove(PICKLE_DIRECTORY_NAME + get_directory(pickle_name_exp) + delete_this)
    if not os.path.isdir(TEMP_PLOTS_DIRECTORY_NAME):
        os.mkdir(TEMP_PLOTS_DIRECTORY_NAME)
    else:
        if remove_unnecessary:
            delete_these = os.listdir(TEMP_PLOTS_DIRECTORY_NAME)
            for delete_this in delete_these:
                os.remove(TEMP_PLOTS_DIRECTORY_NAME + delete_this)
    if not os.path.isdir(Temp_TEXT_DIRECTORY_NAME + get_directory(pickle_name_y)):
        os.mkdir(Temp_TEXT_DIRECTORY_NAME + get_directory(pickle_name_y))
    else:
        if remove_unnecessary:
            delete_these = os.listdir(Temp_TEXT_DIRECTORY_NAME + get_directory(pickle_name_y))
            for delete_this in delete_these:
                os.remove(Temp_TEXT_DIRECTORY_NAME + get_directory(pickle_name_y) + delete_this)
    if not os.path.isdir(Temp_TEXT_DIRECTORY_NAME + get_directory(pickle_name_volt)):
        os.mkdir(Temp_TEXT_DIRECTORY_NAME + get_directory(pickle_name_volt))
    else:
        if remove_unnecessary:
            delete_these = os.listdir(Temp_TEXT_DIRECTORY_NAME + get_directory(pickle_name_volt))
            for delete_this in delete_these:
                os.remove(Temp_TEXT_DIRECTORY_NAME + get_directory(pickle_name_volt) + delete_this)
    
    #retrieve default settings if not set manually
    remove_defective_rows_settings = dict()

    for keys in default_defective_row_settings:
        kwargs.setdefault(keys, default_defective_row_settings[keys])
        remove_defective_rows_settings[keys] = kwargs[keys]

    for keys in other_default_settings:
        kwargs.setdefault(keys, other_default_settings[keys])
    
    remove_defective_rows_settings["check_images_individually"] = kwargs["check_images_individually"]
    remove_defective_rows_settings["remove_at_max"] = kwargs["remove_at_max"]
    remove_defective_rows_settings["reduce_by"] = kwargs["reduce_by"]

    #retrieve image arrays
    image_arrays = []
    for filename in picture_file_names:
        image_arrays.append(get_grayscale(directory + "/" + filename))
    image_arrays = np.array(image_arrays)

    #remove defective rows from image arrays
    if automatic_defect_detect:
        image_arrays, row_positions = remove_defective_rows(
            copy.deepcopy(image_arrays), 
            voltages=picture_voltage_values,
            **remove_defective_rows_settings)
    else:
        img_arr_cop = copy.deepcopy(image_arrays)
        del image_arrays
        image_arrays = []
        row_positions = []
        single_row_pos = []

        ordered_borders = [manually_chosen_borders[0]]
        for i in range(0, len(manually_chosen_borders)):
            border_appended = False
            for j in range(0, len(ordered_borders)):
                if manually_chosen_borders[i][0] < ordered_borders[j][0]:
                    ordered_borders.insert(j, manually_chosen_borders[i])
                    border_appended = True
                    break
            if not border_appended:
                ordered_borders.append(manually_chosen_borders[i])
        
        for i in range(0, len(ordered_borders)):
            for j in range(ordered_borders[i][0], ordered_borders[i][1]+1):
                single_row_pos.append(j)
        
        for i in range(0, len(img_arr_cop)):
            this_arr = []
            for j in single_row_pos:
                this_arr.append(img_arr_cop[i][j])
            image_arrays.append(this_arr)
            row_positions.append(single_row_pos)
        
        del single_row_pos
        del this_arr
        del img_arr_cop
        image_arrays = np.array(image_arrays)
        row_positions = np.array(row_positions)
    
    #calculate y dependence for every image
    diffusion_length_y = []
    exp_fit_params = []
    uncalculatable_rows = []
    for image_index in range(0, len(image_arrays)):
        this_diffusion_length_y = []
        this_fit_params = []
        for row_index in range(0, len(image_arrays[image_index])):
            if row_index not in uncalculatable_rows:
                try:
                    this_diffusion_length_y.append(calc_diffusion_length(
                        image_arrays[image_index][row_index],
                        kwargs["pix_to_length"], 
                        kwargs["initial_values"])
                        )
                    this_fit_params.append(calc_fit_params(
                        image_arrays[image_index][row_index], 
                        kwargs["initial_values"])
                        )
                except:
                    uncalculatable_rows.append(row_index)

        diffusion_length_y.append(this_diffusion_length_y)
        exp_fit_params.append(this_fit_params)
    
    print("For a total of " + str(len(uncalculatable_rows)) + " rows, it was not possible to calculate the diffusion length.")
    copy_image_arrays = []
    copy_row_positions = []
    for g in range(0, len(image_arrays)):
        copy_image_arrays.append(np.delete(image_arrays[g],uncalculatable_rows,axis=0))
        copy_row_positions.append(np.delete(row_positions[g],uncalculatable_rows,axis=0))
    del image_arrays
    del row_positions
    image_arrays = np.array(copy_image_arrays)
    row_positions = np.array(copy_row_positions)

    
    pickle_data_save = dict()
    pickle_data_save["voltage"] = picture_voltage_values
    pickle_data_save["diffusion_length_y"] = diffusion_length_y
    pickle_data_save["row_positions"] = row_positions
    pickle_data_save["voltage_unit"] = voltage_unit
    with open(PICKLE_DIRECTORY_NAME + pickle_name_y, "wb") as fid:
        pickle.dump(pickle_data_save, fid)
    
    critical_rows = []
    sec_size = 10
    eps_factor = 1.6
    for image_index in range(0, len(image_arrays)):
        collect_sec_std = []
        for diff_value in range(0, len(diffusion_length_y[image_index])-sec_size):
            section = diffusion_length_y[image_index][diff_value:diff_value+sec_size]
            section_std = np.std(section)
            #print(picture_voltage_values[image_index], row_positions[image_index][diff_value], section_std)
            collect_sec_std.append(section_std)
        eps = np.mean(collect_sec_std)
        for diff_value in range(0, len(diffusion_length_y[image_index])-sec_size):
            section = diffusion_length_y[image_index][diff_value:diff_value+sec_size]
            section_std = np.std(section)
            if section_std > eps*eps_factor:
                for j in range(diff_value, diff_value+sec_size):
                    critical_rows.append(row_positions[image_index][j])
        #print(np.mean(collect_sec_std))
            
    critical_rows = remove_multiple_elements(critical_rows)
    #critical_rows = []
    
    #calculate voltage dependence
    if kwargs["volt_dep_method"] == "mean_normal" or kwargs["volt_dep_method"] == "all":
        diffusion_length = np.mean(np.array(diffusion_length_y), axis=1)
        diffusion_std = np.std(np.array(diffusion_length_y), axis=1)
        
        pickle_data_save = dict()
        pickle_data_save["voltage"] = picture_voltage_values
        pickle_data_save["diffusion_length"] = diffusion_length
        pickle_data_save["diffusion_std"] = diffusion_std
        pickle_data_save["voltage_unit"] = voltage_unit

        #this_name = pickle_name_volt[:len(pickle_name_volt)-4] + "_mean.pkl"
        this_name = pickle_name_volt + "_mean.pkl"
        with open(PICKLE_DIRECTORY_NAME + this_name, "wb") as fid:
            pickle.dump(pickle_data_save, fid)
        
        #exp fit
        this_name_exp = pickle_name_exp + "_mean.pkl"
        mean_fit_params = []
        mean_points = []
        for it_im in range(0, len(exp_fit_params)):
            mean_fit_params.append(np.mean(np.array(copy.deepcopy(exp_fit_params[it_im])), axis=0))
        mean_fit_params = np.array(mean_fit_params)
        for it_im in range(0, len(image_arrays)):
            mean_points.append(np.mean(np.array(copy.deepcopy(image_arrays[it_im])), axis=0))
        mean_points = np.array(mean_points)

        del pickle_data_save
        pickle_data_save = dict()
        pickle_data_save["voltage"] = picture_voltage_values
        pickle_data_save["voltage_unit"] = voltage_unit
        pickle_data_save["fit_params"] = mean_fit_params
        pickle_data_save["points"] = mean_points
        pickle_data_save["point_position"] = row_positions

        with open(PICKLE_DIRECTORY_NAME + this_name_exp, "wb") as fid:
            pickle.dump(pickle_data_save, fid)

    if kwargs["volt_dep_method"] == "mean_gray" or kwargs["volt_dep_method"] == "all":
        diffusion_length = []
        diffusion_std = []
        for image_index in range(0, len(image_arrays)):
            mean_gray = np.mean(np.array(image_arrays[image_index]), axis=0)
            mean_gray_std = np.std(np.array(image_arrays[image_index]), axis=0)
            diffusion_length.append(calc_diffusion_length(
                    mean_gray,
                    kwargs["pix_to_length"], 
                    kwargs["initial_values"]))
            weird_factor = abs(max(diffusion_length_y[image_index])-min(diffusion_length_y[image_index]))/255
            diffusion_std.append(np.mean(mean_gray_std)*weird_factor)
        
        del mean_gray

        pickle_data_save = dict()
        pickle_data_save["voltage"] = picture_voltage_values
        pickle_data_save["diffusion_length"] = diffusion_length
        pickle_data_save["diffusion_std"] = diffusion_std
        pickle_data_save["voltage_unit"] = voltage_unit

        #this_name = pickle_name_volt[:len(pickle_name_volt)-4] + "_mean-gray.pkl"
        this_name = pickle_name_volt + "_mean-gray.pkl"
        with open(PICKLE_DIRECTORY_NAME + this_name, "wb") as fid:
            pickle.dump(pickle_data_save, fid)
        
        #exp fit
        this_name_exp = pickle_name_exp + "_mean-gray.pkl"
        mean_gray_fit_params = []
        mean_gray_points = []
        for it_im in range(0, len(exp_fit_params)):
            mean_gray_fit_params.append(np.mean(np.array(copy.deepcopy(exp_fit_params[it_im])), axis=0))
        mean_gray_fit_params = np.array(mean_gray_fit_params)
        for it_im in range(0, len(image_arrays)):
            mean_gray_points.append(np.mean(np.array(copy.deepcopy(image_arrays[it_im])), axis=0))
        mean_gray_points = np.array(mean_gray_points)

        del pickle_data_save
        pickle_data_save = dict()
        pickle_data_save["voltage"] = picture_voltage_values
        pickle_data_save["voltage_unit"] = voltage_unit
        pickle_data_save["fit_params"] = mean_gray_fit_params
        pickle_data_save["points"] = mean_gray_points
        pickle_data_save["point_position"] = row_positions

        with open(PICKLE_DIRECTORY_NAME + this_name_exp, "wb") as fid:
            pickle.dump(pickle_data_save, fid)
    
    if kwargs["volt_dep_method"] == "highest_variable_normal" or kwargs["volt_dep_method"] == "all":
        diffusion_length = []
        diffusion_std = []

        highest_exp_fit_params = []
        highest_image_positions = []

        for image_index in range(0, len(image_arrays)):
            # max_diff_L = max(diffusion_length_y[image_index])
            # highest_diff_L_pos = diffusion_length_y[image_index].index(max_diff_L)
            this_sorted_diff_l_y, this_sorted_rowis = sort_multiple(copy.deepcopy(diffusion_length_y[image_index]),[copy.deepcopy(row_positions[image_index])])
            this_sorted_rowis = this_sorted_rowis[0]

            for i in range(len(this_sorted_diff_l_y)-1, -1, -1):
                if this_sorted_rowis[i] not in critical_rows:
                    max_diff_L = this_sorted_diff_l_y[i]
                    highest_diff_L_pos = diffusion_length_y[image_index].index(max_diff_L)
                    break

            close_to_high = [max_diff_L]
            this_exp_fit_params = [exp_fit_params[image_index][highest_diff_L_pos]]
            this_img_positions = [image_arrays[image_index][highest_diff_L_pos]]
            steps = int(kwargs["lines_next_highest"]/2) + 1

            if highest_diff_L_pos+steps > len(diffusion_length_y[image_index])-1:
                upper_border = len(diffusion_length_y[image_index])-1
            else:
                upper_border = highest_diff_L_pos+steps
            
            if highest_diff_L_pos-steps < 0:
                lower_border = 0
            else:
                lower_border = highest_diff_L_pos-steps

            last_row = row_positions[image_index][highest_diff_L_pos]
            #print("var", last_row)
            for i in range(highest_diff_L_pos+1, upper_border+1):
                if row_positions[image_index][i] not in critical_rows:
                    if row_positions[image_index][i] == last_row + 1:
                        close_to_high.append(diffusion_length_y[image_index][i])
                        this_exp_fit_params.append(exp_fit_params[image_index][i])
                        this_img_positions.append(image_arrays[image_index][i])
                        last_row = row_positions[image_index][i]
                    else:
                        break
                else:
                    break
            last_row = row_positions[image_index][highest_diff_L_pos]
            for i in range(highest_diff_L_pos-1, lower_border-1, -1):
                if row_positions[image_index][i] not in critical_rows:
                    if row_positions[image_index][i] == last_row - 1:
                        close_to_high.append(diffusion_length_y[image_index][i])
                        this_exp_fit_params.append(exp_fit_params[image_index][i])
                        this_img_positions.append(image_arrays[image_index][i])
                        last_row = row_positions[image_index][i]
                    else:
                        break
                else:
                    break
            
            close_to_high = np.array(close_to_high)
            diffusion_length.append(np.mean(close_to_high))
            diffusion_std.append(np.std(close_to_high))

            this_exp_fit_params = np.array(this_exp_fit_params)
            this_img_positions = np.array(this_img_positions)
            highest_exp_fit_params.append(np.mean(this_exp_fit_params, axis=0))
            highest_image_positions.append(np.mean(this_img_positions, axis=0))

        pickle_data_save = dict()
        pickle_data_save["voltage"] = picture_voltage_values
        pickle_data_save["diffusion_length"] = diffusion_length
        pickle_data_save["diffusion_std"] = diffusion_std
        pickle_data_save["voltage_unit"] = voltage_unit

        #this_name = pickle_name_volt[:len(pickle_name_volt)-4] + "_highest-row-variable.pkl"
        this_name = pickle_name_volt + "_highest-variable.pkl"
        with open(PICKLE_DIRECTORY_NAME + this_name, "wb") as fid:
            pickle.dump(pickle_data_save, fid)
        
        #exp fit
        this_name_exp = pickle_name_exp + "_highest-variable.pkl"

        del pickle_data_save
        pickle_data_save = dict()
        pickle_data_save["voltage"] = picture_voltage_values
        pickle_data_save["voltage_unit"] = voltage_unit
        pickle_data_save["fit_params"] = highest_exp_fit_params
        pickle_data_save["points"] = highest_image_positions
        pickle_data_save["point_position"] = row_positions

        with open(PICKLE_DIRECTORY_NAME + this_name_exp, "wb") as fid:
            pickle.dump(pickle_data_save, fid)
    
    if kwargs["volt_dep_method"] == "highest_variable_gray" or kwargs["volt_dep_method"] == "all":
        diffusion_length = []
        diffusion_std = []

        highest_gray_exp_fit_params = []
        highest_gray_image_positions = []

        for image_index in range(0, len(image_arrays)):

            this_sorted_diff_l_y, this_sorted_rowis = sort_multiple(copy.deepcopy(diffusion_length_y[image_index]),[copy.deepcopy(row_positions[image_index])])
            this_sorted_rowis = this_sorted_rowis[0]

            for i in range(len(this_sorted_diff_l_y)-1, -1, -1):
                if this_sorted_rowis[i] not in critical_rows:
                    max_diff_L = this_sorted_diff_l_y[i]
                    highest_diff_L_pos = diffusion_length_y[image_index].index(max_diff_L)
                    break

            close_to_high = [image_arrays[image_index][highest_diff_L_pos]]
            steps = int(kwargs["lines_next_highest"]/2) + 1

            if highest_diff_L_pos+steps > len(diffusion_length_y[image_index])-1:
                upper_border = len(diffusion_length_y[image_index])-1
            else:
                upper_border = highest_diff_L_pos+steps
            
            if highest_diff_L_pos-steps < 0:
                lower_border = 0
            else:
                lower_border = highest_diff_L_pos-steps

            last_row = row_positions[image_index][highest_diff_L_pos]
            for i in range(highest_diff_L_pos+1, upper_border+1):
                if row_positions[image_index][i] not in critical_rows:
                    if row_positions[image_index][i] == last_row + 1:
                        close_to_high.append(image_arrays[image_index][i])
                        last_row = row_positions[image_index][i]
                    else:
                        break
                else:
                    break
            last_row = row_positions[image_index][highest_diff_L_pos]
            for i in range(highest_diff_L_pos-1, lower_border-1, -1):
                if row_positions[image_index][i] not in critical_rows:
                    if row_positions[image_index][i] == last_row - 1:
                        close_to_high.append(image_arrays[image_index][i])
                        last_row = row_positions[image_index][i]
                    else:
                        break
                else:
                    break
                    
            close_to_high = np.array(close_to_high)
            mean_gray = np.mean(close_to_high, axis=0)
            mean_gray_std = np.std(close_to_high, axis=0)

            weird_factor = abs(max(diffusion_length_y[image_index])-min(diffusion_length_y[image_index]))/255

            diffusion_length.append(calc_diffusion_length(
                    mean_gray,
                    kwargs["pix_to_length"], 
                    kwargs["initial_values"]))
            diffusion_std.append(np.mean(mean_gray_std)*weird_factor)

            highest_gray_exp_fit_params.append(calc_fit_params(
                    mean_gray,
                    kwargs["initial_values"]
            ))
            highest_gray_image_positions.append(mean_gray)

        pickle_data_save = dict()
        pickle_data_save["voltage"] = picture_voltage_values
        pickle_data_save["diffusion_length"] = diffusion_length
        pickle_data_save["diffusion_std"] = diffusion_std
        pickle_data_save["voltage_unit"] = voltage_unit

        # this_name = pickle_name_volt[:len(pickle_name_volt)-4] + "_highest-row-variable-gray.pkl"
        this_name = pickle_name_volt + "_highest-variable-gray.pkl"
        with open(PICKLE_DIRECTORY_NAME + this_name, "wb") as fid:
            pickle.dump(pickle_data_save, fid)
        
        #exp fit
        this_name_exp = pickle_name_exp + "_highest-variable-gray.pkl"

        del pickle_data_save
        pickle_data_save = dict()
        pickle_data_save["voltage"] = picture_voltage_values
        pickle_data_save["voltage_unit"] = voltage_unit
        pickle_data_save["fit_params"] = highest_gray_exp_fit_params
        pickle_data_save["points"] = highest_gray_image_positions
        pickle_data_save["point_position"] = row_positions

        with open(PICKLE_DIRECTORY_NAME + this_name_exp, "wb") as fid:
            pickle.dump(pickle_data_save, fid)
    
    if kwargs["volt_dep_method"] == "highest_fixed_normal" or kwargs["volt_dep_method"] == "all":
        diffusion_length = []
        diffusion_std = []

        fixed_exp_fit_params = []
        fixed_points = []

        total_diff = []
        row_number = []

        for image_index in range(0, len(image_arrays)):
            for diff_value in range(0, len(diffusion_length_y[image_index])):
                row_found = False
                this_row = row_positions[image_index][diff_value]
                this_value = diffusion_length_y[image_index][diff_value]
                if this_row not in critical_rows:
                    for row in range(0, len(row_number)):
                        if this_row == row_number[row]:
                            row_found = True
                            total_diff[row] += this_value
                            break
                    if not row_found:
                        row_number.append(this_row)
                        total_diff.append(this_value)
        
        sort_total_diff, sort_row_number = sort_multiple(total_diff, [row_number])
        sort_row_number = sort_row_number[0]

        hi_diff_l_row = -1
        for i in range(len(sort_row_number)-1, -1, -1):
            non_missing = True
            for image_i in range(0, len(row_positions)):
                if sort_row_number[i] not in row_positions[image_i]:
                    non_missing = False
                    break
            if non_missing:
                hi_diff_l_row = sort_row_number[i]
                break
        
        if hi_diff_l_row == -1:
            print("Critical error: images do not share one undefective row. Hint: do not choose to evaluate defective rows for every image individually.")
            return

        steps = int(kwargs["lines_next_highest"]/2) + 1

        for image_index in range(0, len(image_arrays)):
            row_pos, = np.where(row_positions[image_index] == hi_diff_l_row)
            row_pos = row_pos[0]
            #row_pos = row_positions[image_index].index(hi_diff_l_row)
            close_to_high = [diffusion_length_y[image_index][row_pos]]
            this_fit_params = [exp_fit_params[image_index][row_pos]]
            this_img_positions = [image_arrays[image_index][row_pos]]

            if row_pos+steps > len(diffusion_length_y[image_index])-1:
                upper_border = len(diffusion_length_y[image_index])-1
            else:
                upper_border = row_pos+steps
            
            if row_pos-steps < 0:
                lower_border = 0
            else:
                lower_border = row_pos-steps

            last_row = row_positions[image_index][row_pos]
            for i in range(row_pos+1, upper_border+1):
                if row_positions[image_index][i] not in critical_rows:
                    if row_positions[image_index][i] == last_row + 1:
                        close_to_high.append(diffusion_length_y[image_index][i])
                        this_fit_params.append(exp_fit_params[image_index][i])
                        this_img_positions.append(image_arrays[image_index][i])
                        last_row = row_positions[image_index][i]
                    else:
                        break
                else:
                    break

            last_row = row_positions[image_index][row_pos]
            for i in range(row_pos-1, lower_border-1, -1):
                if row_positions[image_index][i] not in critical_rows:
                    if row_positions[image_index][i] == last_row - 1:
                        close_to_high.append(diffusion_length_y[image_index][i])
                        this_fit_params.append(exp_fit_params[image_index][i])
                        this_img_positions.append(image_arrays[image_index][i])
                        last_row = row_positions[image_index][i]
                    else:
                        break
                else:
                    break

        
            close_to_high = np.array(close_to_high)
            diffusion_length.append(np.mean(close_to_high))
            diffusion_std.append(np.std(close_to_high))

            this_fit_params = np.array(this_fit_params)
            this_img_positions = np.array(this_img_positions)
            fixed_exp_fit_params.append(np.mean(this_fit_params, axis=0))
            fixed_points.append(np.mean(this_img_positions, axis=0))
        
        pickle_data_save = dict()
        pickle_data_save["voltage"] = picture_voltage_values
        pickle_data_save["diffusion_length"] = diffusion_length
        pickle_data_save["diffusion_std"] = diffusion_std
        pickle_data_save["voltage_unit"] = voltage_unit

        # this_name = pickle_name_volt[:len(pickle_name_volt)-4] + "_highest-row-fixed.pkl"
        this_name = pickle_name_volt + "_highest-fixed.pkl"
        with open(PICKLE_DIRECTORY_NAME + this_name, "wb") as fid:
            pickle.dump(pickle_data_save, fid)
        
        #exp fit
        this_name_exp = pickle_name_exp + "_highest-fixed.pkl"

        del pickle_data_save
        pickle_data_save = dict()
        pickle_data_save["voltage"] = picture_voltage_values
        pickle_data_save["voltage_unit"] = voltage_unit
        pickle_data_save["fit_params"] = fixed_exp_fit_params
        pickle_data_save["points"] = fixed_points
        pickle_data_save["point_position"] = row_positions

        with open(PICKLE_DIRECTORY_NAME + this_name_exp, "wb") as fid:
            pickle.dump(pickle_data_save, fid)
    
    if kwargs["volt_dep_method"] == "highest_fixed_gray" or kwargs["volt_dep_method"] == "all":
        diffusion_length = []
        diffusion_std = []

        fixed_gray_exp_fit_params = []
        fixed_gray_image_positions = []

        total_diff = []
        row_number = []

        for image_index in range(0, len(image_arrays)):
            for diff_value in range(0, len(diffusion_length_y[image_index])):
                row_found = False
                this_row = row_positions[image_index][diff_value]
                this_value = diffusion_length_y[image_index][diff_value]
                if this_row not in critical_rows:
                    for row in range(0, len(row_number)):
                        if this_row == row_number[row]:
                            row_found = True
                            total_diff[row] += this_value
                            break
                    if not row_found:
                        row_number.append(this_row)
                        total_diff.append(this_value)
        
        sort_total_diff, sort_row_number = sort_multiple(total_diff, [row_number])
        sort_row_number = sort_row_number[0]

        hi_diff_l_row = -1
        for i in range(len(sort_row_number)-1, -1, -1):
            non_missing = True
            for image_i in range(0, len(row_positions)):
                if sort_row_number[i] not in row_positions[image_i]:
                    non_missing = False
                    break
            if non_missing:
                hi_diff_l_row = sort_row_number[i]
                break
        
        if hi_diff_l_row == -1:
            print("Critical error: images do not share one undefective row. Hint: do not choose to evaluate defective rows for every image individually.")
            return

        steps = int(kwargs["lines_next_highest"]/2) + 1

        for image_index in range(0, len(image_arrays)):
            row_pos, = np.where(row_positions[image_index] == hi_diff_l_row)
            row_pos = row_pos[0]
            #row_pos = row_positions[image_index].index(hi_diff_l_row)
            close_to_high = [image_arrays[image_index][row_pos]]

            if row_pos+steps > len(diffusion_length_y[image_index])-1:
                upper_border = len(diffusion_length_y[image_index])-1
            else:
                upper_border = row_pos+steps
            
            if row_pos-steps < 0:
                lower_border = 0
            else:
                lower_border = row_pos-steps

            last_row = row_positions[image_index][row_pos]
            for i in range(row_pos+1, upper_border+1):
                if row_positions[image_index][i] not in critical_rows:
                    if row_positions[image_index][i] == last_row + 1:
                        close_to_high.append(image_arrays[image_index][i])
                        last_row = row_positions[image_index][i]
                    else:
                        break
                else:
                    break
            last_row = row_positions[image_index][row_pos]
            for i in range(row_pos-1, lower_border-1, -1):
                if row_positions[image_index][i] not in critical_rows:
                    if row_positions[image_index][i] == last_row - 1:
                        close_to_high.append(image_arrays[image_index][i])
                        last_row = row_positions[image_index][i]
                    else:
                        break
                else:
                    break
            
            close_to_high = np.array(close_to_high)
            mean_gray = np.mean(close_to_high, axis=0)
            mean_gray_std = np.std(close_to_high, axis=0)

            weird_factor = abs(max(diffusion_length_y[image_index])-min(diffusion_length_y[image_index]))/255

            diffusion_length.append(calc_diffusion_length(
                    mean_gray,
                    kwargs["pix_to_length"], 
                    kwargs["initial_values"]))
            diffusion_std.append(np.mean(mean_gray_std)*weird_factor)

            fixed_gray_exp_fit_params.append(calc_fit_params(
                    mean_gray,
                    kwargs["initial_values"]
            ))
            fixed_gray_image_positions.append(mean_gray)
        
        pickle_data_save = dict()
        pickle_data_save["voltage"] = picture_voltage_values
        pickle_data_save["diffusion_length"] = diffusion_length
        pickle_data_save["diffusion_std"] = diffusion_std
        pickle_data_save["voltage_unit"] = voltage_unit

        # this_name = pickle_name_volt[:len(pickle_name_volt)-4] + "_highest-fixed-gray.pkl"
        this_name = pickle_name_volt + "_highest-fixed-gray.pkl"
        with open(PICKLE_DIRECTORY_NAME + this_name, "wb") as fid:
            pickle.dump(pickle_data_save, fid)
        
        #exp fit
        this_name_exp = pickle_name_exp + "_highest-fixed-gray.pkl"

        del pickle_data_save
        pickle_data_save = dict()
        pickle_data_save["voltage"] = picture_voltage_values
        pickle_data_save["voltage_unit"] = voltage_unit
        pickle_data_save["fit_params"] = fixed_gray_exp_fit_params
        pickle_data_save["points"] = fixed_gray_image_positions
        pickle_data_save["point_position"] = row_positions

        with open(PICKLE_DIRECTORY_NAME + this_name_exp, "wb") as fid:
            pickle.dump(pickle_data_save, fid)


    if kwargs["volt_dep_method"] == "all":
        pa_plot.plot_multiple_diffusion_length_voltage_dependence(
            pickle_name=pickle_name_volt,
            save_as="L_U_all", 
            volt_unit=voltage_unit
        )

        pa_plot.plot_multiple_diffusion_length_voltage_dependence(
            pickle_name=pickle_name_volt,
            save_as="L_U_mean",
            filter="mean",
            volt_unit=voltage_unit
        )

        pa_plot.plot_multiple_diffusion_length_voltage_dependence(
            pickle_name=pickle_name_volt,
            save_as="L_U_highest_fix",
            filter="highest-fixed",
            volt_unit=voltage_unit
        )

        pa_plot.plot_multiple_diffusion_length_voltage_dependence(
            pickle_name=pickle_name_volt,
            save_as="L_U_highest_var",
            filter="highest-variable",
            volt_unit=voltage_unit
        )

        pa_plot.plot_multiple_diffusion_length_voltage_dependence(
            pickle_name=pickle_name_volt,
            save_as="L_U_gray",
            filter="gray",
            volt_unit=voltage_unit
        )

        pa_plot.plot_multiple_diffusion_length_voltage_dependence(
            pickle_name=pickle_name_volt,
            save_as="L_U_non_gray",
            filter="gray",
            app_others=True,
            volt_unit=voltage_unit
        )
    
        fi_file_directory = get_directorya(pickle_name_volt)
        fi_file_must_include = get_directorya(pickle_name_volt, ret_after=True)

        fi_files = os.listdir(PICKLE_DIRECTORY_NAME + fi_file_directory)
        fi_files = remove_other_filetypes(copy.deepcopy(fi_files), filetype="pkl")
        fi_files = search_fora(copy.deepcopy(fi_files), fi_file_must_include)

        for fi_file in fi_files:
            create_text_file(pickle_path=PICKLE_DIRECTORY_NAME + fi_file_directory + fi_file, save_path=Temp_TEXT_DIRECTORY_NAME + fi_file_directory + fi_file[:-4] + ".txt")

        this_name_exp = pickle_name_exp + "_mean.pkl"
        pa_plot.plot_exp(pickle_name=this_name_exp, save_as="Exp_fit_mean", volt_unit=voltage_unit, skip_volt=5)
        this_name_exp = pickle_name_exp + "_mean-gray.pkl"
        pa_plot.plot_exp(pickle_name=this_name_exp, save_as="Exp_fit_mean_gray", volt_unit=voltage_unit, skip_volt=5)
        this_name_exp = pickle_name_exp + "_highest-variable.pkl"
        pa_plot.plot_exp(pickle_name=this_name_exp, save_as="Exp_fit_highest_variable", volt_unit=voltage_unit, skip_volt=5)
        this_name_exp = pickle_name_exp + "_highest-variable-gray.pkl"
        pa_plot.plot_exp(pickle_name=this_name_exp, save_as="Exp_fit_highest_variable_gray", volt_unit=voltage_unit, skip_volt=5)
        this_name_exp = pickle_name_exp + "_highest-fixed.pkl"
        pa_plot.plot_exp(pickle_name=this_name_exp, save_as="Exp_fit_highest_fixed", volt_unit=voltage_unit, skip_volt=5)
        this_name_exp = pickle_name_exp + "_highest-fixed-gray.pkl"
        pa_plot.plot_exp(pickle_name=this_name_exp, save_as="Exp_fit_highest_fixed_gray", volt_unit=voltage_unit, skip_volt=5)

    else:
        pa_plot.plot_multiple_diffusion_length_voltage_dependence(
            pickle_name=pickle_name_volt,
            save_as="Diff_L_volt_dep",
            volt_unit=voltage_unit,
            remove_label=True
        )

        create_text_file(pickle_path=PICKLE_DIRECTORY_NAME + this_name, save_path = Temp_TEXT_DIRECTORY_NAME + this_name[:-4])
        
        pa_plot.plot_exp(pickle_name=this_name_exp, save_as="Exp_fit", volt_unit=voltage_unit)
    
    pa_plot.plot_defusion_length_row_dependence(
        pickle_name=pickle_name_y,
        voltage_distance=0,
        save_as="Diff_L_parallel_junction_all",
        volt_unit=voltage_unit,
        reduce_label=True
    )

    create_text_file(pickle_path=PICKLE_DIRECTORY_NAME + pickle_name_y, save_path=Temp_TEXT_DIRECTORY_NAME + pickle_name_y[:-4], volt_dep=False)

    pa_plot.plot_defusion_length_row_dependence(
        pickle_name=pickle_name_y,
        voltage_distance=1,
        save_as="Diff_L_parallel_junction_some",
        volt_unit=voltage_unit
    )