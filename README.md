# IsoPS-DIA-Window-designer
An interactive web application for designing isolation windows for mass spectrometry experiments. This tool allows users to upload MS data, visualize it, and interactively define isolation windows that can be exported for use in experimental setups.

![Isolation_window](https://github.com/user-attachments/assets/223f6fd9-77cb-4947-86c2-a95299b4fd7d)

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
About:
  This tool was developed as part of the research described in:
  [Chan et al. (2025). "IsoPS-DIA: An Dual Functional Approach for Absolute Oncoprotein Mutation Quantification and Proteome Profiling", Under revewing]

Features:
  1. Upload CSV data containing targeted precursors' MZ and RT values
  2. Interactive visualization of the distribution of targeted precursors' MZ
  3. Manual and automated creation of isolation windows
  4. Precision mode for fine-tuning window boundaries
  5. Export window definitions for direct use in MS experiments

Installation:
  Prerequisites
    Python 3.8 or higher

  Setup:
    Clone this repository: bashgit clone https://github.com/yourusername/IsoPS-Window-Designer.git 
    cd IsoPS-Window-Designer

  Create a virtual environment (recommended):
    bashpython -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

  Install required packages:
    bashpip install -r requirements.txt
  Usage:

Run the application:

  bashpython app.py

  Open your web browser and navigate to http://127.0.0.1:8050/
  Upload your MS data CSV file using the "Upload CSV" button. Your CSV should contain at minimum:

  MZ: m/z values
  RT: retention time values


  Optional columns that enhance functionality:
  
  Name: Compound identifiers
  Types: "Light" or other values (affects point opacity)
  Charge: Charge state information
  MZp1, MZp2: Additional m/z values for isotopes or fragments


  Create isolation windows by:
  
  Manually adding lines at specific m/z positions
  Using the "Auto-Fill" feature to automatically fill gaps
  Dragging lines to adjust their positions


  Use "Precise Line Drag Mode" for fine-tuning window boundaries
  Download your isolation windows as CSV with the "Download Lines" button

Example Data:
  Sample datasets are provided in the example_data/ folder to help you get started.
Contributing:
  Contributions to improve IsoPS Window Designer are welcome. Please feel free to submit pull requests or create issues for bugs and feature requests.
License:
  This project is licensed under the MIT License - see the LICENSE file for details.
Acknowledgments:
  List any funding sources or acknowledgments from your paper
  Any libraries or tools that were particularly helpful
