"""Global settings for the project.

This module contains global configurations.
It should be imported and run at the start of the project to ensure consistent settings across all modules.
"""

# import warnings

# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from pandas.plotting import register_matplotlib_converters


def configure_global_settings() -> None:
    """Configure global settings."""
    pass
    # from langchain_community.cache import InMemoryCache
    # from langchain.globals import set_llm_cache

    # set_llm_cache(InMemoryCache())

    # # Warning
    # warnings.filterwarnings("ignore")

    # # Matplotlib settings
    # register_matplotlib_converters()
    # # plt.rc('font', family='NanumGothic')
    # plt.rc("font", family="DejaVu Sans")
    # plt.rc("axes", unicode_minus=False)
    # plt.rc("font", size=20)
    # plt.rc("figure", titlesize=40, titleweight="bold")
    # plt.style.use("ggplot")

    # # Numpy settings
    # np.set_printoptions(
    #     suppress=True,
    #     precision=6,
    #     edgeitems=20,
    #     linewidth=100,
    #     formatter={"float": lambda x: "{:.3f}".format(x)},
    # )

    # # Pandas settings
    # pd.set_option("display.max_rows", 1000)
    # pd.set_option("display.max_columns", 1000)
    # pd.set_option("display.max_colwidth", 1000)
    # pd.set_option("display.width", 1000)
    # pd.set_option("display.float_format", "{:.2f}".format)


# Optional: Add a function to reset to default settings if needed
# def reset_to_default() -> None:
#     """Reset to default settings."""
#     plt.rcdefaults()
#     np.set_printoptions()
#     pd.reset_option("^display")
