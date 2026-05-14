import pandas as pd
from pathlib import Path
p = Path('pc_data.csv')
print('exists', p.exists())
if p.exists():
    df = pd.read_csv(p)
    print('shape', df.shape)
    print('columns', list(df.columns))
    print(df.head(3).to_dict(orient='records'))
