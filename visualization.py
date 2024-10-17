import pandas as pd
import plotly.graph_objects as go


def create_comparison_table(df):
    # Pivot the dataframe to have dates as columns
    pivot_df = df.pivot(
        index="profile_url",
        columns="date_time",
        values=["interests_count", "skills_count"],
    )

    # Calculate the changes
    changes = pivot_df.diff(axis=1).iloc[:, -2:]

    # Prepare data for the table
    table_data = []
    for profile in pivot_df.index:
        row = [profile]
        for metric in ["interests_count", "skills_count"]:
            current = pivot_df.loc[
                profile, (metric, pivot_df.columns.get_level_values(1)[-1])
            ]
            change = changes.loc[
                profile, (metric, changes.columns.get_level_values(1)[-1])
            ]
            row.extend([current, change])
        table_data.append(row)

    # Create the table
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=[
                        "Profile URL",
                        "Interests Count",
                        "Interests Change",
                        "Skills Count",
                        "Skills Change",
                    ],
                    fill_color="paleturquoise",
                    align="left",
                ),
                cells=dict(
                    values=[
                        [row[0] for row in table_data],
                        [row[1] for row in table_data],
                        [
                            f"{row[2]:+d}" if pd.notnull(row[2]) else ""
                            for row in table_data
                        ],
                        [row[3] for row in table_data],
                        [
                            f"{row[4]:+d}" if pd.notnull(row[4]) else ""
                            for row in table_data
                        ],
                    ],
                    fill_color=[
                        "white",
                        "white",
                        [
                            (
                                "red"
                                if pd.notnull(row[2]) and row[2] < 0
                                else (
                                    "green"
                                    if pd.notnull(row[2]) and row[2] > 0
                                    else "white"
                                )
                            )
                            for row in table_data
                        ],
                        "white",
                        [
                            (
                                "red"
                                if pd.notnull(row[4]) and row[4] < 0
                                else (
                                    "green"
                                    if pd.notnull(row[4]) and row[4] > 0
                                    else "white"
                                )
                            )
                            for row in table_data
                        ],
                    ],
                    align="left",
                ),
            )
        ]
    )

    fig.update_layout(title="LinkedIn Profile Data Comparison")
    return fig


def save_comparison_table(df, filename="comparison_table.html"):
    fig = create_comparison_table(df)
    fig.write_html(filename)
    print(f"Comparison table saved as {filename}")
