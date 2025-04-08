"""
Tento súbor obsahuje funkcie na výpočet a analýzu údajov o snehu.

Funkcie:
- calculate_snow_data: Vypočíta základné štatistiky o snehu pre dané obdobie a atribút.
- calculate_snow_extremes: Nájde extrémne hodnoty snehu pre dané obdobie a atribút.
"""

import pandas as pd
from tools import convert_from_unix_timestamp, convert_to_unix_timestamp, find_longest_series, find_first_and_last_condition
from constants import SEASONS, WHOLE_YEAR

def calculate_snow_data(data, monthly_stats, attribute, condition, season):
    # Zabezpečenie, že 'Datum' je datetime
    data["Datum"] = pd.to_datetime(data["Datum"], format='%d.%m.%Y', errors="coerce")

    # Skontrolovať, či nedošlo k chybám pri konverzii
    if data["Datum"].isnull().any():
        raise ValueError("Stĺpec 'Datum' obsahuje neplatné hodnoty, ktoré sa nedajú konvertovať na dátum.")

    if season == "Zima":
        # Filtrovanie dát na zimné mesiace (december, január, február)
        filtered_data = data[(data["Datum"].dt.month >= 12) | (data["Datum"].dt.month <= 2)].copy()
        filtered_data["Zimne obdobie"] = filtered_data.apply(
            lambda row: f"{row['Datum'].year}/{row['Datum'].year + 1}"
            if row["Datum"].month >= 12
            else f"{row['Datum'].year - 1}/{row['Datum'].year}",
            axis=1
        )
    else:
        # Filtrovanie dát na zimné obdobia (október - máj)
        filtered_data = data[(data["Datum"].dt.month >= 10) | (data["Datum"].dt.month <= 5)].copy()
        filtered_data["Zimne obdobie"] = filtered_data.apply(
            lambda row: f"{row['Datum'].year}/{row['Datum'].year + 1}"
            if row["Datum"].month >= 10
            else f"{row['Datum'].year - 1}/{row['Datum'].year}",
            axis=1
        )

    # Výpočet základných štatistík o snehu
    snow_data = (
        filtered_data.groupby("Zimne obdobie")[attribute]
        .agg(["count", "max"])
        .rename(columns={"count": "Pocet dni so snehom", "max": "Max snehova pokryvka"})
    )
    # Odstránenie prvého zimného obdobia 1950/1951
    snow_data = snow_data[snow_data.index != "1950/1951"]
    snow_data["Max snehova pokryvka"] = snow_data["Max snehova pokryvka"].round().astype(int)

    series_data = (
        filtered_data.groupby("Zimne obdobie")
        .apply(lambda g: find_longest_series(g, attribute, condition))
        .apply(pd.Series)
        .rename(columns={0: "Najdlhsia seria (dni)", 1: "Zaciatok serie", 2: "Koniec serie"})
    )

    first_last_condition_data = (
        filtered_data.groupby("Zimne obdobie")
        .apply(lambda g: find_first_and_last_condition(g, attribute, condition))
        .apply(pd.Series)
        .rename(columns={0: "Prvy den s podmienkou", 1: "Posledny den s podmienkou"})
    )

    # Výpočet celkového počtu dní, a pomerov
    def calculate_ratios(row):
        if pd.isnull(row["Prvy den s podmienkou"]) or pd.isnull(row["Posledny den s podmienkou"]):
            return pd.Series([None, None, None], index=["Celkovy pocet dni", "Ratio dni s podmienkou", "Ratio najdlhsej serie"])
        total_days = (row["Posledny den s podmienkou"] - row["Prvy den s podmienkou"]).days + 1
        ratio_condition_days = (row["Pocet dni so snehom"] / total_days) * 100
        ratio_longest_series = (row["Najdlhsia seria (dni)"] / total_days) * 100
        return pd.Series([total_days, ratio_condition_days, ratio_longest_series], index=["Celkovy pocet dni", "Ratio dni s podmienkou", "Ratio najdlhsej serie"])

    snow_data_with_dates = snow_data.join(series_data).join(first_last_condition_data)
    ratio_data = snow_data_with_dates.apply(calculate_ratios, axis=1)

    ratio_data["Celkovy pocet dni"] = ratio_data["Celkovy pocet dni"].round().astype(int)
    ratio_data["Ratio dni s podmienkou"] = ratio_data["Ratio dni s podmienkou"].round(2)
    ratio_data["Ratio najdlhsej serie"] = ratio_data["Ratio najdlhsej serie"].round(2)

    snow_data_with_ratios = snow_data_with_dates.join(ratio_data)

    # Formátovanie dátumov
    snow_data_with_ratios["Prvy den s podmienkou"] = snow_data_with_ratios["Prvy den s podmienkou"].dt.strftime("%d.%m.%Y")
    snow_data_with_ratios["Posledny den s podmienkou"] = snow_data_with_ratios["Posledny den s podmienkou"].dt.strftime("%d.%m.%Y")

    print(snow_data_with_ratios)

    return snow_data_with_ratios


