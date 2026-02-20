"""
Main application window and UI components
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os

from config.settings import COLORS, DEFAULT_PATHS, UI
from core.operations import remove_duplicates, clean_blocklist, convert_to_pihole, download_blocklists, merge_folder_dedupe, split_blocklist, convert_to_adguard
from core.repo_manager import RepoManager
from utils.helpers import get_timestamp, ensure_directory, format_number


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("AD-BlockList Manager - Python Edition")
        self.root.geometry(f"{UI['window_width']}x{UI['window_height']}")
        self.root.minsize(UI['min_width'], UI['min_height'])
        self.root.configure(bg=COLORS['bg'])
        
        self.setup_styles()
        
        # Initialize repo manager
        self.repo_manager = RepoManager()
        
        self.create_ui()
        
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TProgressbar',
                     thickness=20,
                     background=COLORS['accent'],
                     troughcolor=COLORS['input'])
        
    def create_ui(self):
        """Create the user interface"""
        # Main container with scrollbar
        main_canvas = tk.Canvas(self.root, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        
        self.main_frame = tk.Frame(main_canvas, bg=COLORS['bg'])
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        canvas_window = main_canvas.create_window((0, 0), window=self.main_frame, 
                                                  anchor="nw", width=1070)
        
        def on_canvas_configure(event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
            main_canvas.itemconfig(canvas_window, width=event.width)
        
        main_canvas.bind('<Configure>', on_canvas_configure)
        self.main_frame.bind('<Configure>', 
                           lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        
        # Create sections
        self.create_header()
        self.create_section_1_remove_dupes()
        self.create_section_1b_folder_merge()
        self.create_section_1c_split()
        self.create_section_2_clean()
        self.create_section_3_convert()
        self.create_section_3b_convert_reverse()
        self.create_section_4_download()
        self.create_repo_manager_section()
        self.create_log_panel()
        self.create_status_bar()
        
        self.log("AD-BlockList Manager (Python Edition) ready.")
        self.log("Select an operation above to begin.")
        
    def create_header(self):
        """Create application header"""
        header = tk.Frame(self.main_frame, bg=COLORS['accent'], height=80)
        header.pack(fill=tk.X, padx=10, pady=(10, 20))
        header.pack_propagate(False)
        
        title = tk.Label(header, 
                        text="AD-BlockList Management Tool",
                        font=UI['font_title'],
                        fg=COLORS['fg'],
                        bg=COLORS['accent'])
        title.pack(side=tk.LEFT, padx=20, pady=15)
        
        subtitle = tk.Label(header,
                           text="Python Edition - High Performance",
                           font=('Segoe UI', 10),
                           fg='#cccccc',
                           bg=COLORS['accent'])
        subtitle.pack(side=tk.LEFT, padx=10, pady=20)
        
    def create_section_1_remove_dupes(self):
        """Create Remove Duplicates section"""
        frame = tk.LabelFrame(self.main_frame, 
                             text=" 1. Remove Duplicates from Blocklist ",
                             font=UI['font_section'],
                             fg=COLORS['accent'],
                             bg=COLORS['panel'],
                             padx=15, pady=15)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Input file
        tk.Label(frame, text="Input file (large blocklist):",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W)
        
        row1 = tk.Frame(frame, bg=COLORS['panel'])
        row1.pack(fill=tk.X, pady=5)
        
        self.dupe_input = tk.Entry(row1, bg=COLORS['input'], 
                                  fg=COLORS['fg'], insertbackground=COLORS['fg'],
                                  font=UI['font_mono'])
        self.dupe_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.dupe_input.insert(0, os.path.join(DEFAULT_PATHS['temp_dir'], "blocklist.txt"))
        
        tk.Button(row1, text="Browse...", command=self.browse_file(self.dupe_input),
                 bg=COLORS['input'], fg=COLORS['fg'],
                 activebackground=COLORS['accent']).pack(side=tk.RIGHT)
        
        # Output file
        tk.Label(frame, text="Output file (deduplicated):",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W, pady=(10, 0))
        
        row2 = tk.Frame(frame, bg=COLORS['panel'])
        row2.pack(fill=tk.X, pady=5)
        
        self.dupe_output = tk.Entry(row2, bg=COLORS['input'],
                                   fg=COLORS['fg'], insertbackground=COLORS['fg'],
                                   font=UI['font_mono'])
        self.dupe_output.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.dupe_output.insert(0, os.path.join(DEFAULT_PATHS['temp_dir'], "blocklist_unique.txt"))
        
        tk.Button(row2, text="Browse...", command=self.browse_save(self.dupe_output),
                 bg=COLORS['input'], fg=COLORS['fg'],
                 activebackground=COLORS['accent']).pack(side=tk.RIGHT)
        
        # Progress bar
        self.dupe_progress = ttk.Progressbar(frame, mode='determinate', length=100)
        self.dupe_progress.pack(fill=tk.X, pady=10)
        self.dupe_progress['value'] = 0
        
        # Action button
        self.dupe_btn = tk.Button(frame, text="Remove Duplicates",
                                 command=self.run_remove_dupes,
                                 bg=COLORS['accent'], fg=COLORS['fg'],
                                 activebackground=COLORS['accent_hover'],
                                 font=('Segoe UI', 11, 'bold'),
                                 padx=20, pady=10)
        self.dupe_btn.pack(anchor=tk.E)
        
    def create_section_1b_folder_merge(self):
        """Create Folder Merge + Deduplicate section"""
        frame = tk.LabelFrame(self.main_frame, 
                             text=" 1b. Merge Folder & Remove Duplicates ",
                             font=UI['font_section'],
                             fg=COLORS['accent'],
                             bg=COLORS['panel'],
                             padx=15, pady=15)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Description
        tk.Label(frame, text="Select a folder containing multiple .txt blocklist files to merge and deduplicate:",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W)
        
        # Source folder
        tk.Label(frame, text="Source folder (with .txt files):",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W, pady=(10, 0))
        
        row1 = tk.Frame(frame, bg=COLORS['panel'])
        row1.pack(fill=tk.X, pady=5)
        
        self.folder_merge_input = tk.Entry(row1, bg=COLORS['input'], 
                                          fg=COLORS['fg'], insertbackground=COLORS['fg'],
                                          font=UI['font_mono'])
        self.folder_merge_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.folder_merge_input.insert(0, os.path.join(DEFAULT_PATHS['temp_dir'], "blocklists"))
        
        tk.Button(row1, text="Browse...", command=self.browse_folder(self.folder_merge_input),
                 bg=COLORS['input'], fg=COLORS['fg'],
                 activebackground=COLORS['accent']).pack(side=tk.RIGHT)
        
        # File pattern
        tk.Label(frame, text="File pattern (e.g., *.txt):",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W, pady=(10, 0))
        
        row1b = tk.Frame(frame, bg=COLORS['panel'])
        row1b.pack(fill=tk.X, pady=5)
        
        self.folder_merge_pattern = tk.Entry(row1b, bg=COLORS['input'],
                                            fg=COLORS['fg'], insertbackground=COLORS['fg'],
                                            font=UI['font_mono'])
        self.folder_merge_pattern.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.folder_merge_pattern.insert(0, "*.txt")
        
        # Output file
        tk.Label(frame, text="Output file (merged & deduplicated):",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W, pady=(10, 0))
        
        row2 = tk.Frame(frame, bg=COLORS['panel'])
        row2.pack(fill=tk.X, pady=5)
        
        self.folder_merge_output = tk.Entry(row2, bg=COLORS['input'],
                                           fg=COLORS['fg'], insertbackground=COLORS['fg'],
                                           font=UI['font_mono'])
        self.folder_merge_output.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.folder_merge_output.insert(0, os.path.join(DEFAULT_PATHS['temp_dir'], "merged_unique.txt"))
        
        tk.Button(row2, text="Browse...", command=self.browse_save(self.folder_merge_output),
                 bg=COLORS['input'], fg=COLORS['fg'],
                 activebackground=COLORS['accent']).pack(side=tk.RIGHT)
        
        # Progress bar
        self.folder_merge_progress = ttk.Progressbar(frame, mode='determinate', length=100)
        self.folder_merge_progress.pack(fill=tk.X, pady=10)
        self.folder_merge_progress['value'] = 0
        
        # Action button
        self.folder_merge_btn = tk.Button(frame, text="Merge & Remove Duplicates",
                                         command=self.run_folder_merge,
                                         bg=COLORS['accent'], fg=COLORS['fg'],
                                         activebackground=COLORS['accent_hover'],
                                         font=('Segoe UI', 11, 'bold'),
                                         padx=20, pady=10)
        self.folder_merge_btn.pack(anchor=tk.E)
        
    def create_section_1c_split(self):
        """Create Split Large Blocklist section"""
        frame = tk.LabelFrame(self.main_frame, 
                             text=" 1c. Split Large Blocklist into Smaller Files ",
                             font=UI['font_section'],
                             fg=COLORS['accent'],
                             bg=COLORS['panel'],
                             padx=15, pady=15)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Description
        tk.Label(frame, text="Split a large blocklist into smaller files for GitHub upload:",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W)
        
        # Input file
        tk.Label(frame, text="Input file (large blocklist):",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W, pady=(10, 0))
        
        row1 = tk.Frame(frame, bg=COLORS['panel'])
        row1.pack(fill=tk.X, pady=5)
        
        self.split_input = tk.Entry(row1, bg=COLORS['input'], 
                                   fg=COLORS['fg'], insertbackground=COLORS['fg'],
                                   font=UI['font_mono'])
        self.split_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.split_input.insert(0, os.path.join(DEFAULT_PATHS['temp_dir'], "merged_unique.txt"))
        
        tk.Button(row1, text="Browse...", command=self.browse_file(self.split_input),
                 bg=COLORS['input'], fg=COLORS['fg'],
                 activebackground=COLORS['accent']).pack(side=tk.RIGHT)
        
        # Output folder
        tk.Label(frame, text="Output folder for split files:",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W, pady=(10, 0))
        
        row2 = tk.Frame(frame, bg=COLORS['panel'])
        row2.pack(fill=tk.X, pady=5)
        
        self.split_output = tk.Entry(row2, bg=COLORS['input'],
                                    fg=COLORS['fg'], insertbackground=COLORS['fg'],
                                    font=UI['font_mono'])
        self.split_output.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.split_output.insert(0, os.path.join(DEFAULT_PATHS['temp_dir'], "split_files"))
        
        tk.Button(row2, text="Browse...", command=self.browse_folder(self.split_output),
                 bg=COLORS['input'], fg=COLORS['fg'],
                 activebackground=COLORS['accent']).pack(side=tk.RIGHT)
        
        # Lines per file
        tk.Label(frame, text="Lines per file:",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W, pady=(10, 0))
        
        row3 = tk.Frame(frame, bg=COLORS['panel'])
        row3.pack(fill=tk.X, pady=5)
        
        self.split_lines = tk.Spinbox(row3, from_=10000, to=1000000, increment=10000,
                                     bg=COLORS['input'], fg=COLORS['fg'],
                                     insertbackground=COLORS['fg'],
                                     font=UI['font_mono'])
        self.split_lines.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.split_lines.delete(0, tk.END)
        self.split_lines.insert(0, "500000")
        
        tk.Label(row3, text="(500,000 recommended for GitHub)",
                bg=COLORS['panel'], fg=COLORS['info'],
                font=('Segoe UI', 9)).pack(side=tk.LEFT)
        
        # Progress bar
        self.split_progress = ttk.Progressbar(frame, mode='determinate', length=100)
        self.split_progress.pack(fill=tk.X, pady=10)
        self.split_progress['value'] = 0
        
        # Action button
        self.split_btn = tk.Button(frame, text="Split Blocklist",
                                  command=self.run_split,
                                  bg=COLORS['accent'], fg=COLORS['fg'],
                                  activebackground=COLORS['accent_hover'],
                                  font=('Segoe UI', 11, 'bold'),
                                  padx=20, pady=10)
        self.split_btn.pack(anchor=tk.E)
        
    def create_section_2_clean(self):
        """Create Clean Blocklist section"""
        frame = tk.LabelFrame(self.main_frame,
                             text=" 2. Clean Blocklist (Remove Comments) ",
                             font=UI['font_section'],
                             fg=COLORS['accent'],
                             bg=COLORS['panel'],
                             padx=15, pady=15)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Input file
        tk.Label(frame, text="Input file (with comments):",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W)
        
        row1 = tk.Frame(frame, bg=COLORS['panel'])
        row1.pack(fill=tk.X, pady=5)
        
        self.clean_input = tk.Entry(row1, bg=COLORS['input'],
                                   fg=COLORS['fg'], insertbackground=COLORS['fg'],
                                   font=UI['font_mono'])
        self.clean_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.clean_input.insert(0, os.path.join(DEFAULT_PATHS['temp_dir'], "blocklist_unique.txt"))
        
        tk.Button(row1, text="Browse...", command=self.browse_file(self.clean_input),
                 bg=COLORS['input'], fg=COLORS['fg'],
                 activebackground=COLORS['accent']).pack(side=tk.RIGHT)
        
        # Output file
        tk.Label(frame, text="Output file (cleaned):",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W, pady=(10, 0))
        
        row2 = tk.Frame(frame, bg=COLORS['panel'])
        row2.pack(fill=tk.X, pady=5)
        
        self.clean_output = tk.Entry(row2, bg=COLORS['input'],
                                    fg=COLORS['fg'], insertbackground=COLORS['fg'],
                                    font=UI['font_mono'])
        self.clean_output.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.clean_output.insert(0, os.path.join(DEFAULT_PATHS['temp_dir'], "blocklist_clean.txt"))
        
        tk.Button(row2, text="Browse...", command=self.browse_save(self.clean_output),
                 bg=COLORS['input'], fg=COLORS['fg'],
                 activebackground=COLORS['accent']).pack(side=tk.RIGHT)
        
        # Progress bar
        self.clean_progress = ttk.Progressbar(frame, mode='determinate', length=100)
        self.clean_progress.pack(fill=tk.X, pady=10)
        self.clean_progress['value'] = 0
        
        # Action button
        self.clean_btn = tk.Button(frame, text="Clean Blocklist",
                                  command=self.run_clean,
                                  bg=COLORS['accent'], fg=COLORS['fg'],
                                  activebackground=COLORS['accent_hover'],
                                  font=('Segoe UI', 11, 'bold'),
                                  padx=20, pady=10)
        self.clean_btn.pack(anchor=tk.E)
        
    def create_section_3_convert(self):
        """Create Convert to PiHole section"""
        frame = tk.LabelFrame(self.main_frame,
                             text=" 3. Convert AdGuard to PiHole Format ",
                             font=UI['font_section'],
                             fg=COLORS['accent'],
                             bg=COLORS['panel'],
                             padx=15, pady=15)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Source folder
        tk.Label(frame, text="AdGuard folder (source):",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W)
        
        row1 = tk.Frame(frame, bg=COLORS['panel'])
        row1.pack(fill=tk.X, pady=5)
        
        self.convert_input = tk.Entry(row1, bg=COLORS['input'],
                                     fg=COLORS['fg'], insertbackground=COLORS['fg'],
                                     font=UI['font_mono'])
        self.convert_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.convert_input.insert(0, DEFAULT_PATHS['adguard_home'])
        
        tk.Button(row1, text="Browse...", command=self.browse_folder(self.convert_input),
                 bg=COLORS['input'], fg=COLORS['fg'],
                 activebackground=COLORS['accent']).pack(side=tk.RIGHT)
        
        # Destination folder
        tk.Label(frame, text="PiHole folder (destination):",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W, pady=(10, 0))
        
        row2 = tk.Frame(frame, bg=COLORS['panel'])
        row2.pack(fill=tk.X, pady=5)
        
        self.convert_output = tk.Entry(row2, bg=COLORS['input'],
                                      fg=COLORS['fg'], insertbackground=COLORS['fg'],
                                      font=UI['font_mono'])
        self.convert_output.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.convert_output.insert(0, DEFAULT_PATHS['pihole'])
        
        tk.Button(row2, text="Browse...", command=self.browse_folder(self.convert_output),
                 bg=COLORS['input'], fg=COLORS['fg'],
                 activebackground=COLORS['accent']).pack(side=tk.RIGHT)
        
        # Progress bar
        self.convert_progress = ttk.Progressbar(frame, mode='determinate', length=100)
        self.convert_progress.pack(fill=tk.X, pady=10)
        self.convert_progress['value'] = 0
        
        # Action button
        self.convert_btn = tk.Button(frame, text="Convert to PiHole",
                                    command=self.run_convert,
                                    bg=COLORS['accent'], fg=COLORS['fg'],
                                    activebackground=COLORS['accent_hover'],
                                    font=('Segoe UI', 11, 'bold'),
                                    padx=20, pady=10)
        self.convert_btn.pack(anchor=tk.E)
        
    def create_section_3b_convert_reverse(self):
        """Create Convert PiHole to AdGuard section"""
        frame = tk.LabelFrame(self.main_frame,
                             text=" 3b. Convert PiHole to AdGuard Format ",
                             font=UI['font_section'],
                             fg=COLORS['accent'],
                             bg=COLORS['panel'],
                             padx=15, pady=15)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Source folder
        tk.Label(frame, text="PiHole folder (source):",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W)
        
        row1 = tk.Frame(frame, bg=COLORS['panel'])
        row1.pack(fill=tk.X, pady=5)
        
        self.convert_rev_input = tk.Entry(row1, bg=COLORS['input'],
                                     fg=COLORS['fg'], insertbackground=COLORS['fg'],
                                     font=UI['font_mono'])
        self.convert_rev_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.convert_rev_input.insert(0, DEFAULT_PATHS['pihole'])
        
        tk.Button(row1, text="Browse...", command=self.browse_folder(self.convert_rev_input),
                 bg=COLORS['input'], fg=COLORS['fg'],
                 activebackground=COLORS['accent']).pack(side=tk.RIGHT)
        
        # Destination folder
        tk.Label(frame, text="AdGuard folder (destination):",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W, pady=(10, 0))
        
        row2 = tk.Frame(frame, bg=COLORS['panel'])
        row2.pack(fill=tk.X, pady=5)
        
        self.convert_rev_output = tk.Entry(row2, bg=COLORS['input'],
                                      fg=COLORS['fg'], insertbackground=COLORS['fg'],
                                      font=UI['font_mono'])
        self.convert_rev_output.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.convert_rev_output.insert(0, DEFAULT_PATHS['adguard_home'])
        
        tk.Button(row2, text="Browse...", command=self.browse_folder(self.convert_rev_output),
                 bg=COLORS['input'], fg=COLORS['fg'],
                 activebackground=COLORS['accent']).pack(side=tk.RIGHT)
        
        # Progress bar
        self.convert_rev_progress = ttk.Progressbar(frame, mode='determinate', length=100)
        self.convert_rev_progress.pack(fill=tk.X, pady=10)
        self.convert_rev_progress['value'] = 0
        
        # Action button
        self.convert_rev_btn = tk.Button(frame, text="Convert to AdGuard",
                                    command=self.run_convert_reverse,
                                    bg=COLORS['accent'], fg=COLORS['fg'],
                                    activebackground=COLORS['accent_hover'],
                                    font=('Segoe UI', 11, 'bold'),
                                    padx=20, pady=10)
        self.convert_rev_btn.pack(anchor=tk.E)
        
    def create_section_4_download(self):
        """Create Download Blocklists section"""
        frame = tk.LabelFrame(self.main_frame,
                             text=" 4. Download Blocklists from GitHub ",
                             font=UI['font_section'],
                             fg=COLORS['accent'],
                             bg=COLORS['panel'],
                             padx=15, pady=15)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(frame,
                text="Download AdGuard blocklists from official GitHub repositories",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W)
        
        tk.Label(frame,
                text="Sources: AdGuard Hostlists Registry + AdGuard Filters",
                bg=COLORS['panel'], fg=COLORS['success'],
                font=('Segoe UI', 9)).pack(anchor=tk.W, pady=(5, 0))
        
        # Progress bar
        self.download_progress = ttk.Progressbar(frame, mode='determinate', length=100)
        self.download_progress.pack(fill=tk.X, pady=15)
        self.download_progress['value'] = 0
        
        # Action button
        self.download_btn = tk.Button(frame, text="Download All Blocklists",
                                     command=self.run_download,
                                     bg=COLORS['accent'], fg=COLORS['fg'],
                                     activebackground=COLORS['accent_hover'],
                                     font=('Segoe UI', 11, 'bold'),
                                     padx=20, pady=10)
        self.download_btn.pack(anchor=tk.E)
        
    def create_repo_manager_section(self):
        """Create Repository Management section"""
        frame = tk.LabelFrame(self.main_frame,
                             text=" Repository Management (Add/Remove/Enable Blocklist Sources) ",
                             font=UI['font_section'],
                             fg=COLORS['accent'],
                             bg=COLORS['panel'],
                             padx=15, pady=15)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Repo list frame
        list_frame = tk.Frame(frame, bg=COLORS['panel'])
        list_frame.pack(fill=tk.X, pady=5)
        
        # Create treeview for repos
        columns = ('enabled', 'name', 'source', 'folder')
        self.repo_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=6)
        
        self.repo_tree.heading('enabled', text='✓')
        self.repo_tree.heading('name', text='Repository Name')
        self.repo_tree.heading('source', text='Type')
        self.repo_tree.heading('folder', text='Destination')
        
        self.repo_tree.column('enabled', width=30, anchor='center')
        self.repo_tree.column('name', width=300)
        self.repo_tree.column('source', width=100)
        self.repo_tree.column('folder', width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.repo_tree.yview)
        self.repo_tree.configure(yscrollcommand=scrollbar.set)
        
        self.repo_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        btn_frame = tk.Frame(frame, bg=COLORS['panel'])
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(btn_frame, text="Enable/Disable",
                 command=self.toggle_selected_repo,
                 bg=COLORS['input'], fg=COLORS['fg'],
                 activebackground=COLORS['accent'],
                 font=UI['font_main']).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Remove",
                 command=self.remove_selected_repo,
                 bg=COLORS['error'], fg=COLORS['fg'],
                 activebackground='#d64d3d',
                 font=UI['font_main']).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Add New Repository",
                 command=self.show_add_repo_dialog,
                 bg=COLORS['success'], fg=COLORS['bg'],
                 activebackground='#3da58a',
                 font=('Segoe UI', 10, 'bold')).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(btn_frame, text="Refresh List",
                 command=self.refresh_repo_list,
                 bg=COLORS['input'], fg=COLORS['fg'],
                 activebackground=COLORS['accent'],
                 font=UI['font_main']).pack(side=tk.RIGHT, padx=5)
        
        # Status label
        self.repo_count_label = tk.Label(frame,
                                        text="Loading repositories...",
                                        bg=COLORS['panel'], fg=COLORS['info'],
                                        font=('Segoe UI', 9))
        self.repo_count_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Load repos
        self.refresh_repo_list()
        
    def refresh_repo_list(self):
        """Refresh the repository list in the treeview"""
        # Clear existing items
        for item in self.repo_tree.get_children():
            self.repo_tree.delete(item)
        
        # Load repos from manager
        repos = self.repo_manager.get_all_repos()
        enabled_count = 0
        
        for repo in repos:
            enabled = repo.get('enabled', False)
            if enabled:
                enabled_count += 1
            
            self.repo_tree.insert('', tk.END, iid=repo['id'],
                                values=(
                                    '✓' if enabled else '',
                                    repo.get('name', 'Unknown'),
                                    repo.get('source', 'unknown'),
                                    repo.get('destination_folder', 'Custom Lists')
                                ))
        
        self.repo_count_label.config(
            text=f"{len(repos)} repositories ({enabled_count} enabled, {len(repos) - enabled_count} disabled)"
        )
        
    def toggle_selected_repo(self):
        """Toggle enabled status of selected repository"""
        selected = self.repo_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a repository to toggle.")
            return
        
        repo_id = selected[0]
        success, new_status, message = self.repo_manager.toggle_repo(repo_id)
        
        if success:
            self.log(message, 'success')
            self.refresh_repo_list()
        else:
            messagebox.showerror("Error", message)
            
    def remove_selected_repo(self):
        """Remove selected repository"""
        selected = self.repo_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a repository to remove.")
            return
        
        repo_id = selected[0]
        repo = self.repo_manager.get_repo(repo_id)
        repo_name = repo.get('name', repo_id) if repo else repo_id
        
        if messagebox.askyesno("Confirm Removal",
                               f"Remove repository '{repo_name}'?\n\nThis cannot be undone."):
            success, message = self.repo_manager.remove_repo(repo_id)
            
            if success:
                self.log(message, 'success')
                self.refresh_repo_list()
            else:
                messagebox.showerror("Error", message)
                
    def show_add_repo_dialog(self):
        """Show dialog to add a new repository"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Repository")
        dialog.geometry("500x500")
        dialog.configure(bg=COLORS['panel'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Form fields
        tk.Label(dialog, text="Repository ID (unique identifier):",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W, padx=15, pady=(15, 0))
        
        repo_id = tk.Entry(dialog, bg=COLORS['input'], fg=COLORS['fg'],
                          insertbackground=COLORS['fg'],
                          font=UI['font_mono'])
        repo_id.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(dialog, text="Display Name:",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W, padx=15, pady=(10, 0))
        
        repo_name = tk.Entry(dialog, bg=COLORS['input'], fg=COLORS['fg'],
                            insertbackground=COLORS['fg'],
                            font=UI['font_mono'])
        repo_name.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(dialog, text="Source Type:",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W, padx=15, pady=(10, 0))
        
        source_type = ttk.Combobox(dialog, values=['github_api', 'github_raw', 'direct_url'],
                                  font=UI['font_main'])
        source_type.set('github_api')
        source_type.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(dialog, text="URL (API URL for github_api, direct URL for others):",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W, padx=15, pady=(10, 0))
        
        url_entry = tk.Entry(dialog, bg=COLORS['input'], fg=COLORS['fg'],
                            insertbackground=COLORS['fg'],
                            font=UI['font_mono'])
        url_entry.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(dialog, text="File Pattern (regex, for github_api only):",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W, padx=15, pady=(10, 0))
        
        pattern_entry = tk.Entry(dialog, bg=COLORS['input'], fg=COLORS['fg'],
                                insertbackground=COLORS['fg'],
                                font=UI['font_mono'])
        pattern_entry.insert(0, '.*\\.txt$')
        pattern_entry.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(dialog, text="Filename (for single file sources):",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W, padx=15, pady=(10, 0))
        
        filename_entry = tk.Entry(dialog, bg=COLORS['input'], fg=COLORS['fg'],
                                 insertbackground=COLORS['fg'],
                                 font=UI['font_mono'])
        filename_entry.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(dialog, text="Destination Folder:",
                bg=COLORS['panel'], fg=COLORS['fg'],
                font=UI['font_main']).pack(anchor=tk.W, padx=15, pady=(10, 0))
        
        dest_entry = tk.Entry(dialog, bg=COLORS['input'], fg=COLORS['fg'],
                             insertbackground=COLORS['fg'],
                             font=UI['font_mono'])
        dest_entry.insert(0, 'Custom Lists')
        dest_entry.pack(fill=tk.X, padx=15, pady=5)
        
        enabled_var = tk.BooleanVar(value=True)
        tk.Checkbutton(dialog, text="Enable immediately",
                      variable=enabled_var,
                      bg=COLORS['panel'], fg=COLORS['fg'],
                      selectcolor=COLORS['input'],
                      activebackground=COLORS['panel'],
                      activeforeground=COLORS['fg']).pack(anchor=tk.W, padx=15, pady=10)
        
        def save_repo():
            repo_data = {
                'id': repo_id.get().strip(),
                'name': repo_name.get().strip(),
                'source': source_type.get(),
                'enabled': enabled_var.get(),
                'destination_folder': dest_entry.get().strip()
            }
            
            # Add source-specific fields
            if repo_data['source'] == 'github_api':
                repo_data['api_url'] = url_entry.get().strip()
                repo_data['file_pattern'] = pattern_entry.get().strip()
            else:
                repo_data['url'] = url_entry.get().strip()
                repo_data['filename'] = filename_entry.get().strip()
            
            success, message = self.repo_manager.add_repo(repo_data)
            
            if success:
                self.log(message, 'success')
                self.refresh_repo_list()
                dialog.destroy()
            else:
                messagebox.showerror("Error", message)
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg=COLORS['panel'])
        btn_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Button(btn_frame, text="Cancel",
                 command=dialog.destroy,
                 bg=COLORS['input'], fg=COLORS['fg'],
                 activebackground=COLORS['accent'],
                 font=UI['font_main']).pack(side=tk.LEFT)
        
        tk.Button(btn_frame, text="Add Repository",
                 command=save_repo,
                 bg=COLORS['success'], fg=COLORS['bg'],
                 activebackground='#3da58a',
                 font=('Segoe UI', 10, 'bold')).pack(side=tk.RIGHT)
        
    def create_log_panel(self):
        """Create the log panel at bottom"""
        log_frame = tk.LabelFrame(self.main_frame,
                                 text=" Activity Log ",
                                 font=('Segoe UI', 11, 'bold'),
                                 fg=COLORS['accent'],
                                 bg=COLORS['panel'],
                                 padx=10, pady=10)
        log_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame,
                                                  wrap=tk.WORD,
                                                  height=UI['log_height'],
                                                  bg=COLORS['bg'],
                                                  fg=COLORS['fg'],
                                                  font=UI['font_mono'],
                                                  insertbackground=COLORS['fg'],
                                                  state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Tag colors for log
        self.log_text.tag_configure('success', foreground=COLORS['success'])
        self.log_text.tag_configure('warning', foreground=COLORS['warning'])
        self.log_text.tag_configure('error', foreground=COLORS['error'])
        self.log_text.tag_configure('info', foreground=COLORS['fg'])
        
    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        status = tk.Label(self.root, textvariable=self.status_var,
                         bd=1, relief=tk.SUNKEN, anchor=tk.W,
                         bg=COLORS['panel'], fg=COLORS['fg'],
                         font=('Segoe UI', 9))
        status.pack(side=tk.BOTTOM, fill=tk.X)
        
    def browse_file(self, entry):
        """Return a function that browses for file and updates entry"""
        def browse():
            file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if file:
                entry.delete(0, tk.END)
                entry.insert(0, file)
        return browse
    
    def browse_save(self, entry):
        """Return a function that browses for save location and updates entry"""
        def browse():
            file = filedialog.asksaveasfilename(defaultextension=".txt",
                                               filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if file:
                entry.delete(0, tk.END)
                entry.insert(0, file)
        return browse
    
    def browse_folder(self, entry):
        """Return a function that browses for folder and updates entry"""
        def browse():
            folder = filedialog.askdirectory()
            if folder:
                entry.delete(0, tk.END)
                entry.insert(0, folder)
        return browse
        
    def log(self, message, level='info'):
        """Add message to log with timestamp"""
        timestamp = get_timestamp()
        full_message = f"[{timestamp}] {message}\n"
        
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, full_message, level)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
        
    def set_status(self, message):
        """Update status bar"""
        self.status_var.set(message)
        self.root.update_idletasks()
        
    # Operation runners
    def run_remove_dupes(self):
        """Run remove duplicates in thread"""
        input_file = self.dupe_input.get()
        output_file = self.dupe_output.get()
        
        if not os.path.exists(input_file):
            messagebox.showerror("Error", "Input file not found!")
            return
            
        self.dupe_btn.config(state=tk.DISABLED, text="Processing...")
        self.set_status("Removing duplicates...")
        self.log("=== Starting Remove Duplicates ===")
        self.log(f"Input: {input_file}")
        self.log(f"Output: {output_file}")
        
        def progress_cb(percent, status):
            self.dupe_progress['value'] = percent
            self.set_status(status)
            
        def log_cb(msg):
            self.log(msg)
            
        def worker():
            total, unique, success = remove_duplicates(input_file, output_file, progress_cb, log_cb)
            
            if success:
                self.dupe_progress['value'] = 100
                self.log(f"✓ Complete! Processed {format_number(total)} lines, {format_number(unique)} unique.", 'success')
                self.set_status("Remove duplicates complete")
                messagebox.showinfo("Success", 
                    f"Removed duplicates!\nProcessed {format_number(total)} lines, kept {format_number(unique)} unique.")
            else:
                self.set_status("Error occurred")
                
            self.dupe_btn.config(state=tk.NORMAL, text="Remove Duplicates")
            
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
        
    def run_clean(self):
        """Run clean blocklist in thread"""
        input_file = self.clean_input.get()
        output_file = self.clean_output.get()
        
        if not os.path.exists(input_file):
            messagebox.showerror("Error", "Input file not found!")
            return
            
        self.clean_btn.config(state=tk.DISABLED, text="Processing...")
        self.set_status("Cleaning blocklist...")
        self.log("=== Starting Clean Blocklist ===")
        
        def progress_cb(percent, status):
            self.clean_progress['value'] = percent
            self.set_status(status)
            
        def log_cb(msg):
            self.log(msg)
            
        def worker():
            total, kept, success = clean_blocklist(input_file, output_file, progress_cb, log_cb)
            
            if success:
                self.clean_progress['value'] = 100
                self.log(f"✓ Complete! Processed {format_number(total)} lines, kept {format_number(kept)}.", 'success')
                self.set_status("Clean complete")
                messagebox.showinfo("Success",
                    f"Cleaned!\nRemoved comments from {format_number(total)} lines, kept {format_number(kept)}.")
            else:
                self.set_status("Error occurred")
                
            self.clean_btn.config(state=tk.NORMAL, text="Clean Blocklist")
            
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
        
    def run_convert(self):
        """Run convert to PiHole in thread"""
        source_dir = self.convert_input.get()
        target_dir = self.convert_output.get()
        
        if not os.path.exists(source_dir):
            messagebox.showerror("Error", "Source folder not found!")
            return
            
        self.convert_btn.config(state=tk.DISABLED, text="Converting...")
        self.set_status("Converting to PiHole format...")
        self.log("=== Starting Convert to PiHole ===")
        
        def progress_cb(percent, status):
            self.convert_progress['value'] = percent
            self.set_status(status)
            
        def log_cb(filename):
            self.log(f"Converting {filename}...")
            
        def worker():
            processed, success = convert_to_pihole(source_dir, target_dir, progress_cb, log_cb)
            
            if success:
                self.convert_progress['value'] = 100
                self.log(f"✓ Conversion complete! Processed {processed} files.", 'success')
                self.set_status("Conversion complete")
                messagebox.showinfo("Success", "Conversion completed successfully!")
            else:
                self.set_status("Error occurred")
                
            self.convert_btn.config(state=tk.NORMAL, text="Convert to PiHole")
            
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
        
    def run_download(self):
        """Run download in thread"""
        self.download_btn.config(state=tk.DISABLED, text="Downloading...")
        self.set_status("Downloading blocklists from configured repositories...")
        self.log("=== Starting Download ===")
        
        def progress_cb(percent, status):
            self.download_progress['value'] = percent
            self.set_status(status)
            
        def log_cb(msg, filename):
            if filename:
                self.log(f"  ↓ {filename}")
            else:
                self.log(msg)
            
        def worker():
            downloaded, success = download_blocklists(self.repo_manager, progress_cb, log_cb)
            
            if success:
                self.download_progress['value'] = 100
                self.log(f"✓ Download complete! Downloaded {downloaded} files.", 'success')
                self.set_status("Download complete")
                messagebox.showinfo("Success", "All blocklists downloaded successfully!")
            else:
                self.set_status("Error occurred")
                
            self.download_btn.config(state=tk.NORMAL, text="Download All Blocklists")
            
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
        
    def run_folder_merge(self):
        """Run folder merge + dedupe in thread"""
        source_folder = self.folder_merge_input.get()
        output_file = self.folder_merge_output.get()
        file_pattern = self.folder_merge_pattern.get()
        
        if not os.path.exists(source_folder):
            messagebox.showerror("Error", "Source folder not found!")
            return
            
        self.folder_merge_btn.config(state=tk.DISABLED, text="Processing...")
        self.set_status("Merging files and removing duplicates...")
        self.log("=== Starting Folder Merge & Deduplication ===")
        self.log(f"Source folder: {source_folder}")
        self.log(f"File pattern: {file_pattern}")
        self.log(f"Output: {output_file}")
        
        def progress_cb(percent, status):
            self.folder_merge_progress['value'] = percent
            self.set_status(status)
            
        def log_cb(msg):
            self.log(msg)
            
        def worker():
            files, total, unique, success = merge_folder_dedupe(
                source_folder, output_file, file_pattern, progress_cb, log_cb
            )
            
            if success:
                self.folder_merge_progress['value'] = 100
                self.log(f"✓ Complete! Processed {files} files, {format_number(total)} lines, {format_number(unique)} unique.", 'success')
                self.set_status("Merge complete")
                messagebox.showinfo("Success", 
                    f"Merged and deduplicated!\nProcessed {files} files, {format_number(total)} lines, kept {format_number(unique)} unique entries.")
            else:
                self.set_status("Error occurred")
                
            self.folder_merge_btn.config(state=tk.NORMAL, text="Merge & Remove Duplicates")
            
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
        
    def run_split(self):
        """Run split blocklist in thread"""
        input_file = self.split_input.get()
        output_folder = self.split_output.get()
        lines_per_file = int(self.split_lines.get())
        
        if not os.path.exists(input_file):
            messagebox.showerror("Error", "Input file not found!")
            return
            
        self.split_btn.config(state=tk.DISABLED, text="Splitting...")
        self.set_status("Splitting blocklist...")
        self.log("=== Starting Split Blocklist ===")
        self.log(f"Input: {input_file}")
        self.log(f"Output folder: {output_folder}")
        self.log(f"Lines per file: {lines_per_file:,}")
        
        def progress_cb(percent, status):
            self.split_progress['value'] = percent
            self.set_status(status)
            
        def log_cb(msg):
            self.log(msg)
            
        def worker():
            files_created, total_lines, success = split_blocklist(
                input_file, output_folder, lines_per_file, progress_cb, log_cb
            )
            
            if success:
                self.split_progress['value'] = 100
                self.log(f"✓ Complete! Created {files_created} files from {format_number(total_lines)} lines.", 'success')
                self.set_status("Split complete")
                messagebox.showinfo("Success", 
                    f"Split complete!\nCreated {files_created} files from {format_number(total_lines)} total lines.")
            else:
                self.set_status("Error occurred")
                
            self.split_btn.config(state=tk.NORMAL, text="Split Blocklist")
            
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
        
    def run_convert_reverse(self):
        """Run convert PiHole to AdGuard in thread"""
        source_dir = self.convert_rev_input.get()
        target_dir = self.convert_rev_output.get()
        
        if not os.path.exists(source_dir):
            messagebox.showerror("Error", "Source folder not found!")
            return
            
        self.convert_rev_btn.config(state=tk.DISABLED, text="Converting...")
        self.set_status("Converting to AdGuard format...")
        self.log("=== Starting Convert PiHole to AdGuard ===")
        
        def progress_cb(percent, status):
            self.convert_rev_progress['value'] = percent
            self.set_status(status)
            
        def log_cb(filename):
            self.log(f"Converting {filename}...")
            
        def worker():
            processed, success = convert_to_adguard(source_dir, target_dir, progress_cb, log_cb)
            
            if success:
                self.convert_rev_progress['value'] = 100
                self.log(f"✓ Conversion complete! Processed {processed} files.", 'success')
                self.set_status("Conversion complete")
                messagebox.showinfo("Success", "Conversion to AdGuard format completed successfully!")
            else:
                self.set_status("Error occurred")
                
            self.convert_rev_btn.config(state=tk.NORMAL, text="Convert to AdGuard")
            
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
