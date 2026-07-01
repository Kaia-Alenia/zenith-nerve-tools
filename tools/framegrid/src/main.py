from PIL import Image
Image.MAX_IMAGE_PIXELS = None
Image.init()
import sys, os
from alenia_bridge.integration import init_zenith, NerveBridge
init_zenith(__file__)

import sys
import os
import threading
import traceback
import ctypes
import glob
import time
import shutil
import customtkinter as ctk

DND_AVAILABLE = False
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    pass

CURRENT_VERSION = "v1.1"

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"): return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

class AleniaFrameGrid(ctk.CTk, TkinterDnD.DnDWrapper if DND_AVAILABLE else object):
    def __init__(self):
        ctk.CTk.__init__(self)
        self.dnd_active = False
        if DND_AVAILABLE:
            try:
                self.TkdndVersion = TkinterDnD._require(self)
                self.dnd_active = True
                print(f"[SYSTEM] DND_ACTIVE: {self.TkdndVersion}")
            except Exception as e:
                print(f"[SYSTEM] DND_ERROR: {e}")

        ctk.set_appearance_mode("dark")
        self.title(f"Framegrid {CURRENT_VERSION}")
        self.geometry("580x52")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="#0A0A0A")
        
        self.mode = "manual"
        self.path = None
        self.target_p = 0
        self.current_p = 0
        self.color_tick = 0
        self.nerve_bridge = NerveBridge("framegrid", self.handle_nerve_message)
        self.setup_ui()
        self.animate_progress()

    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.main_frame.pack(fill="both", expand=True, padx=10)

        self.brand_label = ctk.CTkLabel(
            self.main_frame, 
            text="FG.SLICER", 
            font=ctk.CTkFont(family="Courier", size=10, weight="bold"),
            text_color="#333333"
        )
        self.brand_label.pack(side="left", padx=(0, 15))

        self.path_label = ctk.CTkLabel(
            self.main_frame,
            text="[ CLICK_TO_LOAD ]",
            font=ctk.CTkFont(family="Courier", size=9),
            text_color="#444444",
            width=100
        )
        self.path_label.pack(side="left", padx=5)
        self.path_label.bind("<Button-1>", lambda e: self.manual_select())

        self.mode_switch = ctk.CTkSegmentedButton(
            self.main_frame,
            values=["MAN", "DIR"],
            command=self.toggle_mode,
            font=ctk.CTkFont(family="Courier", size=9),
            selected_color="#333333",
            unselected_color="#0A0A0A",
            selected_hover_color="#444444",
            border_width=1,
            corner_radius=0
        )
        self.mode_switch.set("MAN")
        self.mode_switch.pack(side="left", padx=10)

        dim_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        dim_frame.pack(side="left", padx=15)

        ctk.CTkLabel(
            dim_frame, text="DIM:", 
            font=ctk.CTkFont(family="Courier", size=9), 
            text_color="#555555"
        ).pack(side="left", padx=(0, 5))

        entry_style = {
            "width": 35,
            "height": 24,
            "border_width": 1,
            "corner_radius": 0,
            "fg_color": "#050505",
            "border_color": "#222222",
            "text_color": "#00FFFF",
            "font": ctk.CTkFont(family="Courier", size=11)
        }

        self.width_entry = ctk.CTkEntry(dim_frame, **entry_style)
        self.width_entry.insert(0, "32")
        self.width_entry.pack(side="left")

        ctk.CTkLabel(
            dim_frame, text="x", 
            font=ctk.CTkFont(family="Courier", size=10), 
            text_color="#222222"
        ).pack(side="left", padx=2)

        self.height_entry = ctk.CTkEntry(dim_frame, **entry_style)
        self.height_entry.insert(0, "32")
        self.height_entry.pack(side="left")

        self.run_btn = ctk.CTkButton(
            self.main_frame,
            text="SLICE_ASSET",
            command=self.on_run,
            width=100,
            height=26,
            corner_radius=0,
            fg_color="#1A1A1A",
            hover_color="#222222",
            border_width=1,
            border_color="#333333",
            font=ctk.CTkFont(family="Courier", size=10, weight="bold")
        )
        self.run_btn.pack(side="left", padx=(10, 15))

        self.nerve_switch = ctk.CTkSwitch(
            self.main_frame,
            text="NERVE",
            command=self.toggle_nerve,
            font=ctk.CTkFont(family="Courier", size=9),
            text_color="#555555",
            progress_color="#00FFFF",
            fg_color="#111111",
            corner_radius=0,
            width=50
        )
        self.nerve_switch.pack(side="left", padx=5)

        self.progress_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="",
            font=ctk.CTkFont(family="Courier", size=14, weight="bold"),
            text_color="#00FFFF"
        )
        self.progress_label.pack(pady=12, fill="x")

        if self.dnd_active:
            for w in [self, self.main_frame, self.path_label]:
                w.drop_target_register(DND_FILES)
                w.dnd_bind('<<Drop>>', self.on_drop)
    
    def animate_progress(self):
        if self.current_p < self.target_p:
            diff = self.target_p - self.current_p
            self.current_p += max(0.5, diff * 0.15)
            if self.current_p > self.target_p:
                self.current_p = self.target_p
        elif self.current_p > self.target_p:
            self.current_p = self.target_p
            
        self.color_tick += 0.02
        total_blocks = 55
        blocks = int((self.current_p / 100) * total_blocks)
        
        def interpolate_color(c1, c2, t):
            r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
            r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            return f"#{r:02x}{g:02x}{b:02x}"

        neon_palette = ["#00FFFF", "#39FF14", "#FF00FF", "#FFFF00", "#FF3131", "#00FF00"]
        idx = int(self.color_tick) % len(neon_palette)
        next_idx = (idx + 1) % len(neon_palette)
        sub_t = self.color_tick - int(self.color_tick)
        
        current_color = interpolate_color(neon_palette[idx], neon_palette[next_idx], sub_t)
        
        bar = "█" * blocks + "░" * (total_blocks - blocks)
        self.progress_label.configure(text=f"{bar} {int(self.current_p)}%", text_color=current_color)
        self.after(20, self.animate_progress)

    def set_progress(self, percent):
        self.target_p = percent

    def manual_select(self):
        from tkinter import filedialog
        self.attributes("-topmost", False)
        if self.mode == "manual":
            p = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
        else:
            p = filedialog.askdirectory()
        self.attributes("-topmost", True)
        if p:
            self.path = p
            name = os.path.basename(p) if len(os.path.basename(p)) < 15 else os.path.basename(p)[:12] + "..."
            self.path_label.configure(text=f"[ {name.upper()} ]", text_color="#00FFFF")
            self.update_status("ready")

    def on_drop(self, event):
        data = event.data
        if data.startswith('{') and data.endswith('}'): data = data[1:-1]
        if data.startswith('file://'): data = data[7:]
        import urllib.parse
        self.path = urllib.parse.unquote(data).strip()
        print(f"[Framegrid] on_drop received: {data}, parsed path: {self.path}, exists: {os.path.exists(self.path)}")
        
        if os.path.exists(self.path):
            name = os.path.basename(self.path) if len(os.path.basename(self.path)) < 15 else os.path.basename(self.path)[:12] + "..."
            self.path_label.configure(text=f"[ {name.upper()} ]", text_color="#00FFFF")
            self.update_status("ready")
        else:
            self.update_status("error")
    
    def toggle_mode(self, value):
        self.mode = "folder" if value == "DIR" else "manual"

    def update_status(self, state):
        if state == "busy":
            self.target_p = 0
            self.current_p = 0
            self.main_frame.pack_forget()
            self.progress_frame.pack(fill="both", expand=True, padx=10)
        else:
            self.progress_frame.pack_forget()
            self.main_frame.pack(fill="both", expand=True, padx=10)

    def toggle_nerve(self):
        self.nerve_bridge.toggle(self.nerve_switch.get() == 1)

    def send_to_giftly(self):
        if not self.path or not self.nerve_switch.get():
            return
        w = self.width_entry.get()
        h = self.height_entry.get()
        msg = {
            "type": "batch_ready",
            "path": self.path,
            "w": w,
            "h": h
        }
        self.nerve_bridge.send("giftly", msg)
        print(f"Sent to Giftly: {msg}")

    def handle_nerve_message(self, msg):
        try:
            if msg.get("type") == "batch_ready":
                path = msg.get("path")
                w, h = msg.get("w"), msg.get("h")
                self.after(0, lambda: self.update_from_nerve(path, w, h))
        except Exception:
            pass

    def update_from_nerve(self, path, w, h):
        print(f"[Framegrid] update_from_nerve triggered with path: {path}")
        self.path = path
        name = os.path.basename(path) if len(os.path.basename(path)) < 15 else os.path.basename(path)[:12] + "..."
        self.path_label.configure(text=f"[ NERVE: {name.upper()} ]", text_color="#00FFFF")
        self.width_entry.delete(0, "end")
        self.width_entry.insert(0, str(w))
        self.height_entry.delete(0, "end")
        self.height_entry.insert(0, str(h))

    def on_run(self):
        print(f"[Framegrid] on_run called with path: {self.path}")
        if not self.path: 
            print("[Framegrid] on_run aborted: No path set.")
            return
        try:
            w = int(self.width_entry.get())
            h = int(self.height_entry.get())
            print(f"[Framegrid] using w={w}, h={h}")
        except ValueError as e:
            print(f"[Framegrid] on_run aborted due to ValueError: {e}")
            return
        
        self.update_status("busy")
        self.set_progress(0)
        print("[Framegrid] starting thread...")
        threading.Thread(target=self._process, args=(w, h), daemon=True).start()

    def _process(self, w, h):
        try:
            root_dir = os.path.dirname(self.path) if os.path.isfile(self.path) else self.path
            export_root = os.path.join(root_dir, "individual_frames")
            
            files = []
            if os.path.isfile(self.path):
                files = [self.path]
            elif os.path.isdir(self.path):
                valid_exts = (".png", ".jpg", ".jpeg", ".webp")
                files = [os.path.join(self.path, f) for f in os.listdir(self.path) if f.lower().endswith(valid_exts)]
            
            if not files:
                self.after(0, lambda: messagebox.showwarning("Sin imágenes", f"Nerve/Manual solicitó: {self.path} pero no hay imágenes válidas directamente allí."))
                self.after(0, lambda: self.update_status("ready"))
                return

            total_files = len(files)
            for f_idx, f_path in enumerate(files):
                try:
                    img = Image.open(f_path)
                    img.load()
                except Exception as e:
                    print(f"Skipping {f_path} due to error: {e}")
                    continue
                img_w, img_h = img.size
                base_name = os.path.splitext(os.path.basename(f_path))[0]
                file_export_dir = os.path.join(export_root, base_name)
                
                if os.path.exists(file_export_dir):
                    shutil.rmtree(file_export_dir)
                os.makedirs(file_export_dir, exist_ok=True)

                rows = img_h // h
                cols = img_w // w
                total_steps = rows * cols
                count = 0
                for r in range(rows):
                    for c in range(cols):
                        left, top = c * w, r * h
                        right, bottom = left + w, top + h
                        frame = img.crop((left, top, right, bottom))
                        frame.save(os.path.join(file_export_dir, f"{count:02d}.png"))
                        count += 1
                        if count % 20 == 0 or count == total_steps:
                            if total_files == 1:
                                p = (count / total_steps) * 100
                            else:
                                p = ((f_idx + (count / total_steps)) / total_files) * 100
                            self.after(0, lambda v=int(p): self.set_progress(v))

            self.after(0, lambda: self.set_progress(100))
            self.after(500, self.send_to_giftly)
            self.after(1200, lambda: self.update_status("ready"))
        except Exception as e:
            print("ERROR IN PROCESS:", e)
            import traceback
            traceback.print_exc()
            from tkinter import messagebox
            self.after(0, lambda e=e: messagebox.showerror("Error", f"Fallo al procesar: {e}"))
            self.after(0, lambda: self.update_status("ready"))

if __name__ == "__main__":
    app = AleniaFrameGrid()
    app.mainloop()
