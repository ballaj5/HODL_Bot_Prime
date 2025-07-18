# src/dashboard/app.py
import dash
from dash import html, dcc, dash_table, Input, Output
import pandas as pd
import os
import json
import logging
# Use relative import for the performance tab
from .performance_tab import render_performance_tab

# ... (rest of the app.py code from the previous response)
# The logic inside this file was already correct, only the import needed fixing.
# Make sure the import line above is correct and the final line is app.run(...)