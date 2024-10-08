import pandas
import nfl_data_py
from .. import cache
from .. import sbowls


def _season_complete(df: pandas.DataFrame, cache_path: str) -> bool:
    sb_dates = sbowls.load_superbowl_dates(cache_path)
    sb_cands = pandas.to_datetime(df["gameday"]).isin(sb_dates).sum()
    complete = sb_cands > 0
    return complete


def get(
    seasons: list[int], cache_path: str = None, update_last_season: bool = False
) -> pandas.DataFrame:
    """
    Get schedules data for the list of seasons provided.
    If a cache path is provided, data will be read from the cache
    or stored in the cache if calling for the first time. Otherwise,
    data is loaded from the web source.

    Parameters
    ----------

    seasons : list[int]
        Seasons to get schedules data for

    cache_path : str = None
        Path to a directory where cache files are stored

    update_last_season : bool = False
        Whether cached seasons that are incomplete should be reloaded (i.e. after a new week has ended).

    Returns
    -------

        out : pandas.DataFrame

    Examples
    --------

        >>> schedules.get([2020, 2021, 2022], "path_to_cache/")
    """
    dfs = []
    if cache_path:
        mdata = cache.load_schedules_mdata(cache_path)
        dfs = []
        for season in seasons:
            from_cache = True
            if season in mdata:
                if not mdata[season] and update_last_season:
                    from_cache = False
            else:
                from_cache = False
            if from_cache:
                dfs.append(cache.load(cache_path, cache.fname_schedules(season)))
            else:
                df = nfl_data_py.import_schedules([season])
                if _season_complete(df, cache_path):
                    mdata[season] = True
                else:
                    mdata[season] = False
                cache.dump(df, cache_path, cache.fname_schedules(season))
                cache.dump_schedules_mdata(mdata, cache_path)
                dfs.append(df)

    else:
        for season in seasons:
            dfs.append(nfl_data_py.import_schedules([season]))
    return pandas.concat(dfs)