def calculate_snow_extremes(snow_data, data):

    snow_extremes = {
        "Najneskorší výskyt prvej SSP": {"Hodnota": None, "Obdobie": None},
        "Priemerný dátum výskytu prvej SSP": {"Hodnota": None, "Obdobie": None},
        "Najskorší výskyt prvej SSP": {"Hodnota": None, "Obdobie": None},
        "Najneskorší výskyt poslednej SSP": {"Hodnota": None, "Obdobie": None},
        "Priemerný dátum výskytu poslednej SSP": {"Hodnota": None, "Obdobie": None},
        "Najskorší výskyt poslednej SSP": {"Hodnota": None, "Obdobie": None},
        "Najdlhšia séria so SSP": {"Hodnota": None, "Obdobie": None},
        "Priemer najdlhších sérií so SSP": {"Hodnota": None, "Obdobie": None},
        "Najkratšia séria so SSP": {"Hodnota": None, "Obdobie": None},
        "Najvyšší počet dní so SSP": {"Hodnota": None, "Obdobie": None},
        "Priemerný počet dní so SSP": {"Hodnota": None, "Obdobie": None},
        "Najmenší počet dní so SSP": {"Hodnota": None, "Obdobie": None},
        "Absolútne najvyššia snehová pokrývka": {"Hodnota": None, "Obdobie": None},
        "Priemer maximálnych snehových pokrývok": {"Hodnota": None, "Obdobie": None},
        "Najnižšia maximálna snehová pokrývka": {"Hodnota": None, "Obdobie": None}
    }

    def find_extreme_date(date_series, find_min=True):
        timestamps = date_series.apply(convert_to_unix_timestamp)
        extreme_timestamp = timestamps.min() if find_min else timestamps.max()
        extreme_date = convert_from_unix_timestamp(extreme_timestamp)
        extreme_index = timestamps.idxmin() if find_min else timestamps.idxmax()
        return extreme_date, extreme_index

    def calculate_average_date(date_series):
        timestamps = date_series.apply(convert_to_unix_timestamp)
        average_timestamp = timestamps.mean()
        average_date = convert_from_unix_timestamp(average_timestamp)
        return average_date

    # Najskorší a najneskorší výskyt prvej SSP
    snow_extremes["Najskorší výskyt prvej SSP"]["Hodnota"], snow_extremes["Najskorší výskyt prvej SSP"]["Obdobie"] = find_extreme_date(snow_data["Prvy den s podmienkou"], find_min=True)
    snow_extremes["Najneskorší výskyt prvej SSP"]["Hodnota"], snow_extremes["Najneskorší výskyt prvej SSP"]["Obdobie"] = find_extreme_date(snow_data["Prvy den s podmienkou"], find_min=False)

    # Priemerný dátum výskytu prvej SSP
    snow_extremes["Priemerný dátum výskytu prvej SSP"]["Hodnota"] = calculate_average_date(snow_data["Prvy den s podmienkou"])

    # Najskorší a najneskorší výskyt poslednej SSP
    snow_extremes["Najskorší výskyt poslednej SSP"]["Hodnota"], snow_extremes["Najskorší výskyt poslednej SSP"]["Obdobie"] = find_extreme_date(snow_data["Posledny den s podmienkou"], find_min=True)
    snow_extremes["Najneskorší výskyt poslednej SSP"]["Hodnota"], snow_extremes["Najneskorší výskyt poslednej SSP"]["Obdobie"] = find_extreme_date(snow_data["Posledny den s podmienkou"], find_min=False)

    # Priemerný dátum výskytu poslednej SSP
    snow_extremes["Priemerný dátum výskytu poslednej SSP"]["Hodnota"] = calculate_average_date(snow_data["Posledny den s podmienkou"])

    # Najdlhšia a najkratšia séria so SSP
    snow_extremes["Najdlhšia séria so SSP"]["Hodnota"] = snow_data["Najdlhsia seria (dni)"].max()
    snow_extremes["Najdlhšia séria so SSP"]["Obdobie"] = snow_data["Najdlhsia seria (dni)"].idxmax()

    # Priemer najdlhších sérií so SSP
    snow_extremes["Priemer najdlhších sérií so SSP"]["Hodnota"] = int(snow_data["Najdlhsia seria (dni)"].mean())

    snow_extremes["Najkratšia séria so SSP"]["Hodnota"] = snow_data["Najdlhsia seria (dni)"].min()
    snow_extremes["Najkratšia séria so SSP"]["Obdobie"] = snow_data["Najdlhsia seria (dni)"].idxmin()

    # Najvyšší a najmenší počet dní so SSP
    snow_extremes["Najvyšší počet dní so SSP"]["Hodnota"] = snow_data["Pocet dni so snehom"].max()
    snow_extremes["Najvyšší počet dní so SSP"]["Obdobie"] = snow_data["Pocet dni so snehom"].idxmax()

    # Priemerný počet dní so SSP
    snow_extremes["Priemerný počet dní so SSP"]["Hodnota"] = int(snow_data["Pocet dni so snehom"].mean())

    snow_extremes["Najmenší počet dní so SSP"]["Hodnota"] = snow_data["Pocet dni so snehom"].min()
    snow_extremes["Najmenší počet dní so SSP"]["Obdobie"] = snow_data["Pocet dni so snehom"].idxmin()

    # Najvyššia snehová pokrývka from input data
    max_snow = data.loc[data["CSP"].idxmax()]
    
    snow_extremes["Absolútne najvyššia snehová pokrývka"]["Hodnota"] = int(max_snow["CSP"])
    snow_extremes["Absolútne najvyššia snehová pokrývka"]["Obdobie"] = max_snow["Datum"]
    snow_extremes["Najnižšia maximálna snehová pokrývka"]["Hodnota"] = snow_data["Max snehova pokryvka"].min()
    snow_extremes["Najnižšia maximálna snehová pokrývka"]["Obdobie"] = snow_data["Max snehova pokryvka"].idxmin()

    # Priemer maximálnych snehových pokrývok
    snow_extremes["Priemer maximálnych snehových pokrývok"]["Hodnota"] = int(snow_data["Max snehova pokryvka"].mean())

    return snow_extremes


