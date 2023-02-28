#importing graphic packages and defining standard graphic settings
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

try:
    import bitsandbobs as bnb
    matplotlib.rcParams["axes.prop_cycle"] = matplotlib.cycler(
        "color",
        bnb.plt.get_default_colors()
    )
except:
    matplotlib.rcParams["axes.prop_cycle"] = matplotlib.cycler(
        "color",
        ['#233954', '#ea5e48', '#1e7d72', '#f49546', '#e8bf58', '#5886be', '#f3a093', '#53d8c9', '#f2da9c', '#f9c192']
    )

matplotlib.rcParams["axes.labelcolor"] = "black"
matplotlib.rcParams["axes.edgecolor"] = "black"
matplotlib.rcParams["xtick.color"] = "black"
matplotlib.rcParams["ytick.color"] = "black"
matplotlib.rcParams["xtick.labelsize"] = 6
matplotlib.rcParams["ytick.labelsize"] = 6
matplotlib.rcParams["xtick.major.pad"] = 2  # padding between text and the tick
matplotlib.rcParams["ytick.major.pad"] = 2  # default 3.5
matplotlib.rcParams["lines.dash_capstyle"] = "round"
matplotlib.rcParams["lines.solid_capstyle"] = "round"
matplotlib.rcParams["font.size"] = 6
matplotlib.rcParams["axes.titlesize"] = 6
matplotlib.rcParams["axes.labelsize"] = 6
matplotlib.rcParams["legend.fontsize"] = 6
matplotlib.rcParams["legend.facecolor"] = "#D4D4D4"
matplotlib.rcParams["legend.framealpha"] = 0.8
matplotlib.rcParams["legend.frameon"] = True
matplotlib.rcParams["axes.spines.right"] = False
matplotlib.rcParams["axes.spines.top"] = False
matplotlib.rcParams["figure.figsize"] = [3.4, 2.7]  # APS single column
matplotlib.rcParams["figure.dpi"] = 300
matplotlib.rcParams["savefig.facecolor"] = (0.0, 0.0, 0.0, 0.0)  # transparent figure bg
matplotlib.rcParams["axes.facecolor"] = (1.0, 0.0, 0.0, 0.0)

#importing other packages
import pickle
import random
import os
import copy
#from tkinter import *
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

#get data directory location
PICKLE_DIRECTORY_NAME = "Pickle_data/"
TEMP_PLOTS_DIRECTORY_NAME = "Temporary_Plots/"
Temp_TEXT_DIRECTORY_NAME = "Temporary_txt_Files/"

if not os.path.isdir(PICKLE_DIRECTORY_NAME):
    os.mkdir(PICKLE_DIRECTORY_NAME)
if not os.path.isdir(TEMP_PLOTS_DIRECTORY_NAME):
    os.mkdir(TEMP_PLOTS_DIRECTORY_NAME)
if not os.path.isdir(Temp_TEXT_DIRECTORY_NAME):
    os.mkdir(Temp_TEXT_DIRECTORY_NAME)


def function(x,L,n0,c):
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


def get_directory(string, ret_after = False):
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


def search_for(file_name_array, include, app_others = False):
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


def get_type(filename):
    """
    """
    for i in range(0, len(filename)):
        if filename[i] == "_":
            position_ = i
        if filename[i] == ".":
            position_dot = i
    return filename[position_+1:position_dot]


def sort_volt(volts, others):
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


#plotting functions

