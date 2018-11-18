# cg3002_project
This project repository is the repository for CG3002 Group 14

## Communication Component
This package contains all the C++ files run on the Arduino Mega and Python scripts run on the Raspberry Pi. The Python interfaces used to interface with the prediction models are also included, as are noteworthy model versions.

- `arduino.cpp`: the C++ program run on the Arduino Mega
- `client.py`: the final script run on the Raspberry Pi
- `local_client.py`: testing script that does not perform TCP communication with the server
- `dataScript.py`: script used for collecting sensor readings and writing it to a CSV file for model training
- `prediction_model`: contains scripts necessary for the client to interface with the model. Model used can be changed in `prediction_interface.py`
- `lib`: contains all the library files used in the C++ program on Arduino Mega

## Prediction Component

## Sensor Component
