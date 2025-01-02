import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem

class DataViewer(QWidget):
    def __init__(self, monthly_stats):
        super().__init__()
        self.monthly_stats = monthly_stats
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Data Viewer")
        self.showMaximized()  # Add this line to start the window maximized
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Vytvorenie tabuľky
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(len(self.monthly_stats))
        self.tableWidget.setColumnCount(len(self.monthly_stats.columns))
        self.tableWidget.setHorizontalHeaderLabels(self.monthly_stats.columns)

        # Iterácia cez riadky monthly_stats (Pandas DataFrame)
        for i, row in self.monthly_stats.iterrows():
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.tableWidget.setItem(i, j, item)

        self.layout.addWidget(self.tableWidget)
