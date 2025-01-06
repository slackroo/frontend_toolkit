"""The table page."""

from ..templates import template
from ..templates.reactmultiselect import multiselect
from ..backend.table_state import TableState
from ..backend._check_common import CommonState, QUARTER_COL, CHAMPION_MODEL, ALL_COUNTRIES
from ..views.table import main_table
from typing import Union, List, Dict, Callable, Any

import reflex as rx
import reflex_chakra as rc
from reflex_ag_grid import ag_grid
import pandas as pd
import re

import plotly.express as px
import plotly.graph_objects as go

# QUARTER_COL: str = 'REPORTED_QUARTER'
# CHAMPION_MODEL: str = 'LR+TCN'
#
# hierarchy_forecasts_df: pd.DataFrame = pd.read_csv("assets/data/hierarchy_forecasts_all_combined_formated.csv").round(4)
# hierarchy_forecasts_df = hierarchy_forecasts_df.map(lambda x: x.upper() if isinstance(x, str) else x)
#
# champion_model_mask = (hierarchy_forecasts_df['MODEL'].isin(['ACTUALS', CHAMPION_MODEL]))
#
# # print(hierarchy_df.head())
# temp_mapper_df = hierarchy_forecasts_df[champion_model_mask].reset_index(drop=True)
# country_category_dict = {index: sorted(row.to_list()[0]) for index, row in
#                          temp_mapper_df.groupby(['COUNTRY']).agg({'PROD_CATEGORY': 'unique'}).iterrows()}
# hierarchy_mapper_df = hierarchy_forecasts_df[hierarchy_forecasts_df['Model'].isin(['Actuals','lr+tcn'])].groupby(['Country','PROD_CATEGORY','OWNER'],dropna=True).agg({'BRAND_DESC':'unique'})

# champion_model_df = hierarchy_forecasts_df[champion_model_mask].reset_index(drop=True).copy()
# print("tcn_df")
# print(champion_model_df.head())
# quarter_mask: bool = (~CommonState.champion_model_df[QUARTER_COL].str.contains('NOT'))
# quarterly_hierarchy_brands_df : pd.DataFrame= CommonState.champion_model_df[quarter_mask].groupby(
#     [QUARTER_COL, 'KEY_', 'COUNTRY', 'BRAND_DESC', 'SHEET', 'OWNER', 'PROD_CATEGORY', 'PROD_CATEGORY_DESCR']).agg(
#     {'VOLUME_UPC': 'sum', 'VALUE_USD': 'sum'}).reset_index()
# print(quarterly_hierarchy_brands_df.head(30))
# print(quarterly_hierarchy_brands_df[QUARTER_COL].unique())
# print(quarterly_hierarchy_brands_df['BRAND_DESC'].unique())


table_selector: List[str] = ['Raw', "Hierarchy Brand Forecasts"]
db_selector: List[str] = ['Nielsen top 40', 'Nielsen non top 40', 'Hist', 'Channel']
db_period_agg_selector: List[str] = CommonState.period_agg_selector
db_metric_selector: List[str] = CommonState.metric_selector
# quarter_periods_selector: List[str] = sorted(set(CommonState.quarterly_champion_df[QUARTER_COL]))
# monthly_periods_selector: List[str] = sorted(set(CommonState.champion_model_df['DATE']))
# country_selector: List[str] = sorted(set(CommonState.champion_model_df['COUNTRY']))


