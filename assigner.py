import pandas as pd
from typing import List, Dict, Tuple

def assign(from_data: pd.DataFrame, pick=1) -> Dict[str, List[Tuple[str, int]]]:
  df = from_data.copy()
  mapping: Dict[str, List[Tuple[str, int]]] = {}
  for i in range(1, len(df.columns) + 1):
    filtered_df: pd.DataFrame = df.loc[:, (df == i).any()]
    for project in filtered_df.columns:
      project_df: pd.Series = filtered_df[filtered_df[project] == i][project]
      random_pick = project_df
      if project_df.shape[0] >= pick:
        random_pick = project_df.sample(n=pick)
        df.drop(project, axis=1, inplace=True)
      df.drop(index=random_pick.index, inplace=True)
      selections = list(zip(random_pick.index.to_numpy(), random_pick.to_numpy()))
      if mapping.get(project) is None:
        mapping[project] = selections
      else:
        mapping[project] += selections
      filtered_df: pd.DataFrame = df.loc[:, (df == i).any()]
  return mapping
    