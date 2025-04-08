import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from data_viewer import DataViewer
from extremes_visualization_window import ExtremesVisualizationWindow
from processing_inputs import load_data, process_data, calculate_historical_extremes
from tools import combine_statistics
from snow import calculate_snow_data, calculate_snow_extremes, create_snow_coverage_frequency_table
from snow_data_viewer import SnowDataViewer
from temp import create_yearly_temperature_summary
from snow_data_viewer_copy import SnowDataViewerCopy  # Import the copied SnowDataViewer

class MainWindow(QMainWindow):
    def __init__(self, file_name, station_id):
        super().__init__()
        self.station_id = station_id
        self.setWindowTitle("Weather Data Viewer")
        self.showMaximized()

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        data = load_data(file_name)
        self.data = data

        self.monthly_stats = process_data(station_id, data)
        self.update_snow_data_viewer("Zimne obdobie", self.data)

        temp_extremes, precip_extremes = calculate_historical_extremes(data)
        self.yearly_summary = create_yearly_temperature_summary(self.monthly_stats)
        self.extremes_viewer = ExtremesVisualizationWindow(temp_extremes, precip_extremes, self.yearly_summary)
        self.tab_widget.addTab(self.extremes_viewer, "Extremes Viewer")

        self.data_viewer = DataViewer(self.monthly_stats)
        self.tab_widget.addTab(self.data_viewer, "Data Viewer")

    def update_snow_data_viewer(self, season, data=None):
        if data is None:
            data = self.data
        snow_data = calculate_snow_data(data, self.monthly_stats, "CSP", 1, season)
        snow_extremes = calculate_snow_extremes(snow_data, data)
        csp_statistics = combine_statistics(self.monthly_stats, "CSP_max")
        csp_count_statistics = combine_statistics(self.monthly_stats, "CSP_count")
        create_snow_coverage_frequency_table(self.monthly_stats, "Letné obdobie")
        frequency_count_coverage, frequency_max_coverage = create_snow_coverage_frequency_table(self.monthly_stats, "Zimné obdobie")
        if hasattr(self, 'snow_data_viewer'):
            self.snow_data_viewer.update_data(snow_data, snow_extremes, csp_statistics, csp_count_statistics)
            self.snow_data_viewer_copy.update_data(snow_data, snow_extremes, csp_statistics, csp_count_statistics, frequency_count_coverage, frequency_max_coverage)
        else:
            self.snow_data_viewer = SnowDataViewer(snow_data, snow_extremes, csp_statistics, csp_count_statistics, self)
            self.snow_data_viewer_copy = SnowDataViewerCopy(snow_data, snow_extremes, csp_statistics, csp_count_statistics, frequency_count_coverage, frequency_max_coverage, self)
            self.tab_widget.addTab(self.snow_data_viewer, "Snow Data Viewer")
            self.tab_widget.addTab(self.snow_data_viewer_copy, "Snow Data Viewer Copy")



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
