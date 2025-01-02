"""
Tento súbor obsahuje pomocné funkcie, ktoré sú písané štýlom, že je ich možné použiť na akýkoľvek atribút a podmienku.

Funkcie:
- find_longest_series: Nájde najdlhšiu sériu atribútu, ktorý spĺňa podmienku.
- find_first_and_last_condition: Nájde prvý a posledný deň zo série atribútu s podmienkou.
- find_min_years: Nájde rok, v ktorom bol zaznamenaný najnižší maximálny atribút pre každý mesiac.
- find_max_years: Nájde rok, v ktorom bol zaznamenaný najvyšší maximálny atribút pre každý mesiac.
- find_avg_years: Nájde priemer maximálnych hodnôt atribútu a roky výskytov pre jednotlivé mesiace.
- combine_statistics: Spojí výsledky funkcií find_min_years, find_max_years a find_avg_years do jednej tabuľky.
- TableFormatter: Trieda na formátovanie tabuliek v PyQt5.
"""

from datetime import datetime
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem
from constants import EVEN_ROW_COLOR, BLUE_COLOR, GREEN_COLOR, RED_COLOR
    
    
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
    

def convert_to_unix_timestamp(date_str):
    try:
        date_format = "%d.%m.%Y"
        date = datetime.strptime(date_str, date_format)
        if date.month >= 10:
            date = date.replace(year=1975)
        elif date.month <= 5:
            date = date.replace(year=1976)
        return int(date.timestamp())
    except ValueError as e:
        print(f"Error parsing date '{date_str}': {e}")
        return 0

def convert_from_unix_timestamp(timestamp):
    date = datetime.fromtimestamp(timestamp)
    return date.strftime("%d.%m.")

# Výpočet najdlhšej série atributu, ktorý spĺňa podmienku
def find_longest_series(group, attribute, condition):
    group = group.sort_values("Datum")
    group["HasCondition"] = group[attribute] >= condition
    group["ConditionGroup"] = (group["HasCondition"] != group["HasCondition"].shift()).cumsum()
    condition_series = group[group["HasCondition"]].groupby("ConditionGroup")["Datum"]
    if not condition_series.size:  # Ak nie je séria, vrátime None hodnoty
        return 0, None, None
    longest_series = condition_series.apply(len).idxmax()  # Index najdlhšej série
    start_date = condition_series.get_group(longest_series).min().strftime("%d.%m.%Y")
    end_date = condition_series.get_group(longest_series).max().strftime("%d.%m.%Y")
    return len(condition_series.get_group(longest_series)), start_date, end_date

 # Výpočet prvého a posledného dňa zo ser atributu s podmienkou
def find_first_and_last_condition(group, attribute, condition):
    group_with_condition = group[group[attribute] >= condition]
    if group_with_condition.empty:  # Ak nie je podmienka splnená, vrátime None hodnoty
        return None, None
    first_date = group_with_condition["Datum"].min()
    last_date = group_with_condition["Datum"].max()
    return first_date, last_date


def find_min_years(monthly_stats, attribute):
    """
    Nájde rok, v ktorom bol zaznamenaný najnižší maximálny atribút pre každý mesiac.

    Args:
    monthly_stats (pd.DataFrame): Vstupné údaje, obsahujúce stĺpce s atribútmi.
    attribute (str): Názov atribútu, pre ktorý sa má nájsť minimum.

    Returns:
    pd.DataFrame: Tabuľka obsahujúca najnižší maximálny atribút a rok pre každý mesiac.
    """
    min_per_month = monthly_stats.loc[monthly_stats.groupby("Mesiac")[attribute].idxmin()].reset_index(drop=True)
    min_per_month = min_per_month.rename(columns={attribute: f"Najnižší {attribute}", "Rok": "Rok minima"})

    print(min_per_month)
    return min_per_month


def find_max_years(monthly_stats, attribute):
    """
    Nájde rok, v ktorom bol zaznamenaný najvyšší maximálny atribút pre každý mesiac.

    Args:
    monthly_stats (pd.DataFrame): Vstupné údaje, obsahujúce stĺpce s atribútmi.
    attribute (str): Názov atribútu, pre ktorý sa má nájsť maximum.

    Returns:
    pd.DataFrame: Tabuľka obsahujúca najvyšší maximálny atribút a rok pre každý mesiac.
    """
    max_per_month = monthly_stats.loc[monthly_stats.groupby("Mesiac")[attribute].idxmax()].reset_index(drop=True)
    max_per_month = max_per_month.rename(columns={attribute: f"Najvyšší {attribute}", "Rok": "Rok maxima"})

    print(max_per_month)
    return max_per_month


def find_avg_years(monthly_stats, attribute):
    """
    Nájde priemer maximálnych hodnôt atribútu a roky výskytov pre jednotlivé mesiace.

    Args:
    monthly_stats (pd.DataFrame): Vstupné údaje, obsahujúce stĺpce s atribútmi.
    attribute (str): Názov atribútu, pre ktorý sa má nájsť priemer.

    Returns:
    pd.DataFrame: Tabuľka obsahujúca priemerný maximálny atribút a roky výskytov pre každý mesiac.
    """
    avg_per_month = monthly_stats.groupby("Mesiac")[attribute].mean().reset_index()
    avg_per_month = avg_per_month.rename(columns={attribute: f"Priemerný {attribute}"})

    print(avg_per_month)
    return avg_per_month


def combine_statistics(monthly_stats, attribute):
    """
    Spojí výsledky funkcií find_min_years, find_max_years a find_avg_years do jednej tabuľky.

    Args:
    monthly_stats (pd.DataFrame): Vstupné údaje, obsahujúce stĺpce s atribútmi.
    attribute (str): Názov atribútu, pre ktorý sa majú nájsť štatistiky.

    Returns:
    pd.DataFrame: Tabuľka obsahujúca minimum, rok minima, priemer, maximum a rok maxima pre každý mesiac.
    """
    if attribute == "CSP_max" or attribute == "CSP_count":
        # Filtrovanie riadkov, kde atribút nie je nulový
        monthly_stats = monthly_stats[monthly_stats[attribute] != 0]

    min_stats = find_min_years(monthly_stats, attribute)
    max_stats = find_max_years(monthly_stats, attribute)
    avg_stats = find_avg_years(monthly_stats, attribute)

    combined = min_stats.merge(avg_stats, on="Mesiac").merge(max_stats, on="Mesiac")
    combined = combined.rename(columns={
    f"Najnižší {attribute}": "Minimum",
    "Rok minima": "Rok minima",
    f"Priemerný {attribute}": "Priemer",
    f"Najvyšší {attribute}": "Maximum",
    "Rok maxima": "Rok maxima"
    })

    combined = combined[["Mesiac", "Minimum", "Rok minima", "Priemer", "Maximum", "Rok maxima"]]

    combined["Minimum"] = combined["Minimum"].round().astype(int)
    combined["Maximum"] = combined["Maximum"].round().astype(int)
    combined["Priemer"] = combined["Priemer"].round().astype(int)

    # Zmena čísel mesiacov na názvy mesiacov
    month_names = {
    1: "Január", 2: "Február", 3: "Marec", 4: "Apríl", 5: "Máj", 6: "Jún",
    7: "Júl", 8: "August", 9: "September", 10: "Október", 11: "November", 12: "December"
    }
    combined["Mesiac"] = combined["Mesiac"].map(month_names)

    print(combined)
    return combined