# ============================================================================ #
# START
# ============================================================================ #

# ============================================================================ #
# 1.0 Load

# Import libraries
import pandas as pd
import janitor as jr
import valdezds as vds

vds.getwd() # Confirm working directory

# Display set for terminal
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Read data
df = pd.read_csv("https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-03-15/cran.csv").clean_names()

# Clipboard
df.to_clipboard(index=False)
jr.shuffle(df, random_state=9432).to_clipboard(index=False)

# EDA
df.info()
jr.get_dupes(df)
df.isnull().sum()


# ============================================================================ #
# 2.0 Data Wrangling
# ============================================================================ #

# ============================================================================ #
# 2.1 Python
# ============================================================================ #

def dataCnv(src):
    return pd.to_datetime(src)

df["date_time"] = df.date.apply(dataCnv)


df["format"] = 1
df["date"][:1]

df.date.filter(regex="^[0-9][^a-zA-Z_]")
# https://stackoverflow.com/questions/26596297/regex-not-beginning-with-number

# In progress


(
    df.query("date.notnull() and package.str.contains('ggplot')")
    .assign(year = df["date"].dt.year)
)

# ============================================================================ #
# 2.1.1 Save to CSV


# ============================================================================ #
# 2.2 SQL
# ============================================================================ #

# Package
from pandasql import sqldf
pysqldf = lambda q: sqldf(q, globals()) # Quicker to write query

q = """
    ;
    """

pysqldf(q)


# ============================================================================ #
# 3.0 Plot
# ============================================================================ #

# ============================================================================ #
# 3.1 Plotnine
# ============================================================================ #

# ============================================================================ #
# 3.2 Tableau
# ============================================================================ #



# ============================================================================ #
# END
# ============================================================================ #
