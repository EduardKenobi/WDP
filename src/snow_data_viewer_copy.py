from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QLabel, QComboBox, QSizePolicy, QGridLayout
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt
from datetime import datetime
import pandas as pd
from constants import EVEN_ROW_COLOR, BLUE_COLOR, GREEN_COLOR, RED_COLOR  # Use absolute import
from table_formatter import TableFormatter  # Import TableFormatter

class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        if isinstance(other, QTableWidgetItem):
            try:
                return float(self.text()) < float(other.text())
            except ValueError:
                return self.text() < other.text()
        return super().__lt__(other)

class DateTableWidgetItem(QTableWidgetItem):
    def __init__(self, text):
        super().__init__(text)
        self.original_text = text
        self.unix_timestamp = self.to_unix_timestamp(text)
        self.display_date = self.to_display_date(text)

    def to_unix_timestamp(self, text):
        try:
            date_format = "%d.%m.%Y"
            if len(text.split('.')) == 2:  # If the date string is missing the year
                text += '.1900'  # Add a default year to the date string
            date = datetime.strptime(text, date_format)
            if date.month >= 10:
                date = date.replace(year=1975)
            elif date.month <= 5:
                date = date.replace(year=1976)
            if date.year < 1970:
                return 0
            return int(date.timestamp())
        except ValueError as e:
            print(f"Error parsing date '{text}': {e}")
            return 0

    def to_display_date(self, text):
        try:
            date_format = "%d.%m.%Y"
            if len(text.split('.')) == 2:  # If the date string is missing the year
                text += '.1900'  # Add a default year to the date string
            date = datetime.strptime(text, date_format)
            return date.strftime("%d.%m.")
        except ValueError as e:
            print(f"Error parsing date '{text}': {e}")
            return text

    def __lt__(self, other):
        if isinstance(other, QTableWidgetItem):
            return self.unix_timestamp < other.unix_timestamp
        return super().__lt__(other)

    def data(self, role):
        if role == Qt.DisplayRole:
            return self.display_date  # Display date in DD.MM. format
        if role == Qt.UserRole:
            return self.unix_timestamp
        return super().data(role)
    

class SnowDataViewerCopy(QWidget):
    def __init__(self, snow_data, snow_extremes, csp_statistics, csp_count_statistics, frequency_count_coverage, frequency_max_coverage, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Snow Data Viewer Copy")
        self.showMaximized()
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.seasonComboBox = QComboBox()
        self.seasonComboBox.addItems(["Zimné obdobie", "Zima"])
        self.seasonComboBox.currentIndexChanged.connect(self.update_season)

        self.stationComboBox = QComboBox()
        self.atributeComboBox = QComboBox()

        # Vytvorenie vertikálneho layoutu
        menu_layout = QVBoxLayout()
        menu_layout.addWidget(self.seasonComboBox)
        menu_layout.addWidget(self.stationComboBox)
        menu_layout.addWidget(self.atributeComboBox)

        menu_widget = QWidget()
        menu_widget.setLayout(menu_layout)

        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(len(snow_data))
        self.tableWidget.setColumnCount(len(snow_data.columns) + 1)
        self.tableWidget.setHorizontalHeaderLabels([
            "Zimné\nobdobie","Počet dní\nso SSP", "Max. snehová\npokrývka [cm]",
            "Najdlhšia séria\nso SSP", "Začiatok\nsérie", "Koniec\nsérie",
            "Prvý deň\nso SSP", "Posledný deň\nso SSP",
            "Počet dní\nvybraného obdobia", "Pomer dní\nso SSP [%]", "Pomer najdlhšej\nsérie [%]"
        ])

        self.extremesTableWidget = QTableWidget()
        self.cspStatisticsTableWidget = QTableWidget()
        self.cspCountStatisticsTableWidget = QTableWidget()
        self.frequencyCountTableWidget = QTableWidget()
        self.frequencyMaxTableWidget = QTableWidget()

        table_layout = QVBoxLayout()
        table_layout.addWidget(self.frequencyCountTableWidget)
        table_layout.addWidget(self.frequencyMaxTableWidget)

        table_widget = QWidget()
        table_widget.setLayout(table_layout)

        self.update_data(snow_data, snow_extremes, csp_statistics, csp_count_statistics, frequency_count_coverage, frequency_max_coverage)

        self.cspCountStatisticsLabel = QLabel("Mesačné štatistiky počtu dní so snehovou pokrývkou")
        self.cspCountStatisticsLabel.setFont(QFont("Arial", 14, QFont.Bold))
        self.cspCountStatisticsLabel.setAlignment(Qt.AlignCenter)

        self.cspStatisticsLabel = QLabel("Mesačné štatistiky max. snehovej pokrývky")
        self.cspStatisticsLabel.setFont(QFont("Arial", 14, QFont.Bold))
        self.cspStatisticsLabel.setAlignment(Qt.AlignCenter)

        self.frequencyCountLabel = QLabel("Častosť výskytu snehovej pokrývky")
        self.frequencyCountLabel.setFont(QFont("Arial", 14, QFont.Bold))
        self.frequencyCountLabel.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(menu_widget, 0, 0)  # Nultý riadok, prvý stĺpec
        self.layout.addWidget(QWidget(), 0, 1)  # Nultý riadok, druhý stĺpec (prázdny)
        self.layout.addWidget(QWidget(), 0, 2)  # Nultý riadok, tretí stĺpec (prázdny)

        self.layout.addWidget(self.cspCountStatisticsLabel, 1, 0)  # Prvý riadok, nultý stĺpec
        self.layout.addWidget(self.cspStatisticsLabel, 1, 1)      # Prvý riadok, prvý stĺpec
        self.layout.addWidget(self.frequencyCountLabel, 1, 2)  # Prvý riadok, druhý stĺpec (prázdny)

        self.layout.addWidget(self.cspCountStatisticsTableWidget, 2, 0)  # Druhý riadok, nultý stĺpec
        self.layout.addWidget(self.cspStatisticsTableWidget, 2, 1)      # Druhý riadok, prvý stĺpec
        self.layout.addWidget(table_widget, 2, 2)  # Druhý riadok, druhý stĺpec (prázdny)

        self.layout.addWidget(self.tableWidget, 3, 0, 1, 2)  # Tretí riadok, nultý a prvý stĺpec (spojenie 2 stĺpcov)
        self.layout.addWidget(self.extremesTableWidget, 3, 2)  # Tretí riadok, druhý stĺpec

        self.layout.setColumnStretch(0, 0)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(0, 2)

        self.layout.setColumnStretch(1, 0)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(1, 2)

        self.layout.setColumnStretch(2, 0)
        self.layout.setColumnStretch(2, 1)
        self.layout.setColumnStretch(2, 2)

        self.layout.setRowStretch(2, 0)
        self.layout.setRowStretch(2, 1)
        self.layout.setRowStretch(2, 2)

        self.layout.setRowStretch(3, 0)
        self.layout.setRowStretch(3, 1)
        self.layout.setRowStretch(3, 2)

        self.tableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.extremesTableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.cspStatisticsTableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.cspCountStatisticsTableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frequencyCountTableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def update_data(self, snow_data, snow_extremes, csp_statistics, csp_count_statistics, frequency_count_coverage, frequency_max_coverage):

        self.frequencyCountTableWidget.setRowCount(len(frequency_count_coverage))
        self.frequencyCountTableWidget.setColumnCount(len(frequency_count_coverage.columns))
        self.frequencyCountTableWidget.setHorizontalHeaderLabels(frequency_count_coverage.columns)
        table_formatter = TableFormatter(self.frequencyCountTableWidget)

        for i, (index, row) in enumerate(frequency_count_coverage.iterrows()):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                table_formatter.format_item(item, is_first_column=(j == 0))
                self.frequencyCountTableWidget.setItem(i, j, item)

        self.frequencyMaxTableWidget.setRowCount(len(frequency_max_coverage))
        self.frequencyMaxTableWidget.setColumnCount(len(frequency_max_coverage.columns))
        self.frequencyMaxTableWidget.setHorizontalHeaderLabels(frequency_max_coverage.columns)
        table_formatter = TableFormatter(self.frequencyMaxTableWidget)

        for i, (index, row) in enumerate(frequency_max_coverage.iterrows()):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                table_formatter.format_item(item, is_first_column=(j == 0))
                self.frequencyMaxTableWidget.setItem(i, j, item)

        self.tableWidget.setRowCount(len(snow_data) + 1)
        table_formatter = TableFormatter(self.tableWidget)

        for i, (index, row) in enumerate(snow_data.iterrows(), start=1):
            item = QTableWidgetItem(str(index))
            table_formatter.format_item(item, is_first_column=True)
            self.tableWidget.setItem(i, 0, item)

            for j, value in enumerate(row, start=1):
                if j in [4, 5, 6, 7]:
                    item = DateTableWidgetItem(str(value))
                else:
                    item = NumericTableWidgetItem(str(value))
                table_formatter.format_item(item)
                self.tableWidget.setItem(i, j, item)

        self.extremesTableWidget.setRowCount(len(snow_extremes))
        self.extremesTableWidget.setColumnCount(3)
        self.extremesTableWidget.setHorizontalHeaderLabels(["Názov extrému", "Hodnota", "Obdobie"])
        table_formatter = TableFormatter(self.extremesTableWidget)

        for i, (key, value) in enumerate(snow_extremes.items()):
            item = QTableWidgetItem(key)
            table_formatter.format_item(item, is_first_column=True)
            self.extremesTableWidget.setItem(i, 0, item)

            extremValue = QTableWidgetItem(str(value["Hodnota"]))
            table_formatter.format_extreme_item(extremValue, i)
            self.extremesTableWidget.setItem(i, 1, extremValue)

            if value["Obdobie"] is not None:
                extremSession = QTableWidgetItem(value["Obdobie"].strftime("%d.%m.%Y") if isinstance(value["Obdobie"], pd.Timestamp) else str(value["Obdobie"]))
            else:
                extremSession = QTableWidgetItem("-")
            # table_formatter.format_extreme_item(extremSession, i)
            extremSession.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            extremSession.setFont(QFont("Arial", 8, QFont.Bold))
            self.extremesTableWidget.setItem(i, 2, extremSession)

        self.extremesTableWidget.resizeColumnsToContents()
        self.extremesTableWidget.setWordWrap(True)
        self.extremesTableWidget.resizeRowsToContents()

        self.cspStatisticsTableWidget.setRowCount(len(csp_statistics))
        self.cspStatisticsTableWidget.setColumnCount(len(csp_statistics.columns))
        self.cspStatisticsTableWidget.setHorizontalHeaderLabels(csp_statistics.columns)
        table_formatter = TableFormatter(self.cspStatisticsTableWidget)

        for i, (index, row) in enumerate(csp_statistics.iterrows()):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                table_formatter.format_item(item, is_first_column=(j == 0), is_even_row=(i % 2 == 0))
                self.cspStatisticsTableWidget.setItem(i, j, item)

        self.cspCountStatisticsTableWidget.setRowCount(len(csp_count_statistics))
        self.cspCountStatisticsTableWidget.setColumnCount(len(csp_count_statistics.columns))
        self.cspCountStatisticsTableWidget.setHorizontalHeaderLabels(csp_count_statistics.columns)
        table_formatter = TableFormatter(self.cspCountStatisticsTableWidget)

        for i, (index, row) in enumerate(csp_count_statistics.iterrows()):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                table_formatter.format_item(item, is_first_column=(j == 0), is_even_row=(i % 2 == 0))
                self.cspCountStatisticsTableWidget.setItem(i, j, item)

    def update_season(self, index):
        # Update the data based on the selection in the seasonComboBox
        season_extremes = self.seasonComboBox.currentText()
        self.parent.update_snow_data_viewer(season_extremes, self.parent.data)
        if self.seasonComboBox.currentText() == "Zima":
            season_extremes = "Zima"
        elif self.seasonComboBox.currentText() == "Zimné obdobie":
            season_extremes = "Zimné\nobdobie"
        else:
            season_extremes = "Zimné\nobdobie"
        self.tableWidget.horizontalHeaderItem(0).setText(season_extremes)
