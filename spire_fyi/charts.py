import pandas as pd
import altair as alt
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
    lines = base.mark_line().encode(
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
    )

    points = lines.mark_point().transform_filter(selection)
    rule = (
        base.transform_pivot("Name", value=metric, groupby=["Date"])
        .mark_rule()
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

    return chart.interactive().properties(height=800, width=800)


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
