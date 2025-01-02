import sys
import pandas as pd

def repair_data(data):
    # Nahradenie hodnoty 995, 999 a 0 v stĺpci CSP hodnotou NaN (prázdna hodnota)
    data["CSP"] = data["CSP"].replace(995, float('nan'))
    data["CSP"] = data["CSP"].replace(999, float('nan'))
    data["CSP"] = data["CSP"].replace(0, float('nan'))

    return data


def load_data(file_name):
    try:
        # Načítanie súboru
        data = pd.read_csv(
            file_name,
            delimiter="\t",
            decimal=",",
            na_values=[""],
            engine="python"
        )
    except FileNotFoundError:
        print(f"Chyba: Súbor {file_name} neexistuje.")
        sys.exit(1)
    except Exception as e:
        print(f"Chyba pri spracovaní súboru: {e}")
        sys.exit(1)

    return repair_data(data)

    
def process_data(station_id, data):
    # Filtrovanie podľa zadaného IND
    station_data = data[data["IND"] == int(station_id)]
    if station_data.empty:
        print(f"Nenašli sa údaje pre stanicu s ID {station_id}.")
        sys.exit(1)

    # Prevod stĺpca 'Datum' na datetime typ s presným formátom
    station_data["Datum"] = pd.to_datetime(station_data["Datum"], format='%d.%m.%Y', errors='coerce')
    
    # Pridanie stĺpcov pre Rok a Mesiac
    station_data['Rok'] = station_data['Datum'].dt.year
    station_data['Mesiac'] = station_data['Datum'].dt.month

    station_data["Tmax"] = station_data["Tmax"].apply(lambda x: round(x, 1) if pd.notnull(x) else x)
    station_data["Tmin"] = station_data["Tmin"].apply(lambda x: round(x, 1) if pd.notnull(x) else x)
    station_data["Tavg"] = station_data["Tavg"].apply(lambda x: round(x, 1) if pd.notnull(x) else x)
    station_data["R"] = station_data["R"].apply(lambda x: round(x, 1) if pd.notnull(x) else x)
    station_data["CSP"] = station_data["CSP"].apply(lambda x: int(x) if pd.notnull(x) else x)

    # Výpočet štatistík pre každý rok a mesiac
    monthly_stats = station_data.groupby(['Rok', 'Mesiac']).agg({
        "Tmax": ["min", "max", "mean"],
        "Tmin": ["min", "max", "mean"],
        "Tavg": ["min", "max", "mean"],
        "R": ["max", "count", "sum"],
        "CSP": ["max", "count", "sum"]
    }).reset_index()

    # Flatten the MultiIndex columns
    monthly_stats.columns = ['_'.join(col).strip() if type(col) is tuple else col for col in monthly_stats.columns]

    # Pridanie stĺpca Rok
    monthly_stats['Rok'] = monthly_stats['Rok_']

    # Zaokrúhlenie výsledkov na 1 desatinné miesto
    monthly_stats["Tmax_mean"] = monthly_stats["Tmax_mean"].round(1)
    monthly_stats["Tmin_mean"] = monthly_stats["Tmin_mean"].round(1)
    monthly_stats["Tavg_mean"] = monthly_stats["Tavg_mean"].round(1)
    monthly_stats["R_sum"] = monthly_stats["R_sum"].round(1)
    monthly_stats["R_count"] = monthly_stats["R_count"].apply(lambda x: int(x) if pd.notnull(x) else x)
    monthly_stats["CSP_max"] = monthly_stats["CSP_max"].apply(lambda x: int(x) if pd.notnull(x) else 0)
    monthly_stats["CSP_count"] = monthly_stats["CSP_count"].apply(lambda x: int(x) if pd.notnull(x) else x)
    monthly_stats["CSP_sum"] = monthly_stats["CSP_sum"].apply(lambda x: int(x) if pd.notnull(x) else x)

    # Pridanie stĺpca Mesiac
    monthly_stats['Mesiac'] = monthly_stats['Mesiac_']

    return monthly_stats


def calculate_historical_extremes(data):
    # Konverzia dátumu na datetime
    data["Datum"] = pd.to_datetime(data["Datum"], format='%d.%m.%Y', errors="coerce")

    # Historické maximá a minimá teploty
    max_temp = data.loc[data["Tmax"].idxmax()]
    min_temp = data.loc[data["Tmin"].idxmin()]

    temp_extremes = {
        "Tmax": {"Hodnota": max_temp["Tmax"], "Datum": max_temp["Datum"].strftime("%d.%m.%Y")},
        "Tmin": {"Hodnota": min_temp["Tmin"], "Datum": min_temp["Datum"].strftime("%d.%m.%Y")},
    }

    # Historické maximá zrážok a snehovej pokrývky
    max_rain = data.loc[data["R"].idxmax()]
    max_snow = data.loc[data["CSP"].idxmax()]

    precip_extremes = {
        "R": {"Hodnota": max_rain["R"], "Datum": max_rain["Datum"].strftime("%d.%m.%Y")},
        "CSP": {"Hodnota": max_snow["CSP"], "Datum": max_snow["Datum"].strftime("%d.%m.%Y")},
    }

    return temp_extremes, precip_extremes