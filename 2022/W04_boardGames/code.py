# ============================================================================ #
# START
# ============================================================================ #

# ============================================================================ #
# 1.0 Load

# Import libraries
import pandas as pd
import numpy as np
import janitor as jr
import valdezds as vds
import plotnine as p9

# Display set for terminal
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Read data
ratings = pd.read_csv('https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-01-25/ratings.csv').clean_names()
details = pd.read_csv('https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-01-25/details.csv').clean_names()

# Merge by id
df = pd.merge(ratings, details, how="left", on="id", suffixes=("_ratings", "_details"))

# Quick EDA
df.info()
df.shape
df.isnull().sum()
vds.view_index(df)
df.pipe(vds.select_by_number, 2, 7, 5, 6, 15).describe()

# Clipboard
df.to_clipboard(index=False)
jr.shuffle(df, random_state=1).to_clipboard(index=False)

# ============================================================================ #
# 2.0 Data Wrangling
# ============================================================================ #

# ============================================================================ #
# 2.1 Python
# ============================================================================ #

# https://stackoverflow.com/questions/72134067/filtering-after-grouped-pandas-dataframe-by-two-or-more-conditions-in-python

# ============================================================================ #
# 2.1.1 Filtering after grouped pandas multiple options

# First approach
dta = df.pipe(vds.select_by_number, 2, 7, 5, 6, 15)

avgs = (dta.query("maxplayers <= 4 and maxplayers != 0")
        .groupby(["maxplayers"])
        .agg(minavg=("average", np.min), maxavg=("average", np.max))
        .unstack()
        .reset_index(0, drop=True)
        .drop_duplicates()
        .reset_index()
        )

avgs.columns = ["maxplayers", "average"]

dta = (pd.merge(dta, avgs, on=["maxplayers", "average"])
       .sort_values(["maxplayers", "average"])
       )


# Second approach -- Using this one
df_players = (df.pipe(vds.select_by_number, 2, 7, 5, 6, 15)
                .groupby("maxplayers")
                .apply(lambda x: x.assign(avg_min=min(x["average"]), avg_max=max(x["average"])))
                .reset_index(drop=True)
                .query("average == avg_min or average == avg_max")
                .query("maxplayers <= 4 and maxplayers != 0")
                .sort_values(["maxplayers", "average"])
              )



# Third approach
grouped = df.groupby('maxplayers').average
cond1 = df.average.eq(grouped.transform(
    'min')) | df.average.eq(grouped.transform('max'))
cond2 = df.maxplayers.between(0, 4)  # a simpler interpretation

df.loc[cond1 & cond2].sort_values(['maxplayers', 'average'])


# ============================================================================ #
# 2.1.2 Python iterator

# How to Create a column with repeating values pandas (mismatching indexes)
# https://stackoverflow.com/questions/50804427/how-to-create-a-column-with-repeating-values-pandas-mismatching-indexes

# Repeating section
lista = ["Worst", "Best"]
list_iterator = lista * int(len(df_players)/len(lista))
df_players["best_worst"] = list_iterator


# ============================================================================ #
# 2.1.3 Pivot Longer -- Using pyjanitor package

df_players = (df_players.remove_columns(column_names=["avg_min", "avg_max"])
        .reorder_columns(["name", "best_worst", "maxplayers"])
        .change_type(["maxplayers", "name"], dtype=object)
        .pivot_longer(index = slice("name", "users_rated"),
                  column_names = slice("average", "bayes_average"),
                  names_to = "type",
                  values_to = "value"
                  )
    )

# Filter best and worst data frames
df_best = (df_players.query("best_worst == 'Best'").sort_values("maxplayers"))
df_worst = (df_players.query("best_worst == 'Worst'").sort_values("maxplayers"))


# ============================================================================ #
# 2.2 SQL
# ============================================================================ #


# Package
from pandasql import sqldf
pysqldf = lambda q: sqldf(q, globals()) # Quicker to write query

q = """
    WITH cte_data AS
    (
        SELECT
            name
            , users_rated
            , average
            , bayes_average
            , maxplayers
            , MIN(average) OVER(PARTITION BY maxplayers) AS avg_min
            , MAX(average) OVER(PARTITION BY maxplayers) AS avg_max
    
        FROM df
    )
    
    SELECT
        *
    
    FROM cte_data
        WHERE 1=1
            AND (average = avg_min OR average = avg_max)
            AND (maxplayers <= 4 AND maxplayers != 0)
        ORDER BY maxplayers, average
    ;
    """

pysqldf(q)


# ============================================================================ #
# 3.0 Plot



# ============================================================================ #
# END
# ============================================================================ #



