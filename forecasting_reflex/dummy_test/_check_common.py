import reflex as rx
import pandas as pd
from typing import Union, List, Dict, Callable, Any

QUARTER_COL: str = 'REPORTED_QUARTER'
CHAMPION_MODEL: str = 'LR+TCN'

hierarchy_forecasts_df: pd.DataFrame = pd.read_csv("assets/data/hierarchy_forecasts_all_combined_formated.csv")
hierarchy_forecasts_df = hierarchy_forecasts_df.map(lambda x: x.upper() if isinstance(x, str) else x)
champion_model_mask = (hierarchy_forecasts_df['MODEL'].isin(['ACTUALS', CHAMPION_MODEL]))
base_champion_model_df = hierarchy_forecasts_df[champion_model_mask].reset_index(drop=True).copy()

quarter_mask = (~base_champion_model_df[QUARTER_COL].str.contains('NOT'))
base_quarterly_champion_df = base_champion_model_df[quarter_mask].groupby(
    [QUARTER_COL, 'KEY_', 'COUNTRY', 'BRAND_DESC', 'SHEET', 'OWNER', 'PROD_CATEGORY', 'PROD_CATEGORY_DESCR']).agg(
    {'VOLUME_UPC': 'sum', 'VALUE_USD': 'sum'}).reset_index()

ALL_COUNTRIES = sorted(set(base_champion_model_df['COUNTRY']))

class CommonState(rx.State):
    refresh_interval: int = 15
    auto_update: bool = True
    # prefer_plain_text: bool = True
    # posts_per_page: int = 20
    QUARTER_COL: str = 'REPORTED_QUARTER'
    CHAMPION_MODEL: str = 'LR+TCN'
    country_selected: str = 'UNITED STATES'
    hierarchy_forecasts_df: pd.DataFrame = hierarchy_forecasts_df
    champion_model_df: pd.DataFrame = base_champion_model_df
    quarterly_champion_df: pd.DataFrame = base_quarterly_champion_df

    country_quarterly_df: pd.DataFrame = quarterly_champion_df[quarterly_champion_df['COUNTRY'] == country_selected]
    country_monthly_df: pd.DataFrame = champion_model_df[champion_model_df['COUNTRY'] == country_selected]

    monthly_cols: list = [{"field": i} for i in champion_model_df.columns]
    quarterly_cols: list = [{"field": i} for i in quarterly_champion_df.columns]

    country_category_dict: dict = {
        index: sorted(row.to_list()[0]) for index, row in
        champion_model_df.groupby(['COUNTRY']).agg({'PROD_CATEGORY': 'unique'}).iterrows()
    }
    quarter_periods_selector: List[str] = sorted(set(base_quarterly_champion_df[QUARTER_COL]))
    monthly_periods_selector: List[str] = sorted(set(base_champion_model_df['DATE']))
    country_selector: List[str] = ALL_COUNTRIES
    period_agg_selector: List[str] = ['monthly', 'quarterly']
    metric_selector: List[str] = ['value', 'volume']

    @rx.event
    def change_country(self, country_selected: str):
        """Change the select db var."""
        self.country_selected = country_selected
        self.country_quarterly_df = self.quarterly_champion_df[self.quarterly_champion_df['COUNTRY'] == country_selected]
        self.country_monthly_df = self.champion_model_df[self.champion_model_df['COUNTRY'] == country_selected]










