from PyQt5.QtGui import QColor

# Color shades
EVEN_ROW_COLOR = QColor(204, 204, 255)

# Additional colors
BLUE_COLOR = QColor(31, 73, 125)  # #1F497D
GREEN_COLOR = QColor(118, 147, 60)  # #76933C
RED_COLOR = QColor(192, 0, 0)  # #C00000

WHOLE_YEAR = {
    1: "Január", 2: "Február", 3: "Marec",
    4: "Apríl", 5: "Máj", 6: "Jún",
    7: "Júl", 8: "August", 9: "September",
    10: "Október", 11: "November", 12: "December"
}
YEAR = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
AUTUMN = [9, 10, 11]
WINTER = [12, 1, 2]
SPRING = [3, 4, 5]
SUMMER = [6, 7, 8]
WINTER_SEASON = [10, 11, 12, 1, 2, 3, 4, 5]
SUMMER_SEASON = [3, 4, 5, 6, 7, 8, 9, 10, 11]
WARM_HALF_YEAR = [4, 5, 6, 7, 8, 9]
COLD_HALF_YEAR = [10, 11, 12, 1, 2, 3]

SEASONS = {
    "Celý rok": YEAR,
    "Jeseň": AUTUMN,
    "Zima": WINTER,
    "Jar": SPRING,
    "Leto": SUMMER,
    "Zimné obdobie": WINTER_SEASON,
    "Letné obdobie": SUMMER_SEASON,
    "Teplá polovica roka": WARM_HALF_YEAR,
    "Chladná polovica roka": COLD_HALF_YEAR
}
# ...other constants can be added here in the future...
