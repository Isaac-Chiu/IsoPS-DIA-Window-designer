import dash
from dash import dcc, html, Input, Output, State, ctx
import pandas as pd
import plotly.graph_objects as go
import base64
import io
import plotly.express as px

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("IsoPS Window Designer"),

    dcc.Upload(
        id="upload-data",
        children=html.Button("Upload CSV", style={"margin-bottom": "20px"}),
        accept=".csv"
    ),

    dcc.Graph(
        id="scatter-plot",
        config={
            'editable': True,
            'edits': {'shapePosition': True},
            'modeBarButtonsToAdd': ['drawline', 'eraseshape']
        }
    ),

    html.Div([
        html.Button("Add Line", id="add-line-btn", n_clicks=0),
        dcc.Input(id="line-position", type="number", placeholder="Enter MZ position", debounce=True),
        html.Button("Remove Last Line", id="remove-line-btn", n_clicks=0),
        html.Button("Download Lines", id="download-lines-btn", n_clicks=0, style={"margin-left": "10px"}),
        html.Button("Precise Line Drag Mode", id="zoom-in-btn", n_clicks=0),
        html.Button("Reset Zoom", id="reset-zoom-btn", n_clicks=0),
        html.Button("Auto-Fill", id="auto-fill-btn", n_clicks=0),
        dcc.Input(id="max-region-width", type="number", value=10, placeholder="Max width between lines", debounce=True),
        dcc.Download(id="download-lines")
    ], style={"margin-bottom": "20px"}),

    html.Div(id="line-positions"),

    dcc.Store(id="lines", data=[]),
    dcc.Store(id="dataframe", data=None),
    dcc.Store(id="current-mode", data="normal"),
    dcc.Store(id="last-altered-line", data=None),
])


