import datetime

import altair as alt
import pandas as pd
import streamlit as st

import spire_fyi.utils as utils


def alt_line_chart(
    data: pd.DataFrame,
    metric: str,
    log_scale=False,
    chart_title="",
    legend_title="Program Name",
    unique_column_name="Name",
    interactive=True,
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
    columns = data[unique_column_name].unique()
    base = alt.Chart(data, title=chart_title).encode(x=alt.X("yearmonthdate(Date):T", title=None))
    selection = alt.selection_point(
        fields=["Date"],
        nearest=True,
        on="mouseover",
        empty=False,
        clear="mouseout",
    )
    legend_selection = alt.selection_point(fields=[unique_column_name], bind="legend")
    lines = base.mark_line(point=True, interpolate="monotone").encode(
        y=alt.Y(
            f"{metric}:Q",
            title=utils.metric_dict[metric],
            scale=alt.Scale(type=scale),
        ),
        color=alt.Color(
            f"{unique_column_name}:N",
            title=legend_title,
            scale=alt.Scale(scheme="turbo"),
            sort=alt.EncodingSortField(metric, op="count", order="descending"),
            legend=alt.Legend(symbolLimit=50),
        ),
        opacity=alt.condition(legend_selection, alt.value(1), alt.value(0.1)),
    )
    points = lines.mark_point(size=50).transform_filter(selection)
    rule = (
        base.transform_pivot(unique_column_name, value=metric, groupby=["Date"])
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
        .add_params(selection)
    )
    chart = lines + points + rule

    if interactive:
        chart = chart.interactive()

    return (
        chart.add_params(legend_selection).properties(height=800, width=800)
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


@st.cache_data(ttl=3600 * 6)
def alt_stakers_chart(
    df, title, ycol, ytitle, colorcol, colortitle, lst, chart_type="Area", normalize=False, interactive=None
):
    stack = "normalize" if normalize else True
    legend_selection = alt.selection_point(fields=["Name"], bind="legend")
    rank = df.groupby(colorcol)[ycol].mean().sort_values(ascending=False).rank().to_dict()
    if "Other" in rank:
        rank["Other"] = -1
    rank_str = str({k: int(v) for k, v in rank.items()})

    tooltips = [
        alt.Tooltip("yearmonthdate(Date)", title="Date"),
        alt.Tooltip("Name"),
        alt.Tooltip("Address"),
        alt.Tooltip("Total Stake", format=",.1f"),
        alt.Tooltip("Rank", title="Staker Rank", format=",.0f"),
    ]
    if lst is not None:
        tooltips += [
            alt.Tooltip("Amount", title=f"Amount, {lst}", format=",.1f"),
            alt.Tooltip("Lst Rank", title=f"{lst} Rank", format=",.0f"),
        ]
    if chart_type == "Area":
        base = (
            alt.Chart(df, title=title)
            .transform_calculate(order=f"{rank_str}[datum['{colorcol}']]")
            .mark_area(interpolate="monotone")
        )
    elif chart_type == "Line":
        base = (
            alt.Chart(df, title=title)
            .transform_calculate(order=f"{rank_str}[datum['{colorcol}']]")
            .mark_line(point=True)
        )
        stack = False if not normalize else "normalize"
    chart = (
        (
            base.encode(
                x=alt.X("yearmonthdate(Date):T", title="Date"),
                y=alt.Y(
                    ycol,
                    title=ytitle,
                    stack=stack,
                ),
                color=alt.Color(
                    colorcol,
                    title=colortitle,
                    scale=alt.Scale(scheme="turbo"),
                    sort=alt.SortField("order", "descending"),
                    # sort=alt.EncodingSortField(ycol, op="mean", order="descending"),
                    legend=alt.Legend(symbolLimit=50),
                ),
                tooltip=tooltips,
                # href="Explorer Url",
                opacity=alt.condition(legend_selection, alt.value(1), alt.value(0.1)),
                order="order:O",
            )
        )
        .properties(height=800, width=800)
        .add_params(legend_selection)
    )
    if interactive is not None:
        bind_x = False if interactive == "y-axis" else True
        bind_y = False if interactive == "x-axis" else True
        chart = chart.interactive(bind_x=bind_x, bind_y=bind_y)
    return chart


@st.cache_data(ttl=3600 * 6)
def alt_total_lst(
    df,
    date_range,
    title="Total LST Balance by Top SOL Stakers",
    chart_type="Area",
    include_total_stake="",
    normalize=False,
    interactive=None,
    lst=None,
):
    # def nonzero_mean(x):
    #     return x[x > 0].mean()
    min_stake_date = df[df["Amount"].notna()].Date.min()
    if date_range == "All dates":
        chart_df = df.copy()[df.Date >= min_stake_date]
    elif date_range == "Past Year":
        past_year = pd.to_datetime(datetime.datetime.today(), utc=True) - pd.Timedelta("365d")
        if past_year > min_stake_date:
            chart_df = df.copy()[df.Date >= (past_year)]
        else:
            chart_df = df.copy()[df.Date >= (min_stake_date)]
    else:
        chart_df = df.copy()[
            df.Date >= (pd.to_datetime(datetime.datetime.today(), utc=True) - pd.Timedelta(date_range))
        ]

    total_df = chart_df.copy().groupby("Date")["Total Stake"].sum().reset_index()
    total_df["Change in Stake"] = total_df["Total Stake"].diff()

    chart_df["nonzero_lst"] = chart_df.Amount.apply(lambda x: 1 if x > 0 else 0)
    chart_df = (
        chart_df[chart_df["Amount"] >= 0.1]
        .groupby(["Date", "Token Name"])
        .agg(
            Symbol=("Symbol", "first"),
            Total_LST_Amount=("Amount", "sum"),
            Avg_LST_Amount=("Amount", "mean"),
            # Avg_LST_Amount_NonZero=("Amount", nonzero_mean),
            Total_Holders=("Address", "nunique"),
            # Total_Holders_NonZero=("nonzero_lst", "sum"),
            Total_SOL_Stake=("Total Stake", "sum"),
            Avg_SOL_Stake=("Total Stake", "mean"),
        )
        .reset_index()
    )
    rank = (
        chart_df.groupby("Token Name")["Total_LST_Amount"]
        .mean()
        .sort_values(ascending=False)
        .rank()
        .to_dict()
    )

    if lst != "All LSTs":
        chart_df_ = chart_df[chart_df["Token Name"] == lst]
    else:
        chart_df_ = chart_df

    rank_str = str({k: int(v) for k, v in rank.items()})
    legend_selection = alt.selection_point(fields=["Token Name"], bind="legend")
    stack = "normalize" if normalize else True
    if chart_type == "Area":
        base = (
            alt.Chart(chart_df_, title=title)
            .transform_calculate(order=f"{rank_str}[datum['Token Name']]")
            .mark_area(interpolate="monotone")
        )
    elif chart_type == "Line":
        base = (
            alt.Chart(chart_df_, title=title)
            .transform_calculate(order=f"{rank_str}[datum['Token Name']]")
            .mark_line(point=True)
        )
        stack = False if not normalize else "normalize"
    chart = base.encode(
        x=alt.X("yearmonthdate(Date):T", title="Date"),
        y=alt.Y(
            "Total_LST_Amount",
            title="Total LST Balance",
            stack=stack,
        ),
        color=alt.Color(
            "Token Name",
            sort=alt.SortField("order", "descending"),
            scale=alt.Scale(domain=[x[1] for x in utils.liquid_staking_tokens.values()], scheme="category10"),
        ),
        order="order:O",
        tooltip=[alt.Tooltip("yearmonthdate(Date):T", title="Date")]
        + [
            alt.Tooltip(
                x,
                title=x.replace("_", " "),
                format=",.1f"
                if x
                not in [
                    "Token Name",
                    "Symbol",
                    "Total_Holders",
                    # "Total_Holders_NonZero",
                ]
                else "",
            )
            for x in chart_df_.columns.drop("Date")
        ],
        opacity=alt.condition(legend_selection, alt.value(1), alt.value(0.1)),
    ).add_params(legend_selection)
    if include_total_stake:
        if include_total_stake == "Change from previous day":
            yval = alt.Y(
                "Change in Stake", title="Daily Change in Total Stake (SOL)", scale=alt.Scale(zero=False)
            )
        else:
            yval = alt.Y("Total Stake", title="Stake by all Top Stakers (SOL)", scale=alt.Scale(zero=False))
        total = (
            alt.Chart(total_df)
            .mark_line(color="#983832", point=alt.OverlayMarkDef(fill="#983832", color="#FD5E53", size=50))
            .encode(
                x=alt.X("yearmonthdate(Date):T", title="Date"),
                y=yval,
                tooltip=[
                    alt.Tooltip("yearmonthdate(Date):T", title="Date"),
                    alt.Tooltip("Total Stake", title="Total Stake (SOL)", format=",.0f"),
                    alt.Tooltip("Change in Stake", title="Daily Change in Total Stake (SOL)", format=",.0f"),
                ],
            )
        )
        chart = alt.layer(chart, total).resolve_scale(y="independent")
    if interactive is not None:
        bind_x = False if interactive == "y-axis" else True
        bind_y = False if interactive == "x-axis" else True
        chart = chart.interactive(bind_x=bind_x, bind_y=bind_y)
    chart = chart.properties(height=800, width=800)
    return chart, chart_df
