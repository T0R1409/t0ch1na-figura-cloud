"""Build T-Zero Auto Figura IP for the verified full support matrix."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().with_name('build_all.py')), run_name='__main__')
