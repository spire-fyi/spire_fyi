import altair as alt
import pandas as pd
import streamlit as st

import spire_fyi.utils as utils


def alt_line_chart(
    data: pd.DataFrame,
    metric: str,
    log_scale=False,
    chart_title="",
) -> alt.Chart:
    """Create a multiline Altair chart with tooltip

    Parameters
    ----------
    data : pd.DataFrame
        Data source to use
    colname : str
        Column name for values
    log_scale : str
        Use log scale for Y axis

    Returns
    -------
    alt.Chart
        Chart showing columnname values, and a multiline tooltip on mouseover
    """
    if log_scale:
        scale = "log"
    else:
        scale = "linear"
    columns = data["Name"].unique()

    base = alt.Chart(data, title=chart_title).encode(x=alt.X("yearmonthdate(Date):T", title=None))
    selection = alt.selection_single(
        fields=["Date"],
        nearest=True,
        on="mouseover",
        empty="none",
        clear="mouseout",
    )
    legend_selection = alt.selection_multi(fields=["Name"], bind="legend")
    lines = base.mark_line(point=True).encode(
        y=alt.Y(
            f"{metric}:Q",
            title=utils.metric_dict[metric],
            scale=alt.Scale(type=scale),
        ),
        color=alt.Color(
            "Name:N",
            title="Program Name",
            scale=alt.Scale(scheme="turbo"),
            sort=alt.EncodingSortField(metric, op="count", order="descending"),
        ),
        opacity=alt.condition(legend_selection, alt.value(1), alt.value(0.1)),
    )
    points = lines.mark_point(size=50).transform_filter(selection)
    rule = (
        base.transform_pivot("Name", value=metric, groupby=["Date"])
        .mark_rule(color="#983832")
        .encode(
            opacity=alt.condition(selection, alt.value(0.3), alt.value(0)),
            tooltip=[alt.Tooltip("yearmonthdate(Date)", title="Date")]
            + [
                alt.Tooltip(
                    c,
                    type="quantitative",
                    format=",",
                )
                for c in columns
            ],
        )
        .add_selection(selection)
    )
    chart = lines + points + rule

    return (
        chart.add_selection(legend_selection)
        .interactive()
        .properties(height=800, width=800)
        # .configure_axis(grid=False)
    )


def alt_line_metric(chart_df, metric, agg_method):
    chart = (
        alt.Chart(chart_df)
        .mark_line()
        .encode(
            x=alt.X("yearmonthdate(Date)", title=None),
            y=alt.Y(metric, title=utils.metric_dict[metric], sort="-y"),
            color=alt.Color(
                "Name",
                title="Program Name",
                scale=alt.Scale(scheme="turbo"),
                sort=alt.EncodingSortField(metric, op=agg_method, order="descending"),
            ),
            tooltip=[
                alt.Tooltip("yearmonthdate(Date)", title="Date"),
                alt.Tooltip("TX_COUNT", title=utils.metric_dict["TX_COUNT"], format=","),
                alt.Tooltip("SIGNERS", title=utils.metric_dict["SIGNERS"], format=","),
                alt.Tooltip("PROGRAM_ID", title="Program ID"),
                alt.Tooltip("LABEL_TYPE", title="Label Type"),
                alt.Tooltip("LABEL_SUBTYPE", title="Label Subtype"),
                alt.Tooltip("LABEL", title="Label"),
                alt.Tooltip("ADDRESS_NAME", title="Address Name"),
            ],
        )
        .properties(height=800, width=800)
        .interactive()
    )
    return chart


def alt_weekly_unique_chart(df, title, y, ytitle):
    chart = (
        alt.Chart(df, title=title)
        .mark_area(
            line={"color": "#4B3D60"},
            color=alt.Gradient(
                gradient="linear",
                stops=[
                    alt.GradientStop(color="#4B3D60", offset=0),
                    alt.GradientStop(color="#FD5E53", offset=1),
                ],
                x1=1,
                x2=1,
                y1=1,
                y2=0,
            ),
            interpolate="monotone",
        )
        .encode(
            x=alt.X("yearmonthdate(WEEK)", title="Date"),
            y=alt.Y(y, title=ytitle),
            tooltip=[
                alt.Tooltip(
                    "yearmonthdate(WEEK)",
                    title="Date (start of week)",
                ),
                alt.Tooltip(y, title=ytitle, format=","),
            ],
        )
        .properties(height=600)
    )
    return chart


def alt_weekly_cumulative_chart(df, title, bar_y, line_y):

    base = alt.Chart(df, title=title).encode(
        x=alt.X("yearmonthdate(WEEK):T", title="Date"),
        tooltip=[
            alt.Tooltip("yearmonthdate(WEEK):T", title="Date (start of week)"),
            alt.Tooltip(bar_y, format=","),
            alt.Tooltip(line_y, format=","),
        ],
    )
    bar = base.mark_bar(width=3, color="#4B3D60").encode(
        y=alt.Y(bar_y),
    )
    line = base.mark_line(color="#FFE373").encode(y=alt.Y(line_y))
    chart = (bar + line).properties(height=600).resolve_scale(y="independent").properties(height=600)

    return chart


def alt_daily_cumulative_chart(df, title, bar_y, line_y, width=3):

    base = alt.Chart(df, title=title).encode(
        x=alt.X("yearmonthdate(Date):T", title="Date"),
        tooltip=[
            alt.Tooltip("yearmonthdate(Date):T"),
            alt.Tooltip(bar_y, format=","),
            alt.Tooltip(line_y, format=","),
        ],
    )
    bar = base.mark_bar(width=width, color="#4B3D60").encode(
        y=alt.Y(bar_y),
    )
    line = base.mark_line(color="#FFE373").encode(y=alt.Y(line_y))
    chart = (
        (bar + line)
        .interactive()
        .properties(height=600)
        .resolve_scale(y="independent")
        .properties(height=600)
    )

    return chart