def plot_defusion_length_row_dependence(
    pickle_name = "Position_dependent/last_pd.pkl", 
    voltage_distance = 0, 
    plot_kind = "scatter",
    save_as = "", 
    volt_unit = "?",
    reduce_label = False,
    **kwargs
    ):
    """
    """
    #default settings
    kwargs.setdefault("title", "")
    kwargs.setdefault("x_label", "position parallel to pn junction")
    kwargs.setdefault("y_label", "diffusion length (in \u03BCm)")
    kwargs.setdefault("voltage_label", "voltage")
    kwargs.setdefault("markers", ["o"])
    kwargs.setdefault("figsize", [3.4, 2.7])
    kwargs.setdefault("linewidth", 1)
    kwargs.setdefault("s", 3)
    kwargs.setdefault("grid", True)

    kwargs["voltage_label"] += " (in " + volt_unit + ")"

    #retrieve data
    with open(PICKLE_DIRECTORY_NAME + pickle_name, "rb") as fid:
        pickle_data_loaded = pickle.load(fid)
    
    voltage = [pickle_data_loaded["voltage"][0]]
    diffusion_length_y = [pickle_data_loaded["diffusion_length_y"][0]]
    row_positions = [pickle_data_loaded["row_positions"][0]]

    #kwargs["voltage_label"] += " (in " + pickle_data_loaded["voltage_unit"] + ")"
    
    #sort input
    for i in range(0, len(pickle_data_loaded["voltage"])):
        appended = False
        for j in range(0, len(voltage)):
            if pickle_data_loaded["voltage"][i] < voltage[j]:
                voltage.insert(j, pickle_data_loaded["voltage"][i])
                diffusion_length_y.insert(j, pickle_data_loaded["diffusion_length_y"][i])
                row_positions.insert(j, pickle_data_loaded["row_positions"][i])
                appended = True
                break
        if not appended:
            voltage.append(pickle_data_loaded["voltage"][i])
            diffusion_length_y.append(pickle_data_loaded["diffusion_length_y"][i])
            row_positions.append(pickle_data_loaded["row_positions"][i])

    #transform data so that it is readable to seaborn
    data = dict()
    data[kwargs["y_label"]] = []
    data[kwargs["x_label"]] = []
    data[kwargs["voltage_label"]] = []
    data["size"] = []

    for i in range(0, len(voltage)):
        if i == 0:
            last = -5000
        if voltage[i] - last < voltage_distance:
            continue
        last = voltage[i]
        for j in range(0, len(diffusion_length_y[i])):
            data[kwargs["y_label"]].append(diffusion_length_y[i][j])
            data[kwargs["x_label"]].append(row_positions[i][j])
            data[kwargs["voltage_label"]].append(str(voltage[i]))
    
    #create plot
    fig, ax = plt.subplots(figsize=kwargs["figsize"])
    if reduce_label:
        if plot_kind == "line":
            norm = plt.Normalize(min(voltage), max(voltage))
            sm = plt.cm.ScalarMappable(cmap="RdBu", norm=norm)
            sm.set_array([])
            ax = sns.lineplot(data=data, x=kwargs["x_label"], y=kwargs["y_label"], hue=kwargs["voltage_label"], linewidth=kwargs["linewidth"])
            ax.get_legend().remove()
            ax.figure.colorbar(sm, label=kwargs["voltage_label"])
        elif plot_kind == "scatter":
            norm = plt.Normalize(min(voltage), max(voltage))
            sm = plt.cm.ScalarMappable(cmap="RdBu", norm=norm)
            sm.set_array([])
            ax = sns.scatterplot(data=data, x=kwargs["x_label"], y=kwargs["y_label"], hue=kwargs["voltage_label"], s=kwargs["s"], palette='RdBu')
            ax.get_legend().remove()
            ax.figure.colorbar(sm, label=kwargs["voltage_label"])
    else:
        if plot_kind == "line":
            ax = sns.lineplot(data=data, x=kwargs["x_label"], y=kwargs["y_label"], hue=kwargs["voltage_label"], linewidth=kwargs["linewidth"])
        elif plot_kind == "scatter":
            ax = sns.scatterplot(data=data, x=kwargs["x_label"], y=kwargs["y_label"], hue=kwargs["voltage_label"], s=kwargs["s"])
    ax.grid(kwargs["grid"])
    ax.set_title(kwargs["title"])
    #ax.legend(kwargs["label"], loc=kwargs["loc"])

    if len(save_as) > 0:
        plt.savefig(TEMP_PLOTS_DIRECTORY_NAME + save_as + ".png", facecolor="white")
        plt.close(fig)
    else:
        plt.show()


