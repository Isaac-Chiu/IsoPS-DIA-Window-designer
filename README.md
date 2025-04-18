# IsoPS-DIA-Window-designer
An interactive web application for designing isolation windows for mass spectrometry experiments. This tool allows users to upload MS data, visualize it, and interactively define isolation windows that can be exported for use in experimental setups.

![Isolation_window](https://github.com/user-attachments/assets/223f6fd9-77cb-4947-86c2-a95299b4fd7d)

## About:
  This tool was developed as part of the research described in:
  [Chan et al. (2025). "IsoPS-DIA: An Dual Functional Approach for Absolute Oncoprotein Mutation Quantification and Proteome Profiling", Under revewing]

## Features:
  1. Upload CSV data containing targeted precursors' MZ and RT values
  2. Interactive visualization of the distribution of targeted precursors' MZ
  3. Manual and automated creation of isolation windows
  4. Precision mode for fine-tuning window boundaries
  5. Export window definitions for direct use in MS experiments
  6. R program for preparing the data as the example files

## Installation:
### Prerequisites
    Python 3.8 or higher
## Setup:
1. Clone this repository:
  ``` bash
    git clone https://github.com/Isaac-Chiu/IsoPS-Window-Designer.git
    cd IsoPS-Window-Designer
  ```
2. Create a virtual environment (recommended):
  ``` bash
    bashpython -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
  ```
3. Install required packages:
  ``` bash
    pip install -r requirements.txt
  ```
## Usage:
1. Run the application:
  ``` bash
  python IsoPS_code_v1.16.py
  ```
2. Open your web browser and navigate to http://127.0.0.1:8050/
   
3. Upload your MS data CSV file using the "Upload CSV" button. Your CSV should contain at minimum: 
    * MZ: m/z values
    * RT: retention time values

4. Create isolation windows by:
    * Manually adding lines at specific m/z positions
    * Using the "Auto-Fill" feature to automatically fill gaps
    * Dragging lines to adjust their positions
    * Use "Precise Line Drag Mode" for fine-tuning window boundaries
    * Download your isolation windows as CSV with the "Download Lines" button
  
5. Program Interface

    ![image](https://github.com/user-attachments/assets/c14ff401-d0e1-4063-b2de-9a7006beb2a0)

    ![image](https://github.com/user-attachments/assets/88720fdb-60ee-405d-a80b-f9e56253051c)

    
6. The Data format of the CSV file:

    Provide skyline out put or your data in the following format:
    ![image](https://github.com/user-attachments/assets/02a7e99b-a45b-4fbe-a90e-2323f8f755df)
  
    Use Dataframe_preparation_1.01.R to prepare ready-to-use CSV file (or prepare it elsewhere):
    ![image](https://github.com/user-attachments/assets/5e88d356-eddd-41b8-8eb0-fdbece01f3c4)
  
  It will contain
  * Name: Compound identifiers
  * Types: "Light" or "Heavy" values (affects point opacity)
  * Charge: Charge state information (For calculate isotopes m/z)
  * MZp1, MZp2: Additional m/z values for isotopes
  * Predefine Isolation window (0.5 th before the target precursors)

## Example Data:
  Sample datasets are provided in the example_data/ folder to help you get started.
  
## Contributing:
  Contributions to improve IsoPS Window Designer are welcome. Please feel free to submit pull requests or create issues for bugs and feature requests.

## License:
  This project is licensed under the MIT License - see the LICENSE file for details.
  
  ![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
  
## Acknowledgments:
  List any funding sources or acknowledgments from your paper
  Any libraries or tools that were particularly helpful

## Contact
  Huan-Chi Chiu: isaac94028@gmail.com
