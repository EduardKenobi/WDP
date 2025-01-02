from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QLabel, QComboBox, QSizePolicy
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt
from datetime import datetime
import pandas as pd
from constants import EVEN_ROW_COLOR, BLUE_COLOR, GREEN_COLOR, RED_COLOR  # Use absolute import

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

class TableFormatter:
    def __init__(self, table_widget):
        self.table_widget = table_widget
        self.header_font = QFont("Arial", 10, QFont.Bold)
        self.data_font = QFont("Arial", 8)
        self.first_column_font = QFont("Arial", 10, QFont.Bold)
        self.setup_table()

    def setup_table(self):
        header = self.table_widget.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        header.setFont(self.header_font)
        header.setFixedHeight(50)
        for col in range(self.table_widget.columnCount()):
            item = self.table_widget.horizontalHeaderItem(col)
            item.setFont(self.header_font)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            item.setToolTip(item.text())
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        self.table_widget.setWordWrap(True)
        self.table_widget.resizeRowsToContents()
        self.table_widget.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        self.table_widget.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        self.table_widget.setSortingEnabled(True)

    def format_item(self, item, is_first_column=False, is_even_row=False):
        if is_first_column:
            item.setFont(self.first_column_font)
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        else:
            item.setFont(self.data_font)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        if is_even_row:
            item.setBackground(EVEN_ROW_COLOR)
        return item

    def format_extreme_item(self, item, row_index):
        if row_index % 3 == 0:
            item.setBackground(RED_COLOR)
        elif row_index % 3 == 1:
            item.setBackground(GREEN_COLOR)
        else:
            item.setBackground(BLUE_COLOR)
        item.setForeground(QColor(Qt.white))
        item.setFont(QFont("Arial", 8, QFont.Bold))
        item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        return item

