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
import plydata.cat_tools as cat
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


# Second approach -- USING THIS ONE
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
              .pivot_longer(index=slice("name", "users_rated"),
                            column_names=slice("average", "bayes_average"),
                            names_to="type",
                            values_to="value"
                            )
              )

# ============================================================================ #
# 2.1.4 Filtering Best and Worst Data Frames

# https://www.business-science.io/python/2021/06/22/plotnine-correlation-plot.html?mc_cid=54d1c6a0bd&mc_eid=f599f6e014

# Best
df_best = (df_players.query("best_worst == 'Best'")
           .sort_values("maxplayers")
           .assign(name = lambda x: x["name"] + " | Max Players | " + x["maxplayers"].astype(str))
           .assign(name = lambda x: cat.cat_inorder(x["name"]))
           )

# Save to csv (Tableau)
df_best.to_csv("2022/W04_boardGames/data_bestBoardGames.csv", index=False)


# Worst
df_worst = (df_players.query("best_worst == 'Worst'")
            .sort_values("maxplayers")
            .assign(name = lambda x: x["name"] + " | Max Players | " + x["maxplayers"].astype(str))
            .assign(name = lambda x: cat.cat_inorder(x["name"]))
            )

# Save to csv (Tableau)
df_worst.to_csv("2022/W04_boardGames/data_worstBoardGames.csv", index=False)


# ============================================================================ #
# 2.2 SQL
# ============================================================================ #

# Package
from pandasql import sqldf
pysqldf = lambda q: sqldf(q, globals()) # Quicker to write query

q = """

    /* Doing partition by for min and max averages */
    
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
    
    /* Filtering avg min and avg max */
    
    , cte_min_max AS
    (
        SELECT
            *
    
        FROM cte_data
            WHERE 1=1
                AND (average = avg_min OR average = avg_max)
                AND (maxplayers <= 4 AND maxplayers != 0)
            ORDER BY maxplayers, average
    )
    
    /* Create column with "repeating values" */
    
    , cte_bs AS
    (
        SELECT
            *
            , CASE
                WHEN avg_min = average
                THEN 'Worst'
                ELSE 'Best'
                END AS best_worst
    
        FROM cte_min_max
    )
    
    /* Because in SQLite there's no Pivot|Unpivot function, use UNION ALL */
    
    SELECT
        name
        , best_worst
        , maxplayers
        , users_rated
        , 'average' AS type
        , average AS value
    
    FROM cte_bs
    UNION ALL
    
    SELECT
        name
        , best_worst
        , maxplayers
        , users_rated
        , 'bayes_average'
        , bayes_average
    
    FROM cte_bs
    ;
    
    /* Final step is to filter by best and worst with WHERE clause */
    /* No need to do it. Using python data frames instead */
    /* I'll be using pandas data frames for plots */
    
    """

pysqldf(q)


# ============================================================================ #
# 3.0 Plot
# ============================================================================ #

# ============================================================================ #
# 3.1 Best Rated Games

(p9.ggplot(
    mapping=p9.aes(x="name", y="value", fill="type"),
    data=df_best) +

    # geoms
    p9.geom_col(position=p9.position_dodge(0.7),
                width=0.3,
                alpha=0.8) +
    p9.facet_wrap("name", nrow=2, scales="free_x") +
    p9.scale_fill_manual(["#58ecf1", "#12b16f"]) +
    p9.scale_y_continuous(limits=[0, 10], breaks=[0, 4, 8]) +
    p9.guides(fill=p9.guide_legend(title="Rating\n")) +

    # labs
    p9.labs(x="",
            y="Average Rating\n",
            title="Best Board Games By Rating") +

    # theme
    p9.theme(
        subplots_adjust={'hspace': 0.25},
        legend_position="bottom",
        legend_title_align="center",
        legend_title=p9.element_text(face="bold"),
        legend_text=p9.element_text(face="italic"),
        rect=p9.element_rect(fill="#cee9ff"),
        plot_title=p9.element_text(face="bold", size=15),
        plot_background=p9.element_rect(fill="#cee9ff", color=None),
        panel_background=p9.element_rect(fill="#cee9ff", color=None),
        panel_border=p9.element_blank(),
        panel_spacing=0.25,
        panel_grid_major_y=p9.element_line(color="#bfbfbf"),
        panel_grid_minor_y=p9.element_blank(),
        panel_grid_major_x=p9.element_line(color="#bfbfbf"),
        panel_grid_minor_x=p9.element_blank(),
        axis_text_y=p9.element_text(face="italic", size=12),
        axis_text_x=p9.element_blank(),
        axis_title_y=p9.element_text(face="bold"),
        axis_title_x=p9.element_text(face="bold"),
        strip_background=p9.element_rect(fill="#b8e3ff"),
        strip_text_x=p9.element_text(face="bold", size=10)) +
    
    # watermark
    p9.watermark("./vdicon.png", xo=25, yo=15)
)

# ============================================================================ #
# 3.2 Worst Rated Games

(p9.ggplot(
    mapping=p9.aes(x="name", y="value", fill="type"),
    data=df_worst) +

    # geoms
    p9.geom_col(position=p9.position_dodge(0.7),
                width=0.3,
                alpha=0.8) +
    p9.facet_wrap("name", nrow=2, scales="free_x") +
    p9.scale_fill_manual(["#b96d16", "#6e4225ab"]) +
    p9.scale_y_continuous(limits=[0, 10], breaks=[0, 4, 8]) +
    p9.guides(fill=p9.guide_legend(title="Rating\n")) +

    # labs
    p9.labs(x="",
            y="Average Rating\n",
            title="Worst Board Games By Rating") +

    # theme
    p9.theme(
        subplots_adjust={'hspace': 0.25},
        legend_position="bottom",
        legend_title_align="center",
        legend_title=p9.element_text(face="bold"),
        legend_text=p9.element_text(face="italic"),
        rect=p9.element_rect(fill="#ffd5ce"),
        plot_title=p9.element_text(face="bold", size=15),
        plot_background=p9.element_rect(fill="#ffd5ce", color=None),
        panel_background=p9.element_rect(fill="#ffd5ce", color=None),
        panel_border=p9.element_blank(),
        panel_spacing=0.25,
        panel_grid_major_y=p9.element_line(color="#bfbfbf"),
        panel_grid_minor_y=p9.element_blank(),
        panel_grid_major_x=p9.element_line(color="#bfbfbf"),
        panel_grid_minor_x=p9.element_blank(),
        axis_text_y=p9.element_text(face="italic", size=12),
        axis_text_x=p9.element_blank(),
        axis_title_y=p9.element_text(face="bold"),
        axis_title_x=p9.element_text(face="bold"),
        strip_background=p9.element_rect(fill="#ffc1b5"),
        strip_text_x=p9.element_text(face="bold", size=10)) +
    
    # watermark
    p9.watermark("./vdicon.png", xo=25, yo=15)
)

# Tableau
# https://public.tableau.com/app/profile/omar.valdez/viz/TidyTuesdayW04_boardGames/BestBoardGamesByRating

# ============================================================================ #
# END
# ============================================================================ #