def create_snow_coverage_frequency_table(monthly_stats, season):
    intervals_depth = ["0 cm", "1-10 cm", "11-20 cm", "21-40 cm", "41-60 cm", "61-80 cm", "80+ cm"]
    intervals_count = ["0 dní", "1-5 dní", "6-13 dní", "14-21 dní", "22-27 dní", "28+ dní"]

    months = SEASONS[season]
    max_value = monthly_stats["CSP_max"].max()

    frequency_count_table = pd.DataFrame(0, index=intervals_count, columns=months)

    for month in months:
        month_data = monthly_stats[monthly_stats["Mesiac"] == month]
        for value in month_data["CSP_count"]:
            if value == 0:
                frequency_count_table.at["0 dní", month] += 1
            elif 1 <= value <= 5:
                frequency_count_table.at["1-5 dní", month] += 1
            elif 6 <= value <= 13:
                frequency_count_table.at["6-13 dní", month] += 1
            elif 14 <= value <= 21:
                frequency_count_table.at["14-21 dní", month] += 1
            elif 22 <= value <= 27:
                frequency_count_table.at["22-27 dní", month] += 1
            else:
                frequency_count_table.at["28+ dní", month] += 1

    month_names = {month: WHOLE_YEAR[month] for month in months}

    frequency_count_table.rename(columns=month_names, inplace=True)
    frequency_count_table.insert(0, "Interval", intervals_count)

    frequency_max_table = pd.DataFrame(0, index=intervals_depth, columns=months)

    for month in months:
        month_data = monthly_stats[monthly_stats["Mesiac"] == month]
        for value in month_data["CSP_max"]:
            if value == 0:
                frequency_max_table.at["0 cm", month] += 1
            elif 1 <= value <= 10:
                frequency_max_table.at["1-10 cm", month] += 1
            elif 11 <= value <= 20:
                frequency_max_table.at["11-20 cm", month] += 1
            elif 21 <= value <= 40:
                frequency_max_table.at["21-40 cm", month] += 1
            elif 41 <= value <= 60:
                frequency_max_table.at["41-60 cm", month] += 1
            elif 61 <= value <= 80:
                frequency_max_table.at["61-80 cm", month] += 1
            else:
                frequency_max_table.at["80+ cm", month] += 1

    frequency_max_table.rename(columns=month_names, inplace=True)
    frequency_max_table.insert(0, "Interval", intervals_depth)

    print("Absolútna častosť maximálnych výšok snehovej pokrývky:")
    print(frequency_max_table)

    print("Absolútna častosť počtu dní so snehovou pokrývkou:")
    print(frequency_count_table)

    return frequency_count_table, frequency_max_table