class SnowDataViewer(QWidget):
    def __init__(self, snow_data, snow_extremes, csp_statistics, csp_count_statistics, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Snow Data Viewer")
        self.showMaximized()  # Add this line to start the window maximized
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Initialize extremesComboBox before using it
        self.extremesComboBox = QComboBox()
        self.extremesComboBox.addItems(["Zimné obdobie", "Zima"])
        self.extremesComboBox.currentIndexChanged.connect(self.update_season)

        # Vytvorenie tabuľky pre snow_data
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(len(snow_data))  # Počet riadkov = počet záznamov
        self.tableWidget.setColumnCount(len(snow_data.columns) + 1)  # +1 pre "Zimne obdobie"
        self.tableWidget.setHorizontalHeaderLabels([
            "Zimné\nobdobie","Počet dní\nso SSP", "Max. snehová\npokrývka [cm]",
            "Najdlhšia séria\nso SSP", "Začiatok\nsérie", "Koniec\nsérie",
            "Prvý deň\nso SSP", "Posledný deň\nso SSP",
            "Počet dní\nvybraného obdobia", "Pomer dní\nso SSP [%]", "Pomer najdlhšej\nsérie [%]"
        ])

        self.extremesTableWidget = QTableWidget()
        self.cspStatisticsTableWidget = QTableWidget()
        self.cspCountStatisticsTableWidget = QTableWidget()

        self.update_data(snow_data, snow_extremes, csp_statistics, csp_count_statistics)

        # Vytvorenie vertikálneho rozloženia pre ľavú časť
        self.leftWidget = QWidget()
        self.leftLayout = QVBoxLayout()
        self.leftWidget.setLayout(self.leftLayout)

        # Vytvorenie horizontálneho rozloženia pre hornú časť ľavej časti
        self.upperLeftHorizontalLayout = QHBoxLayout()

        # Vytvorenie layoutu pre labely nad tabuľkami
        self.labelsLayout = QHBoxLayout()
        self.labelsLayout.setContentsMargins(0, 0, 0, 0)

        # Pridanie názvu tabuľky nad tabuľku csp_count_statistics
        self.cspCountStatisticsLabel = QLabel("Mesačné štatistiky počtu dní so snehovou pokrývkou")
        self.cspCountStatisticsLabel.setFont(QFont("Arial", 14, QFont.Bold))
        self.cspCountStatisticsLabel.setAlignment(Qt.AlignCenter)
        self.labelsLayout.addWidget(self.cspCountStatisticsLabel)

        # Pridanie názvu tabuľky nad tabuľku csp_statistics
        self.cspStatisticsLabel = QLabel("Mesačné štatistiky max. snehovej pokrývky")
        self.cspStatisticsLabel.setFont(QFont("Arial", 14, QFont.Bold))
        self.cspStatisticsLabel.setAlignment(Qt.AlignCenter)
        self.labelsLayout.addWidget(self.cspStatisticsLabel)

        # Pridanie layoutu pre labely do hornej časti
        self.leftLayout.addLayout(self.labelsLayout)
        label_height = 30
        self.cspStatisticsLabel.setFixedHeight(label_height)
        self.cspCountStatisticsLabel.setFixedHeight(label_height)

        # Pridanie tabuľky csp_count_statistics do hornej časti
        self.upperLeftHorizontalLayout.addWidget(self.cspCountStatisticsTableWidget)

        # Pridanie tabuľky csp_statistics do hornej časti
        self.upperLeftHorizontalLayout.addWidget(self.cspStatisticsTableWidget)

        # Pridanie hornej časti do ľavej časti
        self.leftLayout.addLayout(self.upperLeftHorizontalLayout)

        # Pridanie tabuľky snow_data pod hornú časť
        self.leftLayout.addWidget(self.tableWidget)

        # Vytvorenie vertikálneho rozloženia pre pravú časť
        self.rightWidget = QWidget()
        self.rightLayout = QVBoxLayout()
        self.rightWidget.setLayout(self.rightLayout)

        # Pridanie rozklikávacieho zoznamu nad tabuľku snow_extremes
        self.rightLayout.addWidget(self.extremesComboBox)

        self.rightLayout.addWidget(self.extremesTableWidget)

        # Pridanie ľavej a pravej časti do hlavného rozloženia
        self.layout.addWidget(self.leftWidget)
        self.layout.addWidget(self.rightWidget)
        self.layout.setStretch(0, 1)  # Set stretch factor for left widget
        self.layout.setStretch(1, 1)  # Set stretch factor for right widget

        # Ensure the tables expand to fill the available space
        self.tableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.extremesTableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.cspStatisticsTableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.cspCountStatisticsTableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Ensure the left and right layouts expand to fill the available space
        self.leftLayout.setStretch(0, 1)
        self.leftLayout.setStretch(1, 1)
        self.rightLayout.setStretch(0, 1)
        self.rightLayout.setStretch(1, 1)

        # Set fixed width for right widget based on the width of the extremesTableWidget
        right_width = self.extremesTableWidget.horizontalHeader().length()
        self.extremesTableWidget.setFixedWidth(right_width+30)

        left_width = self.cspStatisticsTableWidget.horizontalHeader().length()
        self.cspStatisticsTableWidget.setFixedWidth(left_width+140)
        left_width = self.cspCountStatisticsTableWidget.horizontalHeader().length()
        self.cspCountStatisticsTableWidget.setFixedWidth(left_width+140)

        upper_left_height = self.cspStatisticsTableWidget.verticalHeader().length()
        self.cspStatisticsTableWidget.setFixedHeight(upper_left_height+52)
        upper_left_height = self.cspCountStatisticsTableWidget.verticalHeader().length()
        self.cspCountStatisticsTableWidget.setFixedHeight(upper_left_height+52)

        # Remove fixed width settings for left and right widgets
        self.leftWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.rightWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def update_data(self, snow_data, snow_extremes, csp_statistics, csp_count_statistics):
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
        # Update the data based on the selection in the extremesComboBox
        season_extremes = self.extremesComboBox.currentText()
        self.parent.update_snow_data_viewer(season_extremes, self.parent.data)
        if self.extremesComboBox.currentText() == "Zima":
            season_extremes = "Zima"
        elif self.extremesComboBox.currentText() == "Zimné obdobie":
            season_extremes = "Zimné\nobdobie"
        else:
            season_extremes = "Zimné\nobdobie"
        self.tableWidget.horizontalHeaderItem(0).setText(season_extremes)