# class DatabaseSelectorState(rx.State):
class DatabaseSelectorState(CommonState):
    table_selected: str = table_selector[1]
    data: list[dict] = []
    data_cols: list[str] = []

    db_selected: str = db_selector[0]
    db_period_agg_selected: str = db_period_agg_selector[0]
    db_metric_selected: str = "VALUE_USD"
    quarter_periods_selected: str = CommonState.quarter_periods_selector[-1]
    monthly_periods_selected: str = CommonState.monthly_periods_selector[-1]

    db_plots_control: str | None = None
    # main_period_selector: List[str] = monthly_periods_selector
    main_period_selected: str | None = None
    period_selected: str | None = None

    # country_selected: str | None = 'UNITED STATES'
    # country_monthly_df: pd.DataFrame = pd.DataFrame# = champion_model_df[champion_model_df['COUNTRY'] == country_selected]
    # country_quarterly_df: pd.DataFrame #  = quarterly_hierarchy_brands_df[quarterly_hierarchy_brands_df['COUNTRY'] == country_selected]

    multi_selected: List[Dict[str, Any]] = [
        {"label": "Grapes 🍇", "value": "grapes"},
        {"label": "Mango 🥭", "value": "mango"},
        {"label": "Strawberry 🍓", "value": "strawberry", "disabled": True},
    ]

    @rx.event
    def change_table(self, table_selected: str):
        """Change the select table var."""
        self.table_selected = table_selected

    @rx.event
    def change_db(self, db_selected: str):
        """Change the select db var."""
        self.db_selected = db_selected



    @rx.event
    def change_monthly_period(self, monthly_periods_selected: str):
        """Change the select db var."""
        self.monthly_periods_selected = monthly_periods_selected
        self.main_period_selected = monthly_periods_selected

    @rx.event
    def change_quarterly_period(self, quarter_periods_selected: str):
        """Change the select db var."""
        self.quarter_periods_selected = quarter_periods_selected
        self.main_period_selected = quarter_periods_selected

    @rx.event
    def change_period_agg(self, db_period_agg_selected: str):
        """Change the select db var."""
        self.db_period_agg_selected = db_period_agg_selected

    @rx.event
    def change_page_state(self, db_period_agg_selected: str, country_selected: str, metric_selected: str):
        """Change the select db var."""

        self.db_period_agg_selected = db_period_agg_selected
        self.country_selected = country_selected
        self.db_metric_selected = metric_selected

    @rx.event
    def load_data(self):
        self.data = self.country_quarterly_df.to_dict("records")
        self.data_cols = self.quarterly_cols


def radar_traces(input_df, country_select='UNITED STATES', period_select='Q1 2019', metric_select='VOLUME_UPC',
                 frequency_select='QUARTER_YEAR'):

    print(period_select)
    print(country_select)


    print(metric_select)

    if 'vol' in metric_select.lower():
        metric_select = 'VOLUME_UPC'
    else:
        metric_select = 'VALUE_USD'

    if 'quar' in frequency_select.lower():
        frequency_select = QUARTER_COL
        quarterly_hierarchy_brands_df = input_df
    else:
        frequency_select = 'DATE'
        quarterly_hierarchy_brands_df = input_df.groupby(
            ['DATE', 'KEY_', 'COUNTRY', 'BRAND_DESC', 'SHEET', 'OWNER', 'PROD_CATEGORY', 'PROD_CATEGORY_DESCR']
        ).agg({'VOLUME_UPC': 'sum', 'VALUE_USD': 'sum'}).reset_index()

    country_selected = country_select
    period_selected = period_select
    metric_selected = metric_select

    print(quarterly_hierarchy_brands_df.head())

    xx2 = quarterly_hierarchy_brands_df[(quarterly_hierarchy_brands_df['KEY_'].str.contains(country_selected)) & (
        quarterly_hierarchy_brands_df['KEY_'].str.contains('_INDUSTRY')) & (
                                                quarterly_hierarchy_brands_df[frequency_select] == period_selected)]
    xx3 = quarterly_hierarchy_brands_df[(quarterly_hierarchy_brands_df['KEY_'].str.contains(country_selected)) & (
        quarterly_hierarchy_brands_df['KEY_'].str.contains('_TCCC')) & (
                                            quarterly_hierarchy_brands_df['BRAND_DESC'].str.contains('AGG')) & (
                                                quarterly_hierarchy_brands_df[frequency_select] == period_selected)]
    xx4 = quarterly_hierarchy_brands_df[(quarterly_hierarchy_brands_df['KEY_'].str.contains(country_selected)) & (
        quarterly_hierarchy_brands_df['KEY_'].str.contains('_PEPS')) & (
                                            quarterly_hierarchy_brands_df['BRAND_DESC'].str.contains('AGG')) & (
                                                quarterly_hierarchy_brands_df[frequency_select] == period_selected)]
    xx5 = quarterly_hierarchy_brands_df[(quarterly_hierarchy_brands_df['KEY_'].str.contains(country_selected)) & (
        quarterly_hierarchy_brands_df['KEY_'].str.contains('_ALL OTH')) & (
                                            quarterly_hierarchy_brands_df['BRAND_DESC'].str.contains('AGG')) & (
                                                quarterly_hierarchy_brands_df[frequency_select] == period_selected)]

    # Create radar traces
    print(xx3)
    # metric_selected = ""
    traces = []
    traces.append(go.Scatterpolar(r=xx2[metric_selected], theta=xx2['PROD_CATEGORY'], fill='toself',
                                  name=f'{country_selected} Industry'))
    traces.append(go.Scatterpolar(r=xx3[metric_selected], theta=xx3['PROD_CATEGORY'], fill='toself', name='tccc_share'))
    traces.append(
        go.Scatterpolar(r=xx4[metric_selected], theta=xx4['PROD_CATEGORY'], fill='toself', name='pepsi_share'))
    traces.append(
        go.Scatterpolar(r=xx5[metric_selected], theta=xx5['PROD_CATEGORY'], fill='toself', name='others_share'))

    print(traces)

    return traces


