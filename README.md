# Program to evaluate diffusion length from EBIC images
If you happend to study physics (for master's degree) at the Martin Luther University you might stumble upon an experiment requiring you to take a couple of EBIC images at different voltages to show the dependency of diffusion length and voltage. 
To evaluate the diffusion length of one image takes a lot of time if you are doing it manually.
That's why we developed this program.
Take as many images as you want, the program will handle what's left.

Do not worry. You don't need to be good at python to operate this program as we implemented a user interface.
Download "picture_analysis" (folder must include pa.py, pa_plot.py and pa_interface.py) and store an additional folder inside containing the images. 
Afterwards run pa_interface.py. The program will tell you the next steps and explain all its components in english. 
If you are more comfortable with german look at the sixt chapter ("Automatisierung") of the file: "Protokoll.pdf". 
There you will be fully introduced and guided through the program. Hope it works, fingers crossed :D

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
