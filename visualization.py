import pandas as pd
import sqlite3
from datetime import datetime
import os
import csv
from jinja2 import Template


def create_comparison_table(df):
    print("Original DataFrame:")
    print(df.head())
    print("\nDataFrame info:")
    print(df.info())

    # Sort the dataframe by profile_url and date_time
    df_sorted = df.sort_values(["profile_url", "date_time"])

    # Group by profile_url and compute the changes using shift
    df_sorted["prev_interests_count"] = df_sorted.groupby("profile_url")[
        "interests_count"
    ].shift(1)
    df_sorted["prev_skills_count"] = df_sorted.groupby("profile_url")[
        "skills_count"
    ].shift(1)

    # Calculate changes
    df_sorted["interests_change"] = (
        df_sorted["interests_count"] - df_sorted["prev_interests_count"]
    )
    df_sorted["skills_change"] = (
        df_sorted["skills_count"] - df_sorted["prev_skills_count"]
    )

    # Keep only the latest records per profile where previous data exists
    latest_df = df_sorted.dropna(subset=["prev_interests_count", "prev_skills_count"])

    print("\nLatest Data with Changes:")
    print(latest_df.head())

    # Prepare data for the table
    table_data = []
    for _, row in latest_df.iterrows():
        interests_change = row["interests_change"]
        skills_change = row["skills_change"]

        # Create visual indicators for changes
        interests_indicator = (
            "▲" if interests_change > 0 else "▼" if interests_change < 0 else ""
        )
        skills_indicator = (
            "▲" if skills_change > 0 else "▼" if skills_change < 0 else ""
        )

        # Store the URL as plain text
        profile_url = row["profile_url"]

        table_data.append(
            {
                "profile_url": profile_url,
                "interests_count": int(row["interests_count"]),
                "interests_change": f"{interests_change:+g} {interests_indicator}",
                "skills_count": int(row["skills_count"]),
                "skills_change": f"{skills_change:+g} {skills_indicator}",
            }
        )

    # HTML template
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LinkedIn Profile Data Comparison</title>
        <style>
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f3f2ef;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background-color: #fff;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                padding: 20px;
            }
            h1 {
                text-align: center;
                color: #0a66c2;
                margin-bottom: 30px;
            }
            table {
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
            }
            th, td {
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #e0e0e0;
            }
            th {
                background-color: #0a66c2;
                color: white;
                font-weight: 600;
                text-transform: uppercase;
                font-size: 0.9em;
                letter-spacing: 0.5px;
            }
            tr:hover {
                background-color: #f5f5f5;
            }
            .positive { color: #0a8f0a; }
            .negative { color: #cf0000; }
            a {
                color: #0a66c2;
                text-decoration: none;
                transition: color 0.3s ease;
            }
            a:hover {
                color: #004182;
                text-decoration: underline;
            }
            .change-indicator {
                display: inline-block;
                width: 0;
                height: 0;
                margin-left: 5px;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
            }
            .positive .change-indicator {
                border-bottom: 8px solid #0a8f0a;
            }
            .negative .change-indicator {
                border-top: 8px solid #cf0000;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>LinkedIn Profile Data Comparison</h1>
            <table>
                <thead>
                    <tr>
                        <th>Profile URL</th>
                        <th>Interests Count</th>
                        <th>Interests Change</th>
                        <th>Skills Count</th>
                        <th>Skills Change</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in table_data %}
                    <tr>
                        <td><a href="{{ row['profile_url'] }}" target="_blank">{{ row['profile_url'] }}</a></td>
                        <td>{{ row['interests_count'] }}</td>
                        <td class="{{ 'positive' if '▲' in row['interests_change'] else 'negative' if '▼' in row['interests_change'] else '' }}">
                            {{ row['interests_change'].replace('▲', '').replace('▼', '') }}
                            {% if '▲' in row['interests_change'] or '▼' in row['interests_change'] %}
                                <span class="change-indicator"></span>
                            {% endif %}
                        </td>
                        <td>{{ row['skills_count'] }}</td>
                        <td class="{{ 'positive' if '▲' in row['skills_change'] else 'negative' if '▼' in row['skills_change'] else '' }}">
                            {{ row['skills_change'].replace('▲', '').replace('▼', '') }}
                            {% if '▲' in row['skills_change'] or '▼' in row['skills_change'] %}
                                <span class="change-indicator"></span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    # Render the template
    template = Template(html_template)
    return template.render(table_data=table_data)


def save_comparison_table(df, directory="reports"):
    # Create the reports directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    # Generate filename with current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    html_filename = f"comparison_table_{current_date}.html"
    csv_filename = f"comparison_table_{current_date}.csv"
    html_filepath = os.path.join(directory, html_filename)
    csv_filepath = os.path.join(directory, csv_filename)

    # Create and save the static HTML
    html_content = create_comparison_table(df)
    with open(html_filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Comparison table saved as {html_filepath}")

    # Save CSV file
    latest_df = (
        df.sort_values(["profile_url", "date_time"])
        .groupby("profile_url")
        .last()
        .reset_index()
    )
    latest_df["interests_change"] = latest_df["interests_count"] - df.groupby(
        "profile_url"
    )["interests_count"].shift(1)
    latest_df["skills_change"] = latest_df["skills_count"] - df.groupby("profile_url")[
        "skills_count"
    ].shift(1)

    csv_data = latest_df[
        [
            "profile_url",
            "interests_count",
            "interests_change",
            "skills_count",
            "skills_change",
        ]
    ]
    csv_data.to_csv(csv_filepath, index=False, quoting=csv.QUOTE_ALL)
    print(f"CSV data saved as {csv_filepath}")


def get_data_from_db(db_path="linkedin_data.db"):
    try:
        conn = sqlite3.connect(db_path)
        query = """
        SELECT profile_url, date_time, interests_count, skills_count
        FROM profile_data
        ORDER BY date_time DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        print("Raw data from database:")
        print(df.head())
        print("\nData types before conversion:")
        print(df.dtypes)

        # Convert date_time to datetime
        df["date_time"] = pd.to_datetime(df["date_time"])

        # Ensure interests_count and skills_count are integers
        df["interests_count"] = df["interests_count"].astype(int)
        df["skills_count"] = df["skills_count"].astype(int)

        print("\nData after conversion:")
        print(df.head())
        print("\nData types after conversion:")
        print(df.dtypes)
        print("\nNull values in each column:")
        print(df.isnull().sum())
        return df
    except sqlite3.Error as e:
        print(f"An error occurred while connecting to the database: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    # Connect to the database and get the DataFrame
    df = get_data_from_db()

    # Save the comparison table
    save_comparison_table(df)
