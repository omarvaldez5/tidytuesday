# ============================================================================ #
# START
# ============================================================================ #

# ============================================================================ #
# 1.0 Load

# Import libraries
import pandas as pd
import janitor as jr
import valdezds as vds
import plotnine as p9

vds.getwd() # Confirm working directory

# Display set for terminal
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Read data
df = pd.read_csv("https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-03-08/erasmus.csv").clean_names()
iso = pd.read_csv("https://raw.githubusercontent.com/BjnNowak/TidyTuesday/main/data/iso.csv", sep=";", encoding="latin1")

# Clipboard
df.to_clipboard(index=False)
jr.shuffle(df, random_state=190).to_clipboard(index=False)


# ============================================================================ #
# 2.0 Data Wrangling
# ============================================================================ #

# ============================================================================ #
# 2.1 Python
# ============================================================================ #

# Send data
sending_data = (df.case_when(
    df.participant_gender == "Female", df.participants,
    0,
    column_name="sending_female")
    .case_when(
        df.participant_gender == "Male", df.participants,
        0,
        column_name="sending_male")
    .groupby(["sending_country_code"])
    .agg(female_total=("sending_female", "sum"),
         male_total=("sending_male", "sum"),
         sending=("participants", "sum"))
    .reset_index()
    .merge(iso, how="left", left_on="sending_country_code", right_on="code")
    .sort_values("sending", ascending=False)
    .remove_columns(["sending_country_code"])
    .move(source="country_name", target="female_total", position="before", axis=1)
    .pivot_longer(
        index=["country_name", "sending", "code"],
        column_names=["female_total", "male_total"],
        names_to="female_or_male",
        values_to="count_sending")
    .head(30)
)

# Receiving data
receiving_data = (df.case_when(
    df.participant_gender == "Female", df.participants,
    0,
    column_name="receiving_female")
    .case_when(
        df.participant_gender == "Male", df.participants,
        0,
        column_name="receiving_male")
    .groupby(["receiving_country_code"])
    .agg(female_total=("receiving_female", "sum"),
         male_total=("receiving_male", "sum"),
         receiving=("participants", "sum"))
    .reset_index()
    .merge(iso, how="left", left_on="receiving_country_code", right_on="code")
    .sort_values("receiving", ascending=False)
    .remove_columns(["receiving_country_code"])
    .move(source="country_name", target="female_total", position="before", axis=1)
    .pivot_longer(
        index=["country_name", "receiving", "code"],
        column_names=["female_total", "male_total"],
        names_to="female_or_male",
        values_to="count_receiving")
    .head(30)
)

# Join both
exchange_tbl = (pd.merge(sending_data, receiving_data,
                         how="inner",
                         on="country_name",
                         suffixes=("_sending", "_receiving"))
                )

# ============================================================================ #
# 2.1.1 Save to CSV
exchange_tbl.to_csv("2022/W10_studentMobility/data_studentMobility.csv")


# ============================================================================ #
# 2.2 SQL
# ============================================================================ #

# Package
from pandasql import sqldf
pysqldf = lambda q: sqldf(q, globals()) # Quicker to write query


# Will create only sending data for SQL

q = """
    /* Sending Data */
    WITH cte_sendingdata AS
    (
    SELECT * FROM
    (
    SELECT
        sending_country_code
        , SUM(sending_female) AS female_total
        , SUM(sending_male) AS male_total
        , SUM(participants) AS sending
    
    FROM (
        SELECT
            *
            , CASE
                WHEN participant_gender = 'Female' THEN participants
                ELSE 0
                END AS sending_female
            , CASE
                WHEN participant_gender = 'Male' THEN participants
                ELSE 0
                END AS sending_male
        
        FROM df
    ) tt
        
    GROUP BY sending_country_code
    ) a
    
    LEFT JOIN iso b
        ON a.sending_country_code = b.code
    
    ORDER BY sending DESC
    )
    
    SELECT
        country_name
        , sending
        , code
        , 'female_total' AS female_or_male
        , female_total AS count_sending
        
    FROM cte_sendingdata
    UNION ALL
    
    SELECT
        country_name
        , sending
        , code
        , 'male_total' AS female_or_male
        , male_total AS count_sending
    
    FROM cte_sendingdata
    
    LIMIT 30
    ;
    """

pysqldf(q)



# ============================================================================ #
# 3.0 Plot
# ============================================================================ #

# ============================================================================ #
# 3.1 Plotnine
# ============================================================================ #

(
    p9.ggplot(
        data=exchange_tbl,
        mapping=p9.aes(y="reorder(country_name, receiving)")
    ) +
    p9.geom_segment(
        p9.aes(
            y="reorder(country_name, receiving)",
            yend="reorder(country_name, receiving)",
            x=0,
            xend="receiving"
        ),
        size=9,
        col="#0eac00",
        alpha=0.15
    )
)

# PlotnineError: "Parameters {'col'}, are not understood by either the geom, stat or layer."

# ============================================================================ #
# 3.2 Tableau
# ============================================================================ #

# Link:
# https://public.tableau.com/app/profile/omar.valdez/viz/TidyTuesdayW10_studentMobility/Sheet1

# ============================================================================ #
# END
# ============================================================================ #
