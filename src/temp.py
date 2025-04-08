import pandas as pd
from tools import convert_from_unix_timestamp, convert_to_unix_timestamp, find_longest_series, find_first_and_last_condition

def create_yearly_temperature_summary(monthly_stats):
    # Vytvorenie sumarizácie pre každý rok
    yearly_summary = (
        monthly_stats.groupby("Rok")
        .agg(
            Tmax_min=("Tmax_min", "min"),
            Tmax_max=("Tmax_max", "max"),
            Tmax_mean=("Tmax_mean", "mean"),
            Tmin_min=("Tmin_min", "min"),
            Tmin_max=("Tmin_max", "max"),
            Tmin_mean=("Tmin_mean", "mean"),
            Tavg_min=("Tavg_min", "min"),
            Tavg_max=("Tavg_max", "max"),
            Tavg_mean=("Tavg_mean", "mean"),
            Tmax_count35=("Tmax_count35", "sum"),
            Tmax_count30=("Tmax_count30", "sum"),
            Tmax_count25=("Tmax_count25", "sum"),
            Tmax_count0=("Tmax_count0", "sum"),
            Tmax_count_10=("Tmax_count_10", "sum"),
        )
        .reset_index()
    )
    yearly_summary["Rok"] = yearly_summary["Rok"].astype(int)
    yearly_summary["Tmax_min"] = yearly_summary["Tmax_min"].round(1)
    yearly_summary["Tmax_max"] = yearly_summary["Tmax_max"].round(1)
    yearly_summary["Tmax_mean"] = yearly_summary["Tmax_mean"].round(1)
    yearly_summary["Tmin_min"] = yearly_summary["Tmin_min"].round(1)
    yearly_summary["Tmin_max"] = yearly_summary["Tmin_max"].round(1)
    yearly_summary["Tmin_mean"] = yearly_summary["Tmin_mean"].round(1)
    yearly_summary["Tavg_min"] = yearly_summary["Tavg_min"].round(1)
    yearly_summary["Tavg_max"] = yearly_summary["Tavg_max"].round(1)
    yearly_summary["Tavg_mean"] = yearly_summary["Tavg_mean"].round(1)
    yearly_summary["Tmax_count35"] = yearly_summary["Tmax_count35"].astype(int)
    yearly_summary["Tmax_count30"] = yearly_summary["Tmax_count30"].astype(int)
    yearly_summary["Tmax_count25"] = yearly_summary["Tmax_count25"].astype(int)
    yearly_summary["Tmax_count0"] = yearly_summary["Tmax_count0"].astype(int)
    yearly_summary["Tmax_count_10"] = yearly_summary["Tmax_count_10"].astype(int)

    print(yearly_summary)

    return yearly_summary