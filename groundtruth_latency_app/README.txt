This folder contains everything you need to run the MEP latency ground truth app.
The important files are:
1. df_all_meps.pkl which containes sample MEP trials
2. df_latencies.csv is an empty csv file where you can save your results (NB: you can save any other file when needed and through the app)
3. latency_gt.exe is the app executable (windows only) which you have to double-click to start
4. latency_gt.py is the respective python file of the app. You may run the app also by writing on your terminal python latency_gt.py. This should work in all OS, check requirements.txt

Other files and folders are:
1. latency_gt_gui.ui is the file where the layout of the app is saved
3. build are folders automatically created when you make an executable out of your python file (do not touch)
4. pycache

HOW TO RUN THE APP:
Double click latency_gt.exe (or python-wise, see above). This might take several seconds. Once the app window appears, you will see some instructions written in the "Output".
The first thing you need to do is to load the file with all the MEPs for which you need to define the latency (i.e. beggining of MEP, when the signal starts to deflect (up or down). To do this, press the "Load remaining MEPs". If this is not the first time you have worked on the app, you also need to load the results you have saved already by presing "Load saved latencies".
Now you can start defining the latency for each new MEP (see instructions in the app). If you want to stop, first save your progress by updating the dataframes of both MEP already looked at and actual latency results by pressing the "update dataframe" button. IMPORTANT: first you will be asked to save the latency dataframe (.csv file); secondly the dataframe with remaining MEPs). For safety reasons, you will be asked again to save your data once you close the app; you can just save on top of previously saved files. You can save the MEP file on the initial one that was given in this folder and overwrite it.