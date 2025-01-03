import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from data_viewer import DataViewer
from extremes_visualization_window import ExtremesVisualizationWindow
from processing_inputs import load_data, process_data, calculate_historical_extremes
from tools import combine_statistics
from snow import calculate_snow_data, calculate_snow_extremes
from snow_data_viewer import SnowDataViewer

class MainWindow(QMainWindow):
    def __init__(self, file_name, station_id):
        super().__init__()
        self.station_id = station_id
        self.setWindowTitle("Weather Data Parse")
        self.showMaximized()

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        data = load_data(file_name)
        self.data = data

        self.monthly_stats = process_data(station_id, data)
        self.update_snow_data_viewer("Zimne obdobie", self.data)

        temp_extremes, precip_extremes = calculate_historical_extremes(data)
        self.extremes_viewer = ExtremesVisualizationWindow(temp_extremes, precip_extremes)
        self.tab_widget.addTab(self.extremes_viewer, "Extremes Viewer")

        self.data_viewer = DataViewer(self.monthly_stats)
        self.tab_widget.addTab(self.data_viewer, "Data Viewer")

    def update_snow_data_viewer(self, season, data=None):
        if data is None:
            data = self.data
        self.snow_data = calculate_snow_data(data, self.monthly_stats, "CSP", 1, season)
        self.snow_extremes = calculate_snow_extremes(self.snow_data, data)
        self.csp_statistics = combine_statistics(self.monthly_stats, "CSP_max")
        self.csp_count_statistics = combine_statistics(self.monthly_stats, "CSP_count")
        if hasattr(self, 'snow_data_viewer'):
            self.snow_data_viewer.update_data(self.snow_data, self.snow_extremes, self.csp_statistics, self.csp_count_statistics)
        else:
            self.snow_data_viewer = SnowDataViewer(self.snow_data, self.snow_extremes, self.csp_statistics, self.csp_count_statistics, self)
            self.tab_widget.addTab(self.snow_data_viewer, "Snow Data Viewer")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if len(sys.argv) != 3:
        print("Usage: python main_window.py <file_name> <station_id>")
        sys.exit(1)
    
    file_name = sys.argv[1]
    station_id = sys.argv[2]

    main_window = MainWindow(file_name, station_id)
    main_window.show()
    sys.exit(app.exec_())