def combine_radar_traces(traces_list):
    print(type(traces_list))
    base_fig = go.Figure()

    # Add all traces from the list to the base figure
    for traces in traces_list:
        for trace in traces:
            base_fig.add_trace(trace)

    for trace in base_fig.data:

        if ('Industry' in trace.name) or 'tccc' in trace.name:
            trace.visible = True
            trace.opacity = 1.0
        else:
            trace.visible = 'legendonly'
            trace.opacity = 1.0

    base_fig.update_layout(
        title='Combined Category Radar '
    )

    return base_fig

def trace_list_outter(traces) -> list:
    return [
        o
        for o in traces
    ]
class PlotlyState(DatabaseSelectorState):
    monthly_country_trace_ls: List = []
    quarterly_country_trace_ls: List = []
    monthly_radar_fig: go.Figure = go.Figure()
    quarterly_radar_fig: go.Figure = go.Figure()

    df = px.data.gapminder().query(f"country=='Canada'")
    figure = px.line(
        df,
        x="year",
        y="lifeExp",
        title="Life expectancy in Canada",
    )

    # @rx.var
    # def trace_list(self, traces) -> list:
    #     return [
    #         o
    #         for o in traces
    #     ]

    @rx.event
    def set_radar_chart(self, country, monthly_period, quarterly_period, metric_select):
        self.monthly_country_trace_ls = radar_traces(self.country_monthly_df, country, monthly_period, metric_select, 'DATE')
        self.quarterly_country_trace_ls = radar_traces(self.country_quarterly_df, country, quarterly_period, metric_select, QUARTER_COL)
        # tt = self.trace_list(self.monthly_country_trace_ls)
        # tt = trace_list_outter(self.monthly_country_trace_ls)
        # self.monthly_radar_fig = combine_radar_traces(self.monthly_country_trace_ls)
        self.monthly_radar_fig = combine_radar_traces([self.monthly_country_trace_ls])
        self.quarterly_radar_fig = combine_radar_traces([self.quarterly_country_trace_ls])

        # self.df = px.data.gapminder().query(
        #     f"country=='{country}'"
        # )
        # self.figure = px.line(
        #     self.df,
        #     x="year",
        #     y="lifeExp",
        #     title=f"Life expectancy in {country}",
        # )


