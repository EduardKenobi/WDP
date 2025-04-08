from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from table_formatter import TableFormatter  # Import TableFormatter

class ExtremesVisualizationWindow(QWidget):
    def __init__(self, temp_extremes, precip_extremes, yearly_summary):
        super().__init__()
        self.setWindowTitle("Historické extrémy")
        self.showMaximized()  # Add this line to start the window maximized
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Tabuľka pre teplotné extrémy
        temp_table = QTableWidget()
        temp_table.setRowCount(2)
        temp_table.setColumnCount(2)
        temp_table.setHorizontalHeaderLabels(["Hodnota", "Dátum"])
        temp_table.setVerticalHeaderLabels(["Tmax", "Tmin"])
        temp_table.setItem(0, 0, QTableWidgetItem(str(temp_extremes["Tmax"]["Hodnota"])))
        temp_table.setItem(0, 1, QTableWidgetItem(temp_extremes["Tmax"]["Datum"]))
        temp_table.setItem(1, 0, QTableWidgetItem(str(temp_extremes["Tmin"]["Hodnota"])))
        temp_table.setItem(1, 1, QTableWidgetItem(temp_extremes["Tmin"]["Datum"]))
        self.layout.addWidget(temp_table)

        # Tabuľka pre zrážkové a snehové extrémy
        precip_table = QTableWidget()
        precip_table.setRowCount(2)
        precip_table.setColumnCount(2)
        precip_table.setHorizontalHeaderLabels(["Hodnota", "Dátum"])
        precip_table.setVerticalHeaderLabels(["R", "CSP"])
        precip_table.setItem(0, 0, QTableWidgetItem(str(precip_extremes["R"]["Hodnota"])))
        precip_table.setItem(0, 1, QTableWidgetItem(precip_extremes["R"]["Datum"]))
        precip_table.setItem(1, 0, QTableWidgetItem(str(precip_extremes["CSP"]["Hodnota"])))
        precip_table.setItem(1, 1, QTableWidgetItem(precip_extremes["CSP"]["Datum"]))
        self.layout.addWidget(precip_table)

        # Tabuľka pre ročnú teplotnú sumarizáciu
        yearly_table = QTableWidget()
        yearly_table.setRowCount(len(yearly_summary))
        yearly_table.setColumnCount(len(yearly_summary.columns))
        yearly_table.setHorizontalHeaderLabels(yearly_summary.columns)
        table_formatter = TableFormatter(yearly_table)
        for i, row in yearly_summary.iterrows():
            for j, col in enumerate(yearly_summary.columns):
                item_value = int(row[col]) if col == "Rok" else row[col]
                item = QTableWidgetItem(str(item_value))
                table_formatter.format_item(item, is_first_column=(j == 0), is_even_row=(i % 2 == 0))
                yearly_table.setItem(i, j, item)
        self.layout.addWidget(yearly_table)