@app.callback(
    Output("dataframe", "data"),
    Output("lines", "data"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
)
def upload_file(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        try:
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
            initial_lines = []
            if 'Win_start' in df.columns:
                initial_lines = df['Win_start'].unique().tolist()
            return df.to_dict("records"), initial_lines
        except pd.errors.ParserError:
            return None, []
    return None, []


@app.callback(
    Output("scatter-plot", "figure", allow_duplicate=True),
    Output("current-mode", "data"),
    Input("zoom-in-btn", "n_clicks"),
    State("scatter-plot", "figure"),
    State("dataframe", "data"),
    State("lines", "data"),
    State("last-altered-line", "data"),  # Add this state
    prevent_initial_call=True
)
def zoom_in_for_precision(n_clicks, current_figure, dataframe, lines, last_altered_line):
    if dataframe is None or n_clicks == 0:
        return dash.no_update, dash.no_update

    df = pd.DataFrame(dataframe)
    mz_min = df["MZ"].min()
    mz_max = df["MZ"].max()

    # Determine center for zoom - prioritize last altered line if it exists
    if last_altered_line is not None:
        center = float(last_altered_line)
    elif lines and len(lines) > 0:
        # If we have lines but no recorded last altered line, use the last line
        center = float(lines[-1])
    elif 'layout' in current_figure and 'xaxis' in current_figure['layout'] and 'range' in current_figure['layout']['xaxis']:
        current_range = current_figure['layout']['xaxis']['range']
        center = (float(current_range[0]) + float(current_range[1])) / 2
    else:
        center = (mz_min + mz_max) / 2

    # Use a wider zoom span of 5 m/z units on each side as requested
    zoom_span = 10  # 5 m/z units on each side

    # Calculate zoom boundaries
    x_min = max(center - zoom_span, mz_min)
    x_max = min(center + zoom_span, mz_max)

    # Create a new figure based on the current one
    new_figure = dict(current_figure)

    # Ensure layout exists
    if 'layout' not in new_figure:
        new_figure['layout'] = {}

    # Update xaxis with wider zoom but keep the 0.5 tick spacing
    new_figure['layout']['xaxis'] = {
        'title': "MZ",
        'range': [x_min, x_max],  # ±5 m/z zoom
        'tick0': round(x_min * 2) / 2,  # Round to nearest 0.5
        'dtick': 0.5,  # Keep 0.5 unit ticks as requested
        'showgrid': True,
        'zeroline': False,
    }

    # Visually indicate we're in precision mode
    new_figure['layout']['title'] = "PRECISION MODE: Zoomed In for Enhanced Line Positioning"

    # Change drag mode to pan for easier adjustment
    new_figure['layout']['dragmode'] = 'pan'

    # Force a complete redraw with new ui revision
    new_figure['layout']['uirevision'] = f'precision-mode-{n_clicks}'

    return new_figure, "precision"


@app.callback(
    Output("scatter-plot", "figure", allow_duplicate=True),
    Output("current-mode", "data", allow_duplicate=True),  # Add this output
    Input("reset-zoom-btn", "n_clicks"),
    State("scatter-plot", "figure"),
    State("dataframe", "data"),
    prevent_initial_call=True
)
def reset_zoom(n_clicks, current_figure, dataframe):
    if dataframe is None or n_clicks == 0:
        return dash.no_update, dash.no_update

    df = pd.DataFrame(dataframe)
    mz_min = df["MZ"].min()
    mz_max = df["MZ"].max()
    rt_min = df["RT"].min()
    rt_max = df["RT"].max()

    # Add padding to y-axis
    y_range = rt_max - rt_min
    padding = 0.1 * y_range
    rt_min_padded = rt_min - padding
    rt_max_padded = rt_max + padding

    # Create a new figure based on the current one to ensure update
    new_figure = dict(current_figure)

    # Ensure layout exists
    if 'layout' not in new_figure:
        new_figure['layout'] = {}

    # Reset xaxis with optimized settings
    new_figure['layout']['xaxis'] = {
        'title': "MZ",
        'range': [mz_min, mz_max],  # Full range
        'tick0': 0,
        'dtick': 5,  # Wider ticks for better performance
        'showgrid': True,
        'zeroline': False,
    }

    # Reset yaxis
    new_figure['layout']['yaxis'] = {
        'title': "RT",
        'range': [rt_min_padded, rt_max_padded],
        'showgrid': True,
        'zeroline': False,
    }

    # Reset title
    new_figure['layout']['title'] = "Drag and add the isolation boundary"

    # Reset drag mode
    new_figure['layout']['dragmode'] = "zoom"

    # Force refresh
    new_figure['layout']['uirevision'] = f'normal-mode-{n_clicks}'

    return new_figure, "normal"


@app.callback(
    Output("lines", "data", allow_duplicate=True),
    Output("line-positions", "children", allow_duplicate=True),
    Output("last-altered-line", "data", allow_duplicate=True),
    Input("auto-fill-btn", "n_clicks"),
    State("lines", "data"),
    State("dataframe", "data"),
    State("max-region-width", "value"),
    prevent_initial_call=True
)
def auto_fill_empty_regions(n_clicks, lines, dataframe, max_width):
    if n_clicks == 0 or not lines or dataframe is None:
        return dash.no_update, dash.no_update, dash.no_update

    # Default max_width if none provided
    if max_width is None or max_width <= 0:
        max_width = 10  # Default to 10 if invalid value

    # Convert to float and sort lines
    sorted_lines = sorted([float(line) for line in lines])

    # Get dataframe
    df = pd.DataFrame(dataframe)

    # Get all m/z values from the dataframe
    all_mz_values = set()

    # Collect all m/z values across columns
    mz_columns = [col for col in df.columns if col.startswith("MZ") or col.lower().startswith("mz")]
    if not mz_columns:  # If no MZ columns found, use default names
        mz_columns = ["MZ", "MZp1", "MZp2"]

    for col in mz_columns:
        if col in df.columns:
            all_mz_values.update(df[col].dropna().tolist())

    print(f"Found {len(all_mz_values)} MZ values in columns: {mz_columns}")

    # Initialize new lines to add
    new_lines = []
    last_added = None

    # Process each pair of adjacent lines
    for i in range(len(sorted_lines) - 1):
        start = sorted_lines[i]
        end = sorted_lines[i + 1]
        region_width = end - start

        # Debug information
        print(f"Checking region {start} to {end}, width: {region_width}")

        # If the region is wider than the maximum width
        if region_width > max_width:
            # Check if there are any targets in this region
            targets_in_region = [mz for mz in all_mz_values if start < mz < end]
            target_count = len(targets_in_region)

            print(f"  Found {target_count} targets in region")

            # If no or very few targets, divide the region
            if target_count < 2:  # Allow for more lenient check
                # Calculate divisions - ensure at least one new line
                num_divisions = max(2, int(region_width / max_width) + 1)
                step = region_width / num_divisions

                print(f"  Adding {num_divisions - 1} dividing lines with step {step}")

                # Add lines at equal intervals
                for j in range(1, num_divisions):
                    new_line_pos = start + (j * step)
                    new_lines.append(new_line_pos)
                    last_added = new_line_pos
                    print(f"  Added line at {new_line_pos}")

    # If we didn't add any lines, no update is needed
    if not new_lines:
        print("No new lines were added")
        return dash.no_update, dash.no_update, dash.no_update

    # Add the new lines to the existing ones and sort
    updated_lines = sorted_lines + new_lines
    updated_lines.sort()

    print(f"Added {len(new_lines)} new lines, total lines: {len(updated_lines)}")

    # Create the updated text display
    line_text = f"Lines: {', '.join(f'{x:.2f}' for x in updated_lines)}" if updated_lines else "No lines added yet."

    return updated_lines, line_text, last_added

@app.callback(
    Output("scatter-plot", "figure"),
    Input("lines", "data"),
    Input("dataframe", "data"),
    State("current-mode", "data"),
    State("scatter-plot", "figure"),  # Remove the allow_duplicate parameter here
)
def update_plot(lines, dataframe, current_mode, current_figure):
    fig = go.Figure()

    if dataframe is None:
        fig.update_layout(title="Upload a CSV to get started")
        return fig

    df = pd.DataFrame(dataframe)

    # Create color palette
    if "Name" in df.columns:
        unique_names = df["Name"].unique()
        color_palette = {name: color for name, color in zip(unique_names, px.colors.qualitative.Set2)}
    else:
        color_palette = {}

    def get_opacity(type_value):
        return 0.5 if type_value == "Light" else 1.0

    # Add scatter traces
    scatter_traces = []
    for col in ["MZ", "MZp1", "MZp2"]:
        if col in df.columns:
            scatter_traces.append(
                go.Scatter(
                    x=df[col],
                    y=df["RT"],
                    mode="markers",
                    marker=dict(
                        size=8,
                        color=[color_palette.get(name, "gray") for name in
                               df["Name"]] if "Name" in df.columns else "gray",
                        opacity=[get_opacity(t) for t in df["Types"]] if "Types" in df.columns else 1.0,
                        showscale=False
                    ),
                    text=df["Name"] if "Name" in df.columns else None,
                    name=f"Scatter ({col})"
                )
            )

    fig.add_traces(scatter_traces)

    # Calculate y-axis range with padding
    y_min = df["RT"].min()
    y_max = df["RT"].max()
    y_range = y_max - y_min
    padding = 0.1 * y_range  # 10% padding
    y_min_padded = y_min - padding
    y_max_padded = y_max + padding

    # Add vertical lines with extended length
    if lines:
        shapes = []
        for i, line_pos in enumerate(lines):
            shapes.append({
                'type': 'line',
                'x0': line_pos,
                'x1': line_pos,
                'y0': y_min_padded,  # Extended below
                'y1': y_max_padded,  # Extended above
                'xref': 'x',
                'yref': 'y',
                'line': {
                    'color': 'grey',
                    'width': 1.2,
                },
            })
        fig.update_layout(shapes=shapes)

    # Base layout
    fig.update_layout(
        title="Drag and add the isolation boundary",
        xaxis={
            'title': "MZ",
            'tick0': 0,
            'dtick': 5,
            'showgrid': True,
            'zeroline': False,
        },
        yaxis={
            'title': "RT",
            'showgrid': True,
            'zeroline': False,
            'range': [y_min_padded, y_max_padded],  # Set padded range for y-axis
        },
        dragmode="zoom",
        showlegend=True,
        hovermode='closest'
    )

    if current_mode == "precision" and current_figure and 'layout' in current_figure:
        # If we're in precision mode, preserve the current x-axis range
        if 'xaxis' in current_figure['layout'] and 'range' in current_figure['layout']['xaxis']:
            fig.update_xaxes(range=current_figure['layout']['xaxis']['range'],
                             tick0=current_figure['layout']['xaxis'].get('tick0', 0),
                             dtick=current_figure['layout']['xaxis'].get('dtick', 0.5))
            fig.update_layout(
                dragmode='pan',
                title="PRECISION MODE: Zoomed In for Enhanced Line Positioning"
            )

    return fig


@app.callback(
    Output("lines", "data", allow_duplicate=True),
    Output("line-positions", "children"),
    Output("scatter-plot", "figure", allow_duplicate=True),
    Output("last-altered-line", "data"),
    Input("add-line-btn", "n_clicks"),
    Input("remove-line-btn", "n_clicks"),
    Input("scatter-plot", "relayoutData"),
    State("line-position", "value"),
    State("lines", "data"),
    State("dataframe", "data"),
    State("scatter-plot", "figure"),
    State("current-mode", "data"),
    State("last-altered-line", "data"),  # Add this state to access last altered line
    prevent_initial_call=True
)
def modify_and_update_lines(add_clicks, remove_clicks, relayout_data, line_position, lines, dataframe, current_figure,
                            current_mode, last_altered_line):
    # Original line handling logic
    if lines is None:
        lines = []

    # Create a copy of the current last_altered_line to retain its value if we don't update it
    new_last_altered = last_altered_line

    # Use a wider range for m/z positions (100-2000)
    min_mz = 100
    max_mz = 2000

    # If dataframe exists, get its actual range, but still enforce minimum of 100-2000
    if dataframe is not None:
        df = pd.DataFrame(dataframe)
        data_min = df["MZ"].min()
        data_max = df["MZ"].max()
        # Only use dataset bounds if they're wider than our default bounds
        min_mz = min(min_mz, data_min)
        max_mz = max(max_mz, data_max)

    if ctx.triggered_id == "add-line-btn" and line_position is not None:
        try:
            line_position = float(line_position)
            if min_mz <= line_position <= max_mz and line_position not in lines:
                lines.append(line_position)
                new_last_altered = line_position  # Set last altered to the new line
            else:
                return lines, f"Invalid line position. Please enter a value between {min_mz:.2f} and {max_mz:.2f}.", dash.no_update, new_last_altered
        except ValueError:
            return lines, "Invalid line position. Please enter a number.", dash.no_update, new_last_altered

    elif ctx.triggered_id == "remove-line-btn" and lines:
        if last_altered_line is not None and last_altered_line in lines:
            # Remove the last altered line
            lines.remove(last_altered_line)
            # Reset the last altered line since we just removed it
            new_last_altered = None
        else:
            # Fallback to removing the last line if last_altered is not in the list
            lines.pop()

    elif relayout_data:
        updated_lines = list(lines)
        for key, value in relayout_data.items():
            if key.startswith("shapes[") and key.endswith("].x0"):
                try:
                    index = int(key[7:key.find("]")])
                    line_pos = float(value)
                    if index < len(updated_lines):
                        updated_lines[index] = line_pos
                        new_last_altered = line_pos  # Set last altered to the dragged line
                except (ValueError, IndexError):
                    continue
        if updated_lines:
            lines = updated_lines

    lines.sort()
    line_text = f"Lines: {', '.join(f'{x:.2f}' for x in lines)}" if lines else "No lines added yet."

    # If we're in precision mode and have relayout data that's changing shape positions
    # we need to preserve the current zoom level
    if current_mode == "precision" and ctx.triggered_id == "scatter-plot" and relayout_data:
        # Check if this is a shape drag operation
        shape_keys = [k for k in relayout_data.keys() if k.startswith("shapes[") and (".x0" in k or ".x1" in k)]
        if shape_keys and current_figure and 'layout' in current_figure and 'xaxis' in current_figure['layout']:
            # This is a shape drag, so preserve the current zoom
            new_figure = dict(current_figure)
            # Ensure we keep the precision mode appearance
            new_figure['layout']['title'] = "PRECISION MODE: Zoomed In for Enhanced Line Positioning"
            new_figure['layout']['dragmode'] = 'pan'
            return lines, line_text, new_figure, new_last_altered

    # If it's not a shape drag or we're not in precision mode, don't update the figure
    return lines, line_text, dash.no_update, new_last_altered


@app.callback(
    Output("download-lines", "data"),
    Input("download-lines-btn", "n_clicks"),
    State("lines", "data"),
    State("dataframe", "data"),
    prevent_initial_call=True
)
@app.callback(
    Output("download-lines", "data", allow_duplicate=True),
    Input("download-lines-btn", "n_clicks"),
    State("lines", "data"),
    State("dataframe", "data"),
    prevent_initial_call=True
)
def download_lines(n_clicks, lines, dataframe):
    if not lines or dataframe is None:
        return dash.no_update

    # Sort the lines
    sorted_lines = sorted([float(l) for l in lines])

    # Create output dataframe with the required columns
    output_columns = [
        "Start", "End", "Name", "Types", "Charge", "RT", "MZ", "MZp1", "MZp2",
        "Round_start", "Round_end", "MZ-Round_start", "Round_end-MZp2"
    ]

    output_rows = []

    # Process each pair of adjacent lines to form windows
    if len(sorted_lines) >= 2:
        df = pd.DataFrame(dataframe)

        for i in range(len(sorted_lines) - 1):
            start = sorted_lines[i]
            end = sorted_lines[i + 1]

            # Round start and end to specific precision
            round_start = round(start * 2) / 2  # Rounds to nearest 0.5
            round_end = round(end * 2) / 2  # Rounds to nearest 0.5

            # Filter targets that fall within this window
            targets_in_window = df[(df["MZ"] >= start) & (df["MZ"] < end)]

            # If no targets, create an empty row for the window
            if len(targets_in_window) == 0:
                row = {
                    "Start": start,
                    "End": end,
                    "Name": "NA",
                    "Types": "NA",
                    "Charge": "NA",
                    "RT": "NA",
                    "MZ": "NA",
                    "MZp1": "NA",
                    "MZp2": "NA",
                    "Round_start": round_start,
                    "Round_end": round_end,
                    "MZ-Round_start": "NA",
                    "Round_end-MZp2": "NA"
                }
                output_rows.append(row)
            else:
                # For each target in the window, create a row
                for _, target in targets_in_window.iterrows():
                    # Extract target information
                    name = target.get("Name", "NA")
                    types = target.get("Types", "NA")
                    charge = target.get("Charge", "NA")
                    rt = target.get("RT", "NA")
                    mz = target.get("MZ", "NA")
                    mzp1 = target.get("MZp1", "NA")
                    mzp2 = target.get("MZp2", "NA")

                    # Calculate distances
                    mz_minus_round_start = "NA"
                    round_end_minus_mzp2 = "NA"

                    if mz != "NA" and round_start != "NA":
                        mz_minus_round_start = float(mz) - round_start

                    if mzp2 != "NA" and round_end != "NA":
                        round_end_minus_mzp2 = round_end - float(mzp2)

                    # Create row
                    row = {
                        "Start": start,
                        "End": end,
                        "Name": name,
                        "Types": types,
                        "Charge": charge,
                        "RT": rt,
                        "MZ": mz,
                        "MZp1": mzp1,
                        "MZp2": mzp2,
                        "Round_start": round_start,
                        "Round_end": round_end,
                        "MZ-Round_start": mz_minus_round_start,
                        "Round_end-MZp2": round_end_minus_mzp2
                    }
                    output_rows.append(row)

    # Create the final dataframe
    if output_rows:
        result_df = pd.DataFrame(output_rows)
        # Ensure columns are in the correct order
        result_df = result_df[output_columns]
    else:
        # If no windows, create an empty dataframe with the required columns
        result_df = pd.DataFrame(columns=output_columns)

    # Create CSV in memory and prepare for download
    return dcc.send_data_frame(result_df.to_csv, filename="isolation_windows.csv", index=False)


if __name__ == "__main__":
    app.run_server(debug=True)