def ag_grid_simple_2():  # ToDo Fix the data selection
    return ag_grid(
        id="ag_grid_basic_2",
        row_data=DatabaseSelectorState.data[:200],
        column_defs=DatabaseSelectorState.data_cols,
        pagination=True,
        pagination_page_size=10,
        pagination_page_size_selector=[10, 40, 100],
        width="100%",
        height="40vh",
    )


def select(label, items, value, on_change):
    return rx.flex(
        rx.text(label),
        rx.select.root(
            rx.select.trigger(),
            rx.select.content(
                *[
                    rx.select.item(item, value=item)
                    for item in items
                ]
            ),
            value=value,
            on_change=on_change,
        ),
        align="center",
        justify="center",
        direction="column",
    )


def main_db_selectors() -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.heading("Select the DataBase", size="1"),
            rx.select(
                db_selector,
                placeholder=DatabaseSelectorState.db_selected,
                label="Select DB",
                on_change=DatabaseSelectorState.change_db
            )
        ),
        rx.vstack(
            rx.heading("Select the Table", size="1"),
            rx.select(
                table_selector,
                placeholder=DatabaseSelectorState.table_selected,
                label="Select table",
                on_change=DatabaseSelectorState.change_table
            )
        ),
        rx.text(DatabaseSelectorState.table_selected),

    )


def show_plot_tabs() -> rx.Component:
    """Change the section of plot views conditional render of page based on table selected raw/ forecast."""
    return rx.hstack(
        rx.cond(
            # Condition
            DatabaseSelectorState.table_selected == "Hierarchy Brand Forecasts",
            # Truth render
            show_hierarchy_table_plot_tabs(),
            # False condition
            show_raw_table_plot_tabs()
        ),
        # rx.text(DatabaseSelectorState.db_period_agg_selected),
        # rx.text(DatabaseSelectorState.db_metric_selected),

        spacing="8",
        flex_wrap="nowrap",
        width='100%',
        justify='between'
    )


def show_segment_control_selectors() -> rx.Component:
    """Change the section of period or metric."""
    return rx.hstack(
        rx.text("Select the periodic view and Metric"),
        show_periods_segment(),
        show_metrics_segment(),
        # rx.text(DatabaseSelectorState.db_period_agg_selected),
        # rx.text(DatabaseSelectorState.db_metric_selected),

        # spacing="8",
        flex_wrap="nowrap",
        width='100%',
        justify='between'
    )


def show_metrics_segment() -> rx.Component:
    return rx.segmented_control.root(
        rx.segmented_control.item("Value", value="VALUE_USD"),
        rx.segmented_control.item("Volume", value="VOLUME_UPC"),
        variant="surface",
        color_scheme="red",
        radius='large',
        on_change=DatabaseSelectorState.setvar("db_metric_selected"),
        value=DatabaseSelectorState.db_metric_selected,
    )


def show_periods_segment() -> rx.Component:
    return rx.segmented_control.root(
        rx.segmented_control.item("Monthly", value="monthly"),
        rx.segmented_control.item("Quarterly", value="quarterly"),
        on_change=[lambda p: DatabaseSelectorState.change_page_state(p, DatabaseSelectorState.country_selected,
                                                                     DatabaseSelectorState.db_metric_selected),
                   PlotlyState.set_radar_chart(DatabaseSelectorState.country_selected,
                                               DatabaseSelectorState.monthly_periods_selected,
                                               DatabaseSelectorState.quarter_periods_selected,
                                               DatabaseSelectorState.db_metric_selected)],
        # value=DatabaseSelectorState.db_period_agg_selected,
    )


def show_raw_table_plot_tabs() -> rx.Component:
    return rx.segmented_control.root(
        # rx.segmented_control.item("World", value="world"),
        rx.segmented_control.item("Radar", value="radar"),
        rx.segmented_control.item("Sun Burst", value="sun_burst"),
        rx.segmented_control.item("Tree Map", value="tree_map"),
        on_change=DatabaseSelectorState.setvar("db_plots_control"),
        value=DatabaseSelectorState.db_plots_control,
    )