def plot_multiple_diffusion_length_voltage_dependence(
    pickle_name = "Voltage_dependent/last_vd", 
    filter = "", 
    app_others = False,
    save_as = "", 
    volt_unit = "?",
    remove_label = False,
    **kwargs
    ):
    """
    """
    #default settings
    kwargs.setdefault("title", "")
    kwargs.setdefault("x_label", "voltage")
    kwargs.setdefault("y_label", "diffusion length (in \u03BCm)")
    kwargs.setdefault("figsize", [3.4, 2.7])
    kwargs.setdefault("grid", False)
    kwargs.setdefault("linewidth", 2)
    kwargs.setdefault("linestyle", "--")
    kwargs.setdefault("marker", "o")
    kwargs.setdefault("markersize", 4)
    kwargs.setdefault("capsize", 2.5)
    kwargs.setdefault("capthick", None)
    kwargs.setdefault("ecolor", None)
    kwargs.setdefault("elinewidth", None)
    kwargs.setdefault("ylim", [0.47,1.3])
    kwargs.setdefault("loc", "best")

    kwargs["x_label"] += " (in " + volt_unit + ")"

    mpl_keywords = dict(
        linewidth=kwargs["linewidth"],
        linestyle=kwargs["linestyle"],
        marker=kwargs["marker"],
        markersize=kwargs["markersize"],
        capsize=kwargs["capsize"],
        capthick=kwargs["capthick"],
        ecolor=kwargs["ecolor"],
        elinewidth=kwargs["elinewidth"]
    )

    #retrieve data
    file_directory = get_directory(pickle_name)
    file_must_include = get_directory(pickle_name, ret_after=True)

    files = os.listdir(PICKLE_DIRECTORY_NAME + file_directory)
    files = remove_other_filetypes(copy.deepcopy(files), filetype="pkl")
    files = search_for(copy.deepcopy(files), file_must_include)
    if len(filter) > 0:
        files = search_for(copy.deepcopy(files), filter, app_others=app_others)

    #kwargs["x_label"] += " (in " + pickle_data_loaded["voltage_unit"] + ")"

    fig, ax = plt.subplots(figsize=kwargs["figsize"])

    for filename in files:
        with open(PICKLE_DIRECTORY_NAME + file_directory + filename, "rb") as fid:
            pickle_data_loaded = pickle.load(fid)
        
        desc = get_type(filename)
        
        try:
            this_volt, this_others = sort_volt(pickle_data_loaded["voltage"], [pickle_data_loaded["diffusion_length"], pickle_data_loaded["diffusion_std"]])
            this_diff_l = this_others[0]
            this_diff_std = this_others[1]
            ax.errorbar(this_volt, this_diff_l, this_diff_std, label=desc, **mpl_keywords)
        except:
            this_volt, this_others = sort_volt(pickle_data_loaded["voltage"], [pickle_data_loaded["diffusion_length"]])
            this_diff_l = this_others[0]
            ax.plot(this_volt, this_diff_l, label=desc)

    #create plot
    #ax.grid(kwargs["grid"])
    ax.set_title(kwargs["title"])
    ax.set_ylabel(kwargs["y_label"])
    ax.set_xlabel(kwargs["x_label"])
    ax.grid(kwargs["grid"])
    if not remove_label:
        ax.legend(loc=kwargs["loc"])

    if len(save_as) > 0:
        plt.savefig(TEMP_PLOTS_DIRECTORY_NAME + save_as + ".png", facecolor="white")
        plt.close(fig)
    else:
        plt.show()


def plot_exp(
    pickle_name = "Exponential_fit/last_ef_highest-fixed.pkl", 
    save_as = "", 
    volt_unit = "?",
    skip_volt = 1,
    **kwargs
    ):
    """
    """
    #default settings
    kwargs.setdefault("title", "")
    kwargs.setdefault("x_label", "position perpendicular to pn junction")
    kwargs.setdefault("y_label", "gray value")
    kwargs.setdefault("figsize", [3.4, 2.7])
    kwargs.setdefault("grid", False)
    kwargs.setdefault("linewidth", 1)
    kwargs.setdefault("linestyle", "-")
    kwargs.setdefault("marker", "o")
    kwargs.setdefault("s", 0.5)
    kwargs.setdefault("fit_label", "exponential fit")
    kwargs.setdefault("data_label", "measured datapoints")
    kwargs.setdefault("fit_color", '#ea5e48')
    kwargs.setdefault("reduce_by", 0.95)
    kwargs.setdefault("loc", "best")

    with open(PICKLE_DIRECTORY_NAME + pickle_name, "rb") as fid:
        pickle_data_loaded = pickle.load(fid)
    
    this_volt, this_others = sort_volt(pickle_data_loaded["voltage"], [pickle_data_loaded["fit_params"], pickle_data_loaded["points"], pickle_data_loaded["point_position"]])
    all_params = this_others[0]
    all_points = this_others[1]
    # this_volt = pickle_data_loaded["voltage"]
    # all_params = pickle_data_loaded["fit_params"]
    # all_points = pickle_data_loaded["points"]
    # pos = pickle_data_loaded["point_position"]

    last = 0
    for volt_value in range(0, len(this_volt)):
        if this_volt[volt_value] < last:
            continue
        else:
            last += skip_volt

        this_params = all_params[volt_value]
        this_points = all_points[volt_value]
        this_point_pos = np.arange(0, len(this_points), 1)

        new_points = []
        new_point_pos = []

        checkpoint = kwargs["reduce_by"]
        counter = 0
        bla = 0
        for i in range(0, len(this_points)):
            if this_points[i] < 3:
                if counter >= 1:
                    counter -= 1
                    bla += 1
                else:
                    new_points.append(this_points[i])
                    new_point_pos.append(this_point_pos[i])
                counter += checkpoint
            else:
                new_points.append(this_points[i])
                new_point_pos.append(this_point_pos[i])

        
        max_white = max(this_points)
        start = -1
        end = -1
        for i in range(0, len(this_points)):
            if start == -1:
                if this_points[i] > 0:
                    start = i
            if end == -1:
                if this_points[i] == max_white:
                    end = i
            
            if start != -1 and end != -1:
                break

        calc_at = np.arange(start, end, 1)
        fit = []
        for posi in calc_at:
            fit.append(function(posi, this_params[0], this_params[1], this_params[2]))
        
        for i in range(0, len(fit)):
            if fit[i] > max_white:
                calc_at = calc_at[:i]
                fit = fit[:i]
                break            
        
        fig, ax = plt.subplots(figsize=kwargs["figsize"])
        ax.scatter(new_point_pos, new_points, s=kwargs["s"], marker=kwargs["marker"], label=kwargs["data_label"], color='#233954')
        ax.plot(calc_at, fit, label=kwargs["fit_label"], color=kwargs["fit_color"], linewidth=kwargs["linewidth"], linestyle=kwargs["linestyle"])

        #create plot
        #ax.grid(kwargs["grid"])
        ax.set_title(kwargs["title"])
        ax.set_ylabel(kwargs["y_label"])
        ax.set_xlabel(kwargs["x_label"])
        ax.grid(kwargs["grid"])
        ax.legend(loc=kwargs["loc"])
        ax.text(0.15,0.7,"U = " + str(this_volt[volt_value]) + volt_unit, style='italic', bbox={'facecolor': 'gray', 'alpha': 0.15, 'pad': 3}, transform = ax.transAxes)

        if len(save_as) > 0:
            plt.savefig(TEMP_PLOTS_DIRECTORY_NAME + save_as + "_" + str(this_volt[volt_value]) + volt_unit + ".png", facecolor="white")
            plt.close(fig)
        else:
            plt.show()


#plot_defusion_length_row_dependence(voltage_distance=0)
#plot_diffusion_length_voltage_dependence()

#plot_multiple_diffusion_length_voltage_dependence(pickle_name="Diffusion_per_volt/please_work")
#plot_exp("Exp_fit/ef_last_pickle_highest-fixed-gray.pkl")

#plot_exp(pickle_name = "Exponential_fit/last_ef_mean.pkl")
#plot_defusion_length_row_dependence("Position_dependent/last_pd.pkl", reduce_label=True)
#plot_multiple_diffusion_length_voltage_dependence()