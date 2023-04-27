# Alzheimer's Disease Classification Web App
## Introduction
This is a web application built with Python, Flask and MySQL where users can submit samples of their 3D MRI scan and get the diagnosis results.
The classification algorithm is based on the paper-
> De, Arijit, and Ananda S. Chowdhury. "DTI based Alzheimer’s disease classification with rank modulated fusion of CNNs and random forest." Expert Systems with Applications 169 (2021): 114338.

Direct link of the paper is [here](https://www.sciencedirect.com/science/article/abs/pii/S0957417420310265).

This app can only classify an MRI image among four classes - _Alzheimer's Disease (**AD**), Late Mild Cognitive Impairment (**LMCI**), Early Mild Cognitive Impairment (**EMCI**) and Normal (**N**)_.
This repository contains only the trained model. The code for training the model and the implementation of the above paper can be found [here](https://github.com/arijitde92/Alzheimer_Classification)

## Running instructions
1. Make sure you have all the necessary packages mentioned [here](requirements.txt) installed in your local machine.
2. `git clone` this repository to your local machine
3. Go inside the directory "AD_Classification_App"
4. Run command `python -m flask run`
5. Go to the URL provided in the terminal
6. Login or Register
7. After Login, submit an MRI image of the brain having file format "_.nii_". After submission, you will get the diagnosis.