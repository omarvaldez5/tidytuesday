# ============================================================================ #
# START
# ============================================================================ #

# ============================================================================ #
# 1.0 Load

# Import libraries
import pandas as pd
import janitor as jr
import re
import valdezds as vds

# Display set for terminal
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Read data
breed_rank_all = pd.read_csv("https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-02-01/breed_rank.csv").clean_names()
breed_traits = pd.read_csv("https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-02-01/breed_traits.csv").clean_names()

# Clipboard
breed_rank_all.to_clipboard(index=False)
jr.shuffle(breed_rank_all, random_state=1).to_clipboard(index=False)

breed_traits.to_clipboard(index=False)
jr.shuffle(breed_traits, random_state=1).to_clipboard(index=False)

# Quick EDA
vds.view_index(breed_traits)
breed_traits.pipe(vds.select_by_number, 0, 1, 2, 15, 13).describe()

# ============================================================================ #
# 2.0 Data Wrangling
# ============================================================================ #

# ============================================================================ #
# 2.1 Python
# ============================================================================ #

# Changing data type
breed_rank_all["breed"] = breed_rank_all["breed"].astype("str")
breed_traits["breed"] = breed_traits["breed"].astype("str")

# Removing whitespaces
breed_rank_all["breed"] = breed_rank_all["breed"].apply(lambda x: re.sub("\\s|’", "_", x))
breed_traits["breed"] = breed_traits["breed"].apply(lambda x: re.sub("\\s|’", "_", x))

# Ranking
breed_rank = (breed_rank_all.pivot_longer(index=["breed", "links", "image"],
                                          column_names=slice(
                                              "2013_rank", "2020_rank"),
                                          names_to="year",
                                          values_to="rank")
              .assign(year=lambda x: x["year"].str.extract("(\d+)"))
              .groupby(["breed"])
              .agg(median_rank=("rank", "median"))
              .assign(rank=lambda x: x["median_rank"].rank(method="dense", ascending=True))
              .reset_index()
              .sort_values("median_rank")
              .head(10)
              .remove_columns(["median_rank"])
              .merge(breed_rank_all[["breed", "image"]], how="left", on="breed")
              )

# Join breed rank with traits
df = (breed_rank.merge(breed_traits[["breed", "affectionate_with_family",
                                     "good_with_young_children",
                                     "barking_level",
                                     "shedding_level",
                                     "trainability_level"]],
                       how="left",
                       on="breed")
      .move(source="image", target="breed", position="before", axis=1)
      )


# ============================================================================ #
# 2.1.1 Save to CSV
df.to_csv("2022/W05_dogBreeds/data_dogBreeds.csv", index=False)


# ============================================================================ #
# 2.2 SQL
# ============================================================================ #

# Package
from pandasql import sqldf
pysqldf = lambda q: sqldf(q, globals()) # Quicker to write query

q = """

    /* ************************************************** */
    /* Clean datasets (For some reason I can't join without subquery) */
    /* ************************************************** */
    
    WITH cte_rank AS
    (
        SELECT
            REPLACE(breed, '\\s|’', '') AS clean_breed
            , *
        
        FROM breed_rank_all
    )
    , cte_trait AS
    (
        SELECT
            REPLACE(breed, '\\s|’', '') AS clean_breed
            , *
        
        FROM breed_traits
    )
    
    /* ************************************************** */
    /* Merging both to get total data */
    /* ************************************************** */
    
    , cte_total AS
    (
        SELECT
            *
        
        FROM cte_rank
            LEFT JOIN cte_trait
                USING(clean_breed)
    )
    
    /* ************************************************** */
    /* NOTES: */
    /* There's not pivot longer function and usually */
    /* the best way to solve this issue is by doing */
    /* UNION ALL. However, do I need to do that for all year */
    /* ranks? Somehow that's tedious. */
    /* Besides, I still can't figure out why I wasn't able to do a subquery */
    /* when joining both datasets */
    /* ************************************************** */
    ;
    """

pysqldf(q)


# ============================================================================ #
# 3.0 Plot
# ============================================================================ #

# There's no gt() package in python, moving into Tableau:
# Link:
# https://public.tableau.com/app/profile/omar.valdez/viz/TidyTuesdayW05_dogBreeds/Dashboard1



# ============================================================================ #
# END
# ============================================================================ #
