from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QLabel, QComboBox, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import pandas as pd
from constants import LEFT_WIDTH, RIGHT_WIDTH, UPPER_LEFT_HEIGHT, LABEL_HEIGHT
from tools import TableFormatter, DateTableWidgetItem, NumericTableWidgetItem
    

class SnowDataViewer(QWidget):
    def __init__(self, snow_data, snow_extremes, csp_statistics, csp_count_statistics, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Snow Data Viewer")
        self.showMaximized()  # Add this line to start the window maximized

        # Initialize extremesComboBox before using it
        self.extremesComboBox = QComboBox()
        self.extremesComboBox.addItems(["Zimné obdobie", "Zima"])
        self.extremesComboBox.currentIndexChanged.connect(self.update_season)

        # Create a table for displaying snow data
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(len(snow_data))
        self.tableWidget.setColumnCount(len(snow_data.columns) + 1)
        self.tableWidget.setHorizontalHeaderLabels([
            "Zimné\nobdobie","Počet dní\nso SSP", "Max. snehová\npokrývka [cm]",
            "Najdlhšia séria\nso SSP", "Začiatok\nsérie", "Koniec\nsérie",
            "Prvý deň\nso SSP", "Posledný deň\nso SSP",
            "Počet dní\nvybraného obdobia", "Pomer dní\nso SSP [%]", "Pomer najdlhšej\nsérie [%]"
        ])
        self.tableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create a table for displaying snow_extremes
        self.extremesTableWidget = QTableWidget()
        self.extremesTableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create a table for displaying csp_statistics
        self.cspStatisticsTableWidget = QTableWidget()
        self.cspStatisticsTableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.cspStatisticsTableWidget.setHorizontalHeaderLabels([
            "Mesiac","Minimum", "Rok\nminima", "Priemer", "Maximum", "Rok\nmaxima"
        ])

        # Create a table for displaying csp_count_statistics
        self.cspCountStatisticsTableWidget = QTableWidget()
        self.cspCountStatisticsTableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.cspCountStatisticsTableWidget.setHorizontalHeaderLabels([
            "Mesiac","Minimum", "Rok\nminima", "Priemer", "Maximum", "Rok\nmaxima"
        ])

        # Create a label for the cspCountStatisticsTableWidget
        self.cspCountStatisticsLabel = QLabel("Mesačné štatistiky počtu dní so snehovou pokrývkou")
        self.cspCountStatisticsLabel.setFont(QFont("Arial", 14, QFont.Bold))
        self.cspCountStatisticsLabel.setAlignment(Qt.AlignCenter)

        # Create a label for the cspStatisticsTableWidget
        self.cspStatisticsLabel = QLabel("Mesačné štatistiky max. snehovej pokrývky")
        self.cspStatisticsLabel.setFont(QFont("Arial", 14, QFont.Bold))
        self.cspStatisticsLabel.setAlignment(Qt.AlignCenter)

        # Update the data based on the selection in the extremesComboBox
        self.update_data(snow_data, snow_extremes, csp_statistics, csp_count_statistics)

        # Setting the size of the widgets
        self.adjust_widget_size(self.cspCountStatisticsTableWidget, LEFT_WIDTH, UPPER_LEFT_HEIGHT)
        self.adjust_widget_size(self.cspStatisticsTableWidget, LEFT_WIDTH, UPPER_LEFT_HEIGHT)
        self.adjust_widget_size(self.extremesTableWidget, width=RIGHT_WIDTH)
        self.cspStatisticsLabel.setFixedHeight(LABEL_HEIGHT)
        self.cspCountStatisticsLabel.setFixedHeight(LABEL_HEIGHT)

        # Create a layout for the SnowDataViewer
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Create a left and right widget
        self.leftWidget = QWidget()
        self.leftLayout = QVBoxLayout()
        self.leftWidget.setLayout(self.leftLayout)

        self.upperLeftHorizontalLayout = QHBoxLayout()  # Create a horizontal layout for the upper left part

        # Create a layout for the labels above the tables
        self.labelsLayout = QHBoxLayout()
        self.labelsLayout.setContentsMargins(0, 0, 0, 0)
        self.labelsLayout.addWidget(self.cspCountStatisticsLabel)   # Add the table name above the csp_count_statistics table
        self.labelsLayout.addWidget(self.cspStatisticsLabel)    # Add the table name above the csp_statistics table
        self.leftLayout.addLayout(self.labelsLayout)    # Add the labels layout to the left layout
 
        self.upperLeftHorizontalLayout.addWidget(self.cspCountStatisticsTableWidget)    # Add the csp_count_statistics table to the upper left part
        self.upperLeftHorizontalLayout.addWidget(self.cspStatisticsTableWidget)     # Add the csp_statistics table to the upper left part
        self.leftLayout.addLayout(self.upperLeftHorizontalLayout)       # Add the upper left part to the left layout
        self.leftLayout.addWidget(self.tableWidget)     # Add the tableWidget to the left layout

        # Create a right widget
        self.rightWidget = QWidget()
        self.rightLayout = QVBoxLayout()
        self.rightWidget.setLayout(self.rightLayout)

        # Add the extremesComboBox and the extremesTableWidget to the right layout
        self.rightLayout.addWidget(self.extremesComboBox)
        self.rightLayout.addWidget(self.extremesTableWidget)

        # Add the left and right widgets to the main layout
        self.layout.addWidget(self.leftWidget)
        self.layout.addWidget(self.rightWidget)
        self.layout.setStretch(0, 1)  # Set stretch factor for left widget
        self.layout.setStretch(1, 1)  # Set stretch factor for right widget

        # Ensure the left and right layouts expand to fill the available space
        self.leftLayout.setStretch(0, 1)
        self.leftLayout.setStretch(1, 1)
        self.rightLayout.setStretch(0, 1)
        self.rightLayout.setStretch(1, 1)

        # Remove fixed width settings for left and right widgets
        self.leftWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.rightWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    # Update the data in the SnowDataViewer
    def update_data(self, snow_data, snow_extremes, csp_statistics, csp_count_statistics):
        # Save current sorting order
        sort_column = self.tableWidget.horizontalHeader().sortIndicatorSection()
        sort_order = self.tableWidget.horizontalHeader().sortIndicatorOrder()

        self.tableWidget.setSortingEnabled(False)
        self.extremesTableWidget.setSortingEnabled(False)
        self.cspStatisticsTableWidget.setSortingEnabled(False)
        self.cspCountStatisticsTableWidget.setSortingEnabled(False)

        self.tableWidget.setRowCount(len(snow_data) + 1)
        table_formatter = TableFormatter(self.tableWidget)

        # Clear existing items
        self.tableWidget.clearContents()
        self.extremesTableWidget.clearContents()
        self.cspStatisticsTableWidget.clearContents()
        self.cspCountStatisticsTableWidget.clearContents()

        # Reset headers
        self.tableWidget.setHorizontalHeaderLabels([
            "Zimné\nobdobie","Počet dní\nso SSP", "Max. snehová\npokrývka [cm]",
            "Najdlhšia séria\nso SSP", "Začiatok\nsérie", "Koniec\nsérie",
            "Prvý deň\nso SSP", "Posledný deň\nso SSP",
            "Počet dní\nvybraného obdobia", "Pomer dní\nso SSP [%]", "Pomer najdlhšej\nsérie [%]"
        ])
        self.extremesTableWidget.setColumnCount(3)
        self.extremesTableWidget.setHorizontalHeaderLabels(["Názov extrému", "Hodnota", "Obdobie"])
        self.cspStatisticsTableWidget.setColumnCount(6)
        self.cspStatisticsTableWidget.setHorizontalHeaderLabels([
            "Mesiac","Minimum", "Rok\nminima", "Priemer", "Maximum", "Rok\nmaxima"
        ])
        self.cspCountStatisticsTableWidget.setColumnCount(6)
        self.cspCountStatisticsTableWidget.setHorizontalHeaderLabels([
            "Mesiac","Minimum", "Rok\nminima", "Priemer", "Maximum", "Rok\nmaxima"
        ])

        # Reset sorting order
        self.tableWidget.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)

        # Iterate over the rows of snow_data
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

        # Resize columns and rows to fit the content
        self.extremesTableWidget.setRowCount(len(snow_extremes))
        table_formatter = TableFormatter(self.extremesTableWidget)

        # Iterate over the items in snow_extremes
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
            extremSession.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            extremSession.setFont(QFont("Arial", 8, QFont.Bold))
            self.extremesTableWidget.setItem(i, 2, extremSession)

        # Resize columns and rows to fit the content
        self.extremesTableWidget.resizeColumnsToContents()
        self.extremesTableWidget.setWordWrap(True)
        self.extremesTableWidget.resizeRowsToContents()

        # Resize columns and rows to fit the content
        self.cspStatisticsTableWidget.setRowCount(len(csp_statistics))
        table_formatter = TableFormatter(self.cspStatisticsTableWidget)

        # Iterate over the rows of csp_statistics
        for i, (index, row) in enumerate(csp_statistics.iterrows()):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                table_formatter.format_item(item, is_first_column=(j == 0), is_even_row=(i % 2 == 0))
                self.cspStatisticsTableWidget.setItem(i, j, item)

        # Resize columns and rows to fit the content
        self.cspCountStatisticsTableWidget.setRowCount(len(csp_count_statistics))
        table_formatter = TableFormatter(self.cspCountStatisticsTableWidget)

        # Iterate over the rows of csp_count_statistics
        for i, (index, row) in enumerate(csp_count_statistics.iterrows()):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                table_formatter.format_item(item, is_first_column=(j == 0), is_even_row=(i % 2 == 0))
                self.cspCountStatisticsTableWidget.setItem(i, j, item)

        self.tableWidget.setSortingEnabled(True)
        self.extremesTableWidget.setSortingEnabled(True)
        self.cspStatisticsTableWidget.setSortingEnabled(True)
        self.cspCountStatisticsTableWidget.setSortingEnabled(True)

        # Reapply saved sorting order
        self.tableWidget.sortItems(sort_column, sort_order)

    # Update the season in the SnowDataViewer
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
        # Call update_data to refresh the table with new data
        self.update_data(self.parent.snow_data, self.parent.snow_extremes, self.parent.csp_statistics, self.parent.csp_count_statistics)

    # Resize the widget to fit the content
    def adjust_widget_size(self, widget, width=None, height=None):
        # Resize the widget to fit the content
        if width is not None:
            widget.setFixedWidth(widget.horizontalHeader().length() + width)
        if height is not None:
            widget.setFixedHeight(widget.verticalHeader().length() + height)