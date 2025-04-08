from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from constants import EVEN_ROW_COLOR, BLUE_COLOR, GREEN_COLOR, RED_COLOR

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
