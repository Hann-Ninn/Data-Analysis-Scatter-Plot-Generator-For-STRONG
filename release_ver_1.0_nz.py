import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, StringVar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import sys


class DataGroupSettings:
    def __init__(self):
        self.default_settings = {
            'DeltaX': {
                'y_min': 2,
                'y_max': 5,
                'ref_lines': [3.0, 4.0, 3.5],
                'ref_colors': ['red', 'red', 'orange'],
                'ref_styles': ['-', '-', '--'],
                'ref_labels': ['Ref Line 1', 'Ref Line 2', 'Ref Line 3'],
                'point_size': 15,
                'point_color': 'royalblue',
                'title_prefix': 'NoName',
                'file_prefix': 'NoName'
            },
            'DeltaY': {
                'y_min': -1,
                'y_max': 2,
                'ref_lines': [0.0, 1.0, 0.5],
                'ref_colors': ['red', 'red', 'orange'],
                'ref_styles': ['-', '-', '--'],
                'ref_labels': ['Ref Line 1', 'Ref Line 2', 'Ref Line 3'],
                'point_size': 15,
                'point_color': 'forestgreen',
                'title_prefix': 'NoName',
                'file_prefix': 'NoName'
            },
            'DeltaAngle': {
                'y_min': -1,
                'y_max': 5,
                'ref_lines': [0.0, 4.0],
                'ref_colors': ['green', 'green'],
                'ref_styles': ['-', '-'],
                'ref_labels': ['Min Value', 'Max Value'],
                'point_size': 15,
                'point_color': 'red',
                'title_prefix': 'NoName',
                'file_prefix': 'NoName'
            }
        }

        self.settings = {group: values.copy() for group, values in self.default_settings.items()}

    def get_setting(self, data_group, setting_name):
        return self.settings[data_group].get(setting_name)

    def update_setting(self, data_group, setting_name, value):
        if data_group in self.settings:
            self.settings[data_group][setting_name] = value


class ScatterPlotGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Analysis Scatter Plot Generator")
        self.root.geometry("1150x750")
        self.root.resizable(True, True)
        self.data_settings = DataGroupSettings()
        self.current_data_group = None
        self.station_var = tk.StringVar(value="both")
        self.preview_frame = None
        self.preview_fig = None
        self.current_preview = None
        self.tab_frames = {}
        self.y_min_vars = {}
        self.y_max_vars = {}
        self.ref_trees = {}
        self.point_size_vars = {}
        self.point_color_vars = {}
        self.title_prefix_vars = {}
        self.file_prefix_vars = {}
        self.point_size_displays = {}
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        settings_frame = ttk.LabelFrame(main_frame, text="Parameter Settings", padding="10")
        settings_frame.grid(row=0, column=0, sticky="nsw", padx=(0, 10))
        preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding="10")
        preview_frame.grid(row=0, column=1, sticky="nsew")
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.create_settings_ui(settings_frame)
        self.create_preview_ui(preview_frame)

        button_frame = ttk.Frame(settings_frame, padding="5")
        button_frame.grid(row=12, column=0, columnspan=3, pady=10)

        preview_btn = ttk.Button(button_frame, text="Preview", command=self.preview_plot)
        preview_btn.grid(row=0, column=0, padx=5)

        generate_btn = ttk.Button(button_frame, text="Generate", command=self.generate_plots)
        generate_btn.grid(row=0, column=1, padx=5)

        reset_btn = ttk.Button(button_frame, text="Reset", command=self.reset_settings)
        reset_btn.grid(row=0, column=2, padx=5)

        exit_btn = ttk.Button(button_frame, text="Exit", command=self.root.quit)
        exit_btn.grid(row=0, column=3, padx=5)

    def create_settings_ui(self, parent):
        file_frame = ttk.LabelFrame(parent, text="Data Source Settings")
        file_frame.grid(row=0, column=0, columnspan=3, sticky=tk.W + tk.E, pady=5)

        ttk.Label(file_frame, text="Excel file:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.file_path = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path, width=40)
        file_entry.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W + tk.E)
        ttk.Button(file_frame, text="Browse...", command=self.browse_file).grid(row=0, column=2, padx=5, pady=2)

        ttk.Label(file_frame, text="Save path:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.save_path = tk.StringVar(value=os.getcwd())
        save_entry = ttk.Entry(file_frame, textvariable=self.save_path, width=40)
        save_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W + tk.E)
        ttk.Button(file_frame, text="Browse...", command=self.browse_save_path).grid(row=1, column=2, padx=5, pady=2)

        ttk.Label(file_frame, text="Stations:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        station_combo = ttk.Combobox(file_frame, textvariable=self.station_var,
                                     values=["Station 1", "Station 2", "Both Stations"],
                                     state="readonly", width=20)
        station_combo.set("Both Stations")
        station_combo.grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)

        prefix_frame = ttk.LabelFrame(file_frame, text="Global Prefixes")
        prefix_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W + tk.E, pady=5)

        ttk.Label(prefix_frame, text="Title prefix:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.global_title_prefix = tk.StringVar(value="NoName")
        ttk.Entry(prefix_frame, textvariable=self.global_title_prefix,
                  width=25).grid(row=0, column=1, padx=5, pady=2, sticky=tk.W + tk.E)

        ttk.Label(prefix_frame, text="Filename prefix:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.global_file_prefix = tk.StringVar(value="NoName")
        ttk.Entry(prefix_frame, textvariable=self.global_file_prefix,
                  width=25).grid(row=1, column=1, padx=5, pady=2, sticky=tk.W + tk.E)

        data_frame = ttk.LabelFrame(parent, text="Select Data Groups")
        data_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W + tk.E, pady=5)

        self.data_group_var = StringVar(value="DeltaX")
        self.data_groups = ["DeltaX", "DeltaY", "DeltaAngle"]
        self.notebook = ttk.Notebook(data_frame)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        for group in self.data_groups:
            tab_frame = ttk.Frame(self.notebook, padding="5")
            self.notebook.add(tab_frame, text=group)
            self.tab_frames[group] = tab_frame
            tab_frame.columnconfigure(0, weight=1)
            tab_frame.rowconfigure(0, weight=1)
            prefix_frame = ttk.LabelFrame(tab_frame, text="Title and Filename Prefix")
            prefix_frame.grid(row=0, column=0, sticky=tk.W + tk.E, pady=5)
            range_frame = ttk.LabelFrame(tab_frame, text="Y-axis Range")
            range_frame.grid(row=0, column=0, sticky=tk.W + tk.E, pady=5)
            ttk.Label(range_frame, text="Minimum:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
            self.y_min_vars[group] = tk.StringVar(
                value=str(self.data_settings.get_setting(group, 'y_min')))
            ttk.Entry(range_frame, textvariable=self.y_min_vars[group], width=10).grid(row=0, column=1, padx=5, pady=2,
                                                                                       sticky=tk.W)
            ttk.Label(range_frame, text="Maximum:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
            self.y_max_vars[group] = tk.StringVar(
                value=str(self.data_settings.get_setting(group, 'y_max')))
            ttk.Entry(range_frame, textvariable=self.y_max_vars[group], width=10).grid(row=0, column=3, padx=5, pady=2,
                                                                                       sticky=tk.W)
            ref_frame = ttk.LabelFrame(tab_frame, text="Reference Lines")
            ref_frame.grid(row=2, column=0, sticky=tk.W + tk.E, pady=5)
            columns = ("Value", "Style", "Color", "Label")
            ref_tree = ttk.Treeview(ref_frame, columns=columns, show="headings", height=5)
            self.ref_trees[group] = ref_tree
            for col in columns:
                ref_tree.heading(col, text=col)
                ref_tree.column(col, width=110, anchor="center")
            ref_tree.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky=tk.W + tk.E)
            ref_lines = self.data_settings.get_setting(group, 'ref_lines') or []
            ref_colors = self.data_settings.get_setting(group, 'ref_colors') or []
            ref_styles = self.data_settings.get_setting(group, 'ref_styles') or []
            ref_labels = self.data_settings.get_setting(group, 'ref_labels') or []
            for i in range(len(ref_lines)):
                ref_tree.insert("", "end", values=(
                    ref_lines[i],
                    ref_styles[i] if i < len(ref_styles) else "-",
                    ref_colors[i] if i < len(ref_colors) else "red",
                    ref_labels[i] if i < len(ref_labels) else "Reference"
                ))

            btn_frame = ttk.Frame(ref_frame)
            btn_frame.grid(row=1, column=0, columnspan=4, sticky=tk.W + tk.E)

            ttk.Button(btn_frame, text="Add Line",
                       command=lambda g=group: self.add_ref_line(g)).grid(row=0, column=0, padx=2, pady=5)
            ttk.Button(btn_frame, text="Remove Line",
                       command=lambda g=group: self.remove_ref_line(g)).grid(row=0, column=1, padx=2, pady=5)
            ttk.Button(btn_frame, text="Edit Line",
                       command=lambda g=group: self.edit_ref_line(g)).grid(row=0, column=2, padx=2, pady=5)

            point_frame = ttk.LabelFrame(tab_frame, text="Point Settings")
            point_frame.grid(row=3, column=0, sticky=tk.W + tk.E, pady=5)

            ttk.Label(point_frame, text="Point size:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            self.point_size_vars[group] = tk.IntVar(
                value=self.data_settings.get_setting(group, 'point_size') or 15)
            ttk.Scale(point_frame, from_=10, to=40, orient=tk.HORIZONTAL,
                      variable=self.point_size_vars[group],
                      command=lambda v, g=group: self.update_point_size_display(g, v)).grid(row=0, column=1, padx=5,
                                                                                            pady=5)

            self.point_size_displays[group] = ttk.Label(point_frame, text=str(self.point_size_vars[group].get()))
            self.point_size_displays[group].grid(row=0, column=2, padx=5, pady=5)

            ttk.Label(point_frame, text="Point color:").grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
            point_colors = ["royalblue", "forestgreen", "red", "purple", "orange", "black"]
            self.point_color_vars[group] = tk.StringVar(
                value=self.data_settings.get_setting(group, 'point_color') or "royalblue")
            ttk.Combobox(point_frame, textvariable=self.point_color_vars[group],
                         values=point_colors, state="readonly", width=12).grid(row=0, column=4, padx=5, pady=5)

    def update_point_size_display(self, data_group, value):
        self.point_size_displays[data_group].config(text=str(round(float(value))))

    def add_ref_line(self, data_group):
        self.ref_trees[data_group].insert("", "end", values=(0.0, '-', 'red', 'Reference'))

    def edit_ref_line(self, data_group):
        ref_tree = self.ref_trees[data_group]
        selected = ref_tree.selection()
        if not selected:
            messagebox.showinfo("Warning", "Please select a reference line to edit.")
            return

        item = selected[0]
        values = ref_tree.item(item, "values")
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit Reference Line")
        edit_win.geometry("270x200")
        edit_win.resizable(False, False)

        row_idx = 0
        ttk.Label(edit_win, text="Value:").grid(row=row_idx, column=0, padx=10, pady=5, sticky='e')
        value_var = tk.StringVar(value=values[0])
        ttk.Entry(edit_win, textvariable=value_var, width=10).grid(row=row_idx, column=1, padx=10, pady=5, sticky='w')
        row_idx += 1
        ttk.Label(edit_win, text="Line Style:").grid(row=row_idx, column=0, padx=10, pady=5, sticky='e')
        style_var = tk.StringVar(value=values[1])
        styles = ['-', '--', '-.', ':']
        ttk.Combobox(edit_win, textvariable=style_var, values=styles, state="readonly", width=8).grid(
            row=row_idx, column=1, padx=10, pady=5, sticky='w')
        row_idx += 1
        ttk.Label(edit_win, text="Color:").grid(row=row_idx, column=0, padx=10, pady=5, sticky='e')
        color_var = tk.StringVar(value=values[2])
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'black', 'brown', 'pink', 'gray', 'cyan', 'magenta',
                  'yellow']
        ttk.Combobox(edit_win, textvariable=color_var, values=colors, state="readonly", width=10).grid(
            row=row_idx, column=1, padx=10, pady=5, sticky='w')
        row_idx += 1
        ttk.Label(edit_win, text="Label:").grid(row=row_idx, column=0, padx=10, pady=5, sticky='e')
        label_var = tk.StringVar(value=values[3])
        ttk.Entry(edit_win, textvariable=label_var, width=20).grid(row=row_idx, column=1, padx=10, pady=5, sticky='w')
        row_idx += 1
        button_frame = ttk.Frame(edit_win)
        button_frame.grid(row=row_idx, column=0, columnspan=2, pady=15)

        def save_changes():
            new_values = (
                value_var.get(),
                style_var.get(),
                color_var.get(),
                label_var.get()
            )
            ref_tree.item(item, values=new_values)
            edit_win.destroy()

        ttk.Button(button_frame, text="Save", command=save_changes, width=10).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Cancel", command=edit_win.destroy, width=10).grid(row=0, column=1, padx=10)

    def remove_ref_line(self, data_group):
        selected = self.ref_trees[data_group].selection()
        if selected:
            self.ref_trees[data_group].delete(selected)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path.set(file_path)

    def browse_save_path(self):
        save_path = filedialog.askdirectory()
        if save_path:
            self.save_path.set(save_path)

    def create_preview_ui(self, parent):
        self.preview_container = ttk.Frame(parent, width=600, height=400)
        self.preview_container.pack(fill=tk.BOTH, expand=True)
        self.preview_container.pack_propagate(False)
        self.preview_frame = ttk.Frame(self.preview_container)
        self.preview_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.clear_preview()

    def reset_settings(self):
        self.file_path.set("")
        self.save_path.set(os.getcwd())
        self.station_var.set("Both Stations")

        for group in self.data_groups:
            default_min = self.data_settings.default_settings[group]['y_min']
            default_max = self.data_settings.default_settings[group]['y_max']
            self.y_min_vars[group].set(str(default_min))
            self.y_max_vars[group].set(str(default_max))

            ref_tree = self.ref_trees[group]
            for item in ref_tree.get_children():
                ref_tree.delete(item)

            ref_lines = self.data_settings.default_settings[group]['ref_lines']
            ref_colors = self.data_settings.default_settings[group]['ref_colors']
            ref_styles = self.data_settings.default_settings[group]['ref_styles']
            ref_labels = self.data_settings.default_settings[group]['ref_labels']

            for i in range(len(ref_lines)):
                ref_tree.insert("", "end", values=(
                    ref_lines[i],
                    ref_styles[i],
                    ref_colors[i],
                    ref_labels[i]
                ))

            self.point_size_vars[group].set(self.data_settings.default_settings[group]['point_size'])
            self.point_size_displays[group].config(text=str(self.point_size_vars[group].get()))
            self.point_color_vars[group].set(self.data_settings.default_settings[group]['point_color'])
            self.title_prefix_vars[group].set(self.data_settings.default_settings[group]['title_prefix'])
            self.file_prefix_vars[group].set(self.data_settings.default_settings[group]['file_prefix'])

        self.clear_preview()

    def clear_preview(self):
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        placeholder_frame = ttk.Frame(self.preview_frame, width=500, height=400)
        placeholder_frame.pack(fill=tk.BOTH, expand=True)

        placeholder = ttk.Label(
            self.preview_frame,
            text="Preview Area - Select settings and click 'Preview'",
            justify="center",
            font=("Arial", 12)
        )
        placeholder.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.current_preview = placeholder_frame

        if hasattr(self, 'preview_fig'):
            plt.close(self.preview_fig)
            del self.preview_fig

        self.current_preview = None

    def validate_inputs(self):
        errors = []
        if not self.file_path.get():
            errors.append("Please select an Excel file")
        elif not os.path.isfile(self.file_path.get()):
            errors.append("Selected file does not exist")
        elif not (self.file_path.get().endswith('.xlsx') or self.file_path.get().endswith('.csv')):
            errors.append("Only .xlsx or .csv files are supported")
        if not self.save_path.get():
            errors.append("Please select a save path")
        elif not os.path.isdir(self.save_path.get()):
            errors.append("Selected save path does not exist")
        station = self.station_var.get()
        if station not in ["Station 1", "Station 2", "Both Stations"]:
            errors.append("Invalid station selection")
        for group in self.data_groups:
            ymin = self.y_min_vars[group].get()
            ymax = self.y_max_vars[group].get()

            if ymin and ymax:
                try:
                    ymin_val = float(ymin)
                    ymax_val = float(ymax)
                    if ymin_val >= ymax_val:
                        errors.append(f"{group}: Y-axis min must be less than max")
                except ValueError:
                    errors.append(f"{group}: Y-axis values must be numbers")

            for item in self.ref_trees[group].get_children():
                values = self.ref_trees[group].item(item, "values")
                if len(values) > 0:
                    try:
                        float(values[0])
                    except ValueError:
                        errors.append(f"{group}: Reference line value must be a number")

        return errors

    def get_ref_lines(self, data_group):
        ref_lines = []
        for item in self.ref_trees[data_group].get_children():
            values = self.ref_trees[data_group].item(item, "values")
            if len(values) < 4:
                continue

            try:
                ref_lines.append({
                    'value': float(values[0]),
                    'style': values[1],
                    'color': values[2],
                    'label': values[3]
                })
            except ValueError:
                continue

        return ref_lines

    def create_plot(self, df, station, data_group, output_path=None, preview=False):
        if preview:
            fig, ax = plt.subplots(figsize=(6, 4))
        else:
            fig, ax = plt.subplots(figsize=(8, 6))

        ref_lines = self.get_ref_lines(data_group)
        x_values = range(1, len(df) + 1)
        point_size = self.point_size_vars[data_group].get()
        point_color = self.point_color_vars[data_group].get()
        ax.scatter(x=x_values, y=df[data_group],
                   s=point_size,
                   alpha=0.7,
                   color=point_color)
        title_prefix = self.global_title_prefix.get()
        title = f"{title_prefix}-Station {station}-{data_group} Distribution"
        ax.set_title(title, fontsize=14)
        ax.set_xlabel('', fontsize=12)
        ax.set_ylabel(data_group, fontsize=12)
        ax.set_xticks([])
        values = df[data_group]
        min_value = values.min()
        max_value = values.max()
        mean_value = values.mean()
        stats_text = (f"Min: {min_value:.2f}\n"
                      f"Max: {max_value:.2f}\n"
                      f"Mean: {mean_value:.2f}")
        ax.legend([stats_text], loc='upper right', frameon=True,
                  handlelength=0, handletextpad=0,
                  fontsize=11, markerscale=0, fancybox=True)
        for ref in ref_lines:
            ax.axhline(y=ref['value'],
                       linestyle=ref['style'],
                       color=ref['color'],
                       linewidth=1.5 if ref['style'] == '--' else 1.2,
                       alpha=0.7)
            ax.text(len(df) * 1.02, ref['value'] + 0.02, ref['label'],
                    fontsize=10, color=ref['color'],
                    ha='left', va='bottom')
        try:
            y_min = float(self.y_min_vars[data_group].get())
            y_max = float(self.y_max_vars[data_group].get())
            ax.set_ylim(y_min, y_max)
        except (ValueError, TypeError):
            ref_values = [ref['value'] for ref in ref_lines] if ref_lines else []
            if ref_values:
                y_min = min(min(values) - 0.5, min(ref_values) - 1)
                y_max = max(max(values) + 0.5, max(ref_values) + 1)
            else:
                y_min = min(values) - 0.5
                y_max = max(values) + 0.5
            ax.set_ylim(y_min, y_max)
        plt.tight_layout()
        if preview:
            return fig
        file_prefix = self.global_file_prefix.get()
        safe_group_name = data_group.replace("/", "_").replace(" ", "_")
        filename = f"{file_prefix}_Station_{station}_{safe_group_name}_Plot.png"
        filepath = os.path.join(output_path, filename)

        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close(fig)

        return filename

    def update_preview(self, fig):
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.preview_frame, width=500, height=400)
        frame.pack(fill=tk.BOTH, expand=True)
        self.preview_fig = fig
        self.preview_canvas = FigureCanvasTkAgg(fig, master=frame)
        self.preview_canvas.draw()
        self.preview_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.current_preview = frame

    def preview_plot(self):
        errors = self.validate_inputs()
        if errors:
            messagebox.showerror("Input Error", "\n".join(errors))
            return

        try:
            df = pd.read_excel(self.file_path.get())
            station_column = 'Station'
            if station_column not in df.columns:
                messagebox.showerror("Data Error", f"Missing '{station_column}' column in Excel file")
                return

            tab_index = self.notebook.index(self.notebook.select())
            data_group = self.data_groups[tab_index]

            if data_group not in df.columns:
                messagebox.showerror("Data Error", f"Missing data column: {data_group}")
                return

            station_selection = self.station_var.get()
            station_map = {
                "Station 1": 1,
                "Station 2": 2,
                "Both Stations": 1
            }
            station = station_map.get(station_selection, 1)
            station_df = df[df['Station'] == station]
            if station_df.empty:
                messagebox.showinfo("Info", f"No data found for Station {station}")
                return
            fig = self.create_plot(station_df, station, data_group, preview=True)
            self.update_preview(fig)

        except Exception as e:
            messagebox.showerror("Error", f"Error generating preview:\n{str(e)}")

    def generate_plots(self):
        errors = self.validate_inputs()
        if errors:
            messagebox.showerror("Input Error", "\n".join(errors))
            return
        try:
            if self.file_path.get().endswith('.csv'):
                df = pd.read_csv(self.file_path.get())
            else:
                df = pd.read_excel(self.file_path.get())
            station_column = 'Station'
            if station_column not in df.columns:
                messagebox.showerror("Data Error", f"Missing '{station_column}' column in data file")
                return
            data_groups = self.data_groups
            missing_groups = [group for group in data_groups if group not in df.columns]
            if missing_groups:
                messagebox.showerror("Data Error", f"Missing data columns: {', '.join(missing_groups)}")
                return
            save_path = self.save_path.get()
            station_selection = self.station_var.get()
            stations = []
            if station_selection == "Station 1" or station_selection == "Both Stations":
                stations.append(1)
            if station_selection == "Station 2" or station_selection == "Both Stations":
                stations.append(2)
            total_plots = len(stations) * len(data_groups)
            if total_plots == 0:
                messagebox.showinfo("Info", "No plots to generate")
                return
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Generation Progress")
            progress_window.geometry("300x120")
            progress_window.transient(self.root)
            progress_window.grab_set()
            ttk.Label(progress_window, text="Generating plots, please wait...").pack(pady=5)
            progress = ttk.Progressbar(progress_window, orient=tk.HORIZONTAL,
                                       length=280, mode='determinate', maximum=total_plots)
            progress.pack(pady=5)
            progress_label = ttk.Label(progress_window, text=f"0/{total_plots}")
            progress_label.pack(pady=5)

            generated_files = []
            count = 0
            for station in stations:
                station_df = df[df['Station'] == station]
                if station_df.empty:
                    messagebox.showwarning("Warning", f"No data found for Station {station}")
                    continue

                for data_group in data_groups:
                    try:
                        filename = self.create_plot(station_df, station, data_group, save_path)
                        generated_files.append(filename)
                    except Exception as e:
                        messagebox.showwarning("Plot Error",
                                               f"Error generating plot for Station {station} - {data_group}:\n{str(e)}")

                    count += 1
                    progress['value'] = count
                    progress_label.config(text=f"{count}/{total_plots}")
                    progress_window.update()

            progress_window.destroy()

            msg = f"Successfully generated {len(generated_files)} plots:\n" + "\n".join(generated_files[:3])
            if len(generated_files) > 3:
                msg += f"\n... and {len(generated_files) - 3} more"

            messagebox.showinfo("Completed", msg)

            try:
                if sys.platform == "win32":
                    os.startfile(save_path)
                elif sys.platform == "darwin":
                    os.system(f'open "{save_path}"')
                else:
                    os.system(f'xdg-open "{save_path}"')
            except:
                pass

        except Exception as e:
            messagebox.showerror("Error", f"Error generating plots:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ScatterPlotGenerator(root)
    root.mainloop()