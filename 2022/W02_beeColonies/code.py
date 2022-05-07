# ============================================================================ #
# START
# ============================================================================ #

# ============================================================================ #
# 1.0 Load Packages and data

# Import libraries
import pandas as pd
import janitor as jr
import valdezds as vds
import plotnine as p9

# Read data
colony = pd.read_csv('https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-01-11/colony.csv')
stressor = pd.read_csv('https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-01-11/stressor.csv')

# Work with colony only, so store it in df variable
df = colony.copy()

# Quick EDA
df.info()
df.shape
df.isnull().sum()
vds.view_index(df)

# Clipboard
df.to_clipboard(index=False)
jr.shuffle(df, random_state=1).to_clipboard(index=False)


# ============================================================================ #
# 2.0 Data Wrangling
# ============================================================================ #

# ============================================================================ #
# 2.1 Python

# Top 10
state_tbl = (df.pipe(vds.select_by_number, 2, 5)
                .groupby(["state"])
                .agg(bee_mean = ("colony_lost", "mean"))
                .reset_index()
                .sort_values("bee_mean", ascending=False)
                .query("~state.str.contains('United States')")
                .head(10)
                .assign(state = lambda x: x["state"].astype("category"))
                # .assign(sep = lambda x: ["{:,.0f}".format(x) for x in x["bee_mean"]])
            )

# Save to csv (Tableau)
state_tbl.to_csv("2022/W02_beeColonies/data_beeColonies.csv", index=False)

# ============================================================================ #
# 2.2 SQL

# Package
from pandasql import sqldf
pysqldf = lambda q: sqldf(q, globals()) # Quicker to write query

# Top 10
q = """
    SELECT
        state
        , AVG(colony_lost) AS bee_mean
    
    FROM df
    
        WHERE 1=1
            AND state NOT LIKE '%United States%'
            
        GROUP BY 1
        ORDER BY bee_mean DESC
        LIMIT 10
    ;
    """

pysqldf(q)


# ============================================================================ #
# 3.0 Plot

# Ommit

# def scale_comma_sep(data, c):
#     df = data.copy()
#     df[c] = df[c].apply(lambda x: '{:,.0f}'.format(x))
    
#     return df[c]

# scale_comma_sep(state_tbl, "bee_mean")


(p9.ggplot(state_tbl)
 + p9.aes(x = "reorder(state, bee_mean)", y = "bee_mean")
 + p9.geom_col(alpha = 0.8)
 + p9.coord_flip()
 + p9.scale_y_continuous(breaks = [25000,50000,75000,100000],
                      labels = ["25,000", "50,000", "75,000", "100,000"])
 + p9.watermark("./iconvaldezdata.png")
 + p9.labs(
     x = "",
     y = "",
     title = "Mean Colony Lost - First time using plotnine"
 )
)

# Seems there's no captions or subtitles for plotnine

# Tableau:
# https://public.tableau.com/views/TidyTuesdayW02_beeColonies/TidyTuesdayW02_beeColonies?:language=en-US&:display_count=n&:origin=viz_share_link


# ============================================================================ #
# END
# ============================================================================ #
