"""Run the notebook's chart cell using a small local dataset."""
import json
from pathlib import Path
import re
from unittest.mock import patch

import pandas as pd
import plotly
from plotly.offline import get_plotlyjs

root = Path(__file__).resolve().parents[1]
notebook = json.loads(next(root.rglob('*.ipynb')).read_text())
cells = [''.join(cell.get('source', [])) for cell in notebook['cells']]
version = re.search(r'plotly==([0-9.]+)', '\n'.join(cells)).group(1)
assert plotly.__version__ == version
bundle_version = re.search(r'plotly.js v([0-9.]+)', get_plotlyjs()).group(1)
assert tuple(map(int, bundle_version.split('.'))) >= (2, 25, 2)
frame = pd.DataFrame({'Code': ['CA', 'NY'], 'State': ['California', 'New York'],
                      'DecamillionairesPer10000People': [8., 5.],
                      'Decamillionaires': [1000, 500], 'Total Wealth': [10000, 5000],
                      'Population': [100000, 100000]})
namespace = {'df': frame}
chart = next(cell for cell in cells if 'px.choropleth(' in cell)
with patch('plotly.basedatatypes.BaseFigure.show'):
    exec(compile(chart, 'notebook-chart', 'exec'), namespace)
figure = namespace['fig']
assert len(figure.data) == 3
assert list(figure.data[0].locations) == ['CA', 'NY']
assert figure.layout.geo.scope == 'usa'
assert len(figure.to_json()) > 1000
print('Notebook choropleth and annotations passed with Plotly ' + version + ' / Plotly.js ' + bundle_version)
