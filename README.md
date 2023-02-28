# MLU (university in germany) - Master physics - experiment M07 (REM/EBIC)
Program that helps to compute the diffusion length of many images taken with ebic.
Download "picture_analysis" (folder must include pa.py, pa_plot.py and pa_interface.py) and store an additional folder inside containing the images. Afterwards run pa_interface.py. The program will tell you the next steps. Hope it works :D

Example of required folder structure:
- picture_analysis (folder)
    - pa.py
    - pa_plot.py
    - pa_interface.py
    - images (folder with all the images)

If the program compiles successfully, it will create 4 additional folders:
- Pickle_data 
    (Calculated values stored in .pkl-files)
- Temporarily_Resized_Images 
    (This one has no use to you. 
    The images you took might need to be resized to display them correctly on the interface. 
    Those resized images will be stored here.)
- Temporary_Plots
    (Plots created from the calculated values.)
- Temporary_txt_Files
    (Calculated values stored in .txt-files)