class MultiSelectState(rx.State):
    selected: List[dict[str, str]] = []

    @rx.var(cache=True)
    def selected_values(self) -> str:
        return ", ".join([d["value"] for d in self.selected])

    @rx.var
    def multi_select_options(self) -> list[dict[str, str]]:
        return [
            {"label": o, "value": o}
            for o in ALL_COUNTRIES
        ]


def multiselect_country() -> rx.Component:
    return rx.vstack(
        rx.heading("Select Multiple Countries", size="1"),
        multiselect(
            # options=[
            #     {"value": "opt1", "label": "Option 1"},
            #     {"value": "opt2", "label": "Option 2"},
            # ],
            options=MultiSelectState.multi_select_options,
            on_change=MultiSelectState.set_selected,
            placeholder="Select multi countries",

        ),
        rx.text(f"Multiselect value {MultiSelectState.selected_values}"),
    )


class TabsState(rx.State):
    """The app state."""

    tab_value = "radar"
    tab_selected = ""

    @rx.event
    def change_value(self, val):
        self.tab_selected = f"{val} clicked!"
        self.tab_value = val


def show_hierarchy_table_plot_tabs() -> rx.Component:
    return rx.tabs.root(
        rx.tabs.list(
            rx.tabs.trigger("Radar", value="radar"),
            rx.tabs.trigger("Sun Burst", value="sun_burst"),
            rx.tabs.trigger("Tree Map", value="tree_map"),
        ),
        rx.tabs.content(
            radar_view(),
            value="radar",
        ),
        rx.tabs.content(
            sunburst_view(),
            value="sun_burst",
        ),
        rx.tabs.content(
            treemap_view(),
            value="tree_map",
        ),
        default_value="sun_burst",
        value=TabsState.tab_value,
        on_change=[lambda x: TabsState.change_value(x),
                   PlotlyState.set_radar_chart(DatabaseSelectorState.country_selected,
                                               DatabaseSelectorState.monthly_periods_selected, # FOR QUARTER>>>?
                                               DatabaseSelectorState.quarter_periods_selected,
                                               DatabaseSelectorState.db_metric_selected)],
        width="100%"
    )


# def filter_options(options: List[Dict[str, str]], filter: Optional[str]) -> List[Dict[str, str]]:
#     if not filter:
#         return options
#     # Create a case-insensitive regular expression
#     pattern = re.compile(filter, re.IGNORECASE)
#     # Filter options based on whether the 'value' key matches the pattern
#     return [option for option in options if 'value' in option and option['value'] and pattern.search(option['value'])]


# state.country_trace_ls = radar_traces(state.qurterly_hierarchy_brands_df, country_select=state.country_selected, period_select=state.p1_selected, metric_select=state.db_metric_selected, frequency_select= state.db_freq_selected)
# # print(type(state.country_trace_ls))
# state.combined_radar_fig = combine_radar_traces([state.country_trace_ls])
# state.select_multi_country = sorted(list(set(state.qurterly_hierarchy_brands_df['Country'])))
def radar_box() -> rx.Component:
    return rx.flex(
        rx.center(
            rx.heading(
                f"{DatabaseSelectorState.country_selected} Category Radar for {DatabaseSelectorState.main_period_selected}",
                size="3"
            ),
            # rx.center(
            #     rx.plotly(data=PlotlyState.figure),
            #     width="98%",
            #     height="100%",
            # ),
            rx.cond(
                DatabaseSelectorState.db_period_agg_selected == "monthly",
                rx.plotly(data=PlotlyState.monthly_radar_fig),
                rx.plotly(data=PlotlyState.quarterly_radar_fig),

            ),

            width="50%",
            text_align="center",
            # padding="1em",
            padding_top="1em",
            border_width="1px",
            border_radius="5px",
            direction="column"

        ),
        rx.center(
            rx.heading(
                f"Countries Category Radar for {MultiSelectState.selected_values}",
                size="3"
            ),
            # rx.box(
            #     rx.plotly(data=PlotlyState.figure),
            #     width="100%",
            #     height="100%",
            # ),
            rx.plotly(data=PlotlyState.figure),
            width="50%",
            text_align="center",
            # padding="1em",
            padding_top="1em",
            border_width="1px",
            border_radius="5px",
            direction="column"

        ),
        direction="row",
        align="start",
        width="100%",
        spacing="1",
        justify='between'

    )


