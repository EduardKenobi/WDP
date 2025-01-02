# My Python Project

This project is designed to visualize and analyze temperature and snow data using a graphical user interface (GUI). It provides functionalities to load, process, and display data in a user-friendly manner.

## Project Structure

```
my-python-project
├── src
│   ├── data_viewer.py                # Main functionality for displaying data in a GUI
│   ├── extremes_visualization_window.py # Contains the ExtremesVisualizationWindow class for displaying historical extremes
│   ├── main_window.py                # Main application window
│   ├── processing_inputs.py          # Functions for loading, repairing, processing data, and calculating statistics
│   ├── requirements.py               # Function to install required Python packages
│   ├── snow.py                       # Functions for calculating and analyzing snow data
│   ├── snow_data_viewer.py           # GUI for displaying snow data
│   └── tools.py                      # Helper functions for various calculations
├── requirements.txt                   # Lists required Python packages
└── README.md                          # Documentation for the project
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd my-python-project
   ```

2. Install the required packages:
   ```
   python src/requirements.py
   ```

## Usage

1. Run the application:
   ```
   python src/main_window.py <file_name> <station_id>
   ```
   Replace `<file_name>` with the path to your data file and `<station_id>` with the desired station ID.

2. The application will display the data in a table format, along with a visualization window for historical extremes.

## Requirements

The project requires the following Python packages:
- PyQt5
- pandas

These packages are listed in `requirements.txt` and can be installed using the provided `requirements.py` script.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.