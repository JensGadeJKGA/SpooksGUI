import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from SpooksHelperLib.Vequilibrium import verticalEquilibrium
from SpooksHelperLib.GenerateReport.generateReport import generateReport
from SpooksHelperLib.Export.export import export
from SpooksHelperLib.plot import plot
from SpooksHelperLib.SPWplugin import log_usage
from SpooksHelperLib.openSpooks import OpenSpooks

import os

class SpooksApp(tk.Tk):
    def __init__(self, version="3.0"):
        super().__init__()
        self.title("WinSPOOKS Plug-in")
        self.minsize(700, 600)

        # State variables
        self.version = version
        self.filename = None
        self.outputdir = None

        # Output options
        self.checkplot = tk.IntVar(value=0)
        self.checkexp_ep = tk.IntVar(value=0)
        self.checkexp = tk.IntVar(value=0)
        self.checkreport = tk.IntVar(value=0)

        self._make_tabs()

    # ---------------- Tabs ----------------
    def _make_tabs(self):
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both")

        self.tab_calc = ttk.Frame(notebook)
        self.tab_log = ttk.Frame(notebook)
        self.tab_version = ttk.Frame(notebook)

        notebook.add(self.tab_calc, text="Calculations")
        notebook.add(self.tab_log, text="Calculation Log")
        notebook.add(self.tab_version, text="Version")

        self._make_calc_tab()
        self._make_log_tab()
        self._make_version_tab()

    # ---------------- Calculation Tab ----------------
    def _make_calc_tab(self):
        tab = self.tab_calc

        # Logo + header
        ttk.Label(tab, text=" COWI", font=("Century Schoolbook", 33), foreground="orange red")\
            .grid(column=0, row=0, sticky="SE")
        ttk.Label(tab, text="WinSPOOKS Plug-in", font=("Calibri", 16))\
            .grid(column=2, row=0, sticky="SW")

        # Best practice note
        ttk.Label(tab, text=" Best practice ", font=("Calibri", 10, "italic"))\
            .grid(column=0, row=1, sticky="NE")

        # Input section
        ttk.Label(tab, text="Input", font=("Calibri", 14))\
            .grid(column=0, row=2, sticky="E")
        ttk.Button(tab, text="Browse", command=self._browse_file)\
            .grid(column=0, row=3, sticky="E")

        ttk.Label(tab, text="Input file:  ", font=("Calibri", 11))\
            .grid(column=1, row=3, sticky="E")
        self.label_file = ttk.Label(tab, text="No file", font=("Calibri", 11))
        self.label_file.grid(column=2, row=3, sticky="W")

        # Divider
        ttk.Separator(tab, orient="horizontal").grid(column=1, row=4, columnspan=3, sticky="ew", pady=5)

        # Output section
        ttk.Label(tab, text="Output", font=("Calibri", 14))\
            .grid(column=0, row=8, sticky="E")

        ttk.Checkbutton(tab, variable=self.checkplot, text="Plot results")\
            .grid(column=1, row=9, sticky="W")
        ttk.Checkbutton(tab, variable=self.checkexp_ep, text="Export earth pressure results as .txt",
                        command=self._toggle_output)\
            .grid(column=1, row=10, sticky="W")
        ttk.Checkbutton(tab, variable=self.checkexp, text="Export results as .txt",
                        command=self._toggle_output)\
            .grid(column=1, row=11, sticky="W")
        ttk.Checkbutton(tab, variable=self.checkreport, text="Generate reports",
                        command=self._toggle_output)\
            .grid(column=1, row=12, sticky="W")

        ttk.Label(tab, text="Export results to:  ", font=("Calibri", 11), foreground="grey")\
            .grid(column=1, row=13, sticky="E")
        self.label_dir = ttk.Label(tab, text="No directory", font=("Calibri", 11), foreground="grey")
        self.label_dir.grid(column=2, row=13, sticky="W")

        ttk.Button(tab, text="Browse", command=self._browse_output, state="disabled")\
            .grid(column=0, row=13, sticky="E")


        # Divider
        ttk.Separator(tab, orient="horizontal").grid(column=1, row=14, columnspan=6, sticky="ew", pady=5)

        # Calculations section
        ttk.Label(tab, text="Calculations", font=("Calibri", 14))\
            .grid(column=0, row=16, sticky="E")

        ttk.Label(tab, text="Status:", font=("Calibri", 11))\
            .grid(column=1, row=17, sticky="E")
        self.label_status = ttk.Label(tab, text=" No input file", font=("Calibri", 11))
        self.label_status.grid(column=2, row=17, sticky="W")

        ttk.Label(tab, text="Calc. no.:", font=("Calibri", 11))\
            .grid(column=1, row=18, sticky="E")
        self.label_calcno = ttk.Label(tab, text="", font=("Calibri", 11))
        self.label_calcno.grid(column=2, row=18, sticky="W")

        ttk.Button(tab, text="Run calculations", command=self._calculate)\
            .grid(column=1, row=20, sticky="E")
        self.warning = ttk.Label(tab, text="", font=("Calibri", 11), foreground="red")
        self.warning.grid(column=2, row=20, sticky="W")

        self.progress = ttk.Progressbar(tab, length=300, mode="determinate")
        self.progress.grid(column=2, row=21, sticky="W")

        # Divider
        ttk.Separator(tab, orient="horizontal").grid(column=1, row=28, columnspan=6, sticky="ew", pady=5)

        # Footer
        ttk.Button(tab, text="Open WinSpooks", command=OpenSpooks, state="enabled")\
            .grid(column=0, row=29, sticky="E")
        ttk.Label(tab, text="COWI A/S", font=("Calibri", 9))\
            .grid(column=0, row=30, sticky="E")
        ttk.Label(tab, text=f"Current version: {self.version}", font=("Calibri", 9))\
            .grid(column=2, row=30, sticky="W")

        # Configure row/column padding so it spaces correctly
        for r in range(0, 27):
            tab.rowconfigure(r, pad=3)
        for c in range(0, 7):
            tab.columnconfigure(c, pad=5)

    def _toggle_output(self):
        if self.checkexp.get() or self.checkexp_ep.get() or self.checkreport.get():
            # enable
            for child in self.tab_calc.winfo_children():
                if isinstance(child, ttk.Button) and child.cget("text") == "Browse":
                    child.configure(state="normal")
            self.label_dir.configure(foreground="black")
        else:
            # disable
            for child in self.tab_calc.winfo_children():
                if isinstance(child, ttk.Button) and child.cget("text") == "Browse":
                    child.configure(state="disabled")
            self.label_dir.configure(foreground="grey")

    def _browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if filename:
            self.filename = filename
            self.label_file.config(text=os.path.basename(filename), foreground="green")
            self.label_status.config(text="Input file loaded")

    def _browse_output(self):
        outputdir = filedialog.askdirectory()
        if outputdir:
            self.outputdir = outputdir
            self.label_dir.config(text=outputdir, foreground="green")
            self.label_status.config(text="Export directory selected")

    def _calculate(self):
        if not self.filename:
            self.label_status.config(text="Please select an input file")
            return
        self.label_status.config(text="Calculating...")
        self.update_idletasks()

        # Run actual calculations
        log_usage()
        feeder_output = verticalEquilibrium.SPOOKSFeeder(
            self.filename, None, self.progress, self.tab_calc, self.logtxt, tk
        )

        if self.checkreport.get():
            generateReport().ReportsMerger(feeder_output, [self.outputdir], self.version, self.label_status, self.tab_calc, self.progress, None)
        if self.checkplot.get():
            plot.PlotResults(feeder_output)
        if self.checkexp.get():
            export.ExportResultsAsTxt(feeder_output, [self.outputdir])
        if self.checkexp_ep.get():
            export.ExportEarthPressureResultsAsTxt(feeder_output, [self.outputdir])

        self.label_status.config(text="Tasks completed")

    # ---------------- Log Tab ----------------
    def _make_log_tab(self):
        frame = ttk.Frame(self.tab_log, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Calculation Log", font=("Calibri", 16, "bold")).pack(anchor="w", pady=10)
        self.logtxt = scrolledtext.ScrolledText(frame, width=100, height=30)
        self.logtxt.pack(fill="both", expand=True)
        self.logtxt.insert(tk.END, "Load file - start calculating.\n")

    # ---------------- Version Tab ----------------
    def _make_version_tab(self):
        frame = ttk.Frame(self.tab_version, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Version History", font=("Calibri", 16, "bold")).pack(anchor="w", pady=10)

        tree = ttk.Treeview(frame, columns=("Date", "Prepared", "Checked", "Description"), show="headings", height=10)
        tree.pack(fill="both", expand=True)

        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="w")

        version_history = [
            ("3.0", "20.08.2025", "JKGA", "JKGA", "Completely refactored source code"),
            ("2.0", "22.03.2024", "EMBT", "MLHU", "Added sheet pile wall - Add on"),
            ("1.0", "12.05.2020", "EMBT", "EMSS", "Report generation and vertical equilibrium added"),
            ("0.1", "10.01.2020", "EMBT", "EMSS", "Test version"),
        ]

        for v in version_history:
            tree.insert("", "end", values=v[1:])  # skip version in values
            tree.set(tree.get_children()[-1], column="Date", value=v[1])  # align with headings
            tree.item(tree.get_children()[-1], values=v[1:])  # properly align

        

if __name__ == "__main__":
    OpenSpooks()
    app = SpooksApp()
    app.mainloop()