def radar_view() -> rx.Component:
    return rx.flex(
        rx.spacer(),
        rx.heading("Radar plot : View the Categories radar for a country and period. ", size="3", align='left'),
        rx.flex(
            common_plot_filters(),
            # rx.spacer(),
            multiselect_country(),

            spacing="9",
            justify='between',

            flex_wrap="wrap",
            width='100%',

        ),
        radar_box(),
        spacing="3",
        direction="column",
        width="100%",
    )


def sunburst_view() -> rx.Component:
    return rx.flex(
        rx.spacer(),
        rx.heading("Sun Burst plot : View the Hierachchy share for a country and period", size="3"),
        common_plot_filters(),
        spacing="3",
        direction="column",
    )


def treemap_view() -> rx.Component:
    return rx.flex(
        rx.spacer(),
        rx.heading("Tree Map plot : View the  share for a country and period", size="3"),
        common_plot_filters(),
        spacing="3",
        direction="column",
    )


def common_plot_filters():
    return rx.hstack(
        rx.vstack(
            rx.heading("Select the Period", size="1"),
            rx.cond(
                DatabaseSelectorState.db_period_agg_selected == "monthly",
                rx.select(
                    CommonState.monthly_periods_selector,
                    placeholder=DatabaseSelectorState.monthly_periods_selected,
                    label="Select Period",
                    on_change=[DatabaseSelectorState.change_monthly_period,
                               PlotlyState.set_radar_chart(DatabaseSelectorState.country_selected,
                                                           DatabaseSelectorState.monthly_periods_selected,
                                                           DatabaseSelectorState.quarter_periods_selected,
                                                           DatabaseSelectorState.db_metric_selected)],
                ),
                rx.select(
                    CommonState.quarter_periods_selector,
                    placeholder=DatabaseSelectorState.quarter_periods_selected,
                    label="Select Period",
                    on_change=[
                        DatabaseSelectorState.change_quarterly_period,
                        PlotlyState.set_radar_chart(DatabaseSelectorState.country_selected,
                                                    DatabaseSelectorState.quarter_periods_selected,
                                                    DatabaseSelectorState.quarter_periods_selected,
                                                    DatabaseSelectorState.db_metric_selected)
                    ]
                )
            ),
            rx.cond(
                DatabaseSelectorState.db_period_agg_selected =='monthly',
                rx.text(DatabaseSelectorState.monthly_periods_selected),
                rx.text(DatabaseSelectorState.quarter_periods_selected)
            )
        ),
        rx.vstack(
            rx.heading("Select the Country", size="1"),
            rx.select(
                CommonState.country_selector,
                placeholder=DatabaseSelectorState.country_selected,
                label="Select Country",
                on_change=[
                    DatabaseSelectorState.change_country,
                    lambda c: PlotlyState.set_radar_chart(
                        c,
                        DatabaseSelectorState.monthly_periods_selected,
                        DatabaseSelectorState.quarter_periods_selected,
                        DatabaseSelectorState.db_metric_selected
                    )
                           ],
            ),
            rx.text(DatabaseSelectorState.country_selected),
            rx.text(DatabaseSelectorState.db_metric_selected)
        ),
    )


@template(route="/database", title="Database", on_load=TableState.load_entries)
def database() -> rx.Component:
    """The table page.

    Returns:
        The UI for the databasse page.
    """
    return rx.vstack(
        rx.heading("Database", size="8"),
        rx.divider(),
        main_db_selectors(),
        ag_grid_simple_2(),
        show_segment_control_selectors(),
        show_plot_tabs(),
        spacing="2",
        width="100%",
    )
