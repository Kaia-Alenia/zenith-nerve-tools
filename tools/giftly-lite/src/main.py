

from PIL import Image
Image.init()
import sys, os
from alenia_bridge.integration import init_zenith, NerveBridge
init_zenith(__file__)

import sys
import os
import threading
import traceback
import time
import json
import shutil
from tkinter import messagebox
import customtkinter as ctk
from tkinter import colorchooser

DND_AVAILABLE = False
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    pass



CURRENT_VERSION = "v1.1"

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class AleniaGiftlyLite(ctk.CTk, TkinterDnD.DnDWrapper if DND_AVAILABLE else object):
    def __init__(self):
        ctk.CTk.__init__(self)
        self.dnd_active = False
        if DND_AVAILABLE:
            try:
                self.TkdndVersion = TkinterDnD._require(self)
                self.dnd_active = True
            except:
                pass

        ctk.set_appearance_mode("dark")
        self.title(f"Giftly Lite {CURRENT_VERSION}")
        self.geometry("640x160")
        self.resizable(False, False)
        self.configure(fg_color="#0A0A0A")

        self.mode = "manual"
        self.path = None
        self.target_p = 0
        self.current_p = 0
        self.color_tick = 0
        
        self.nerve_bridge = NerveBridge("giftly", self.handle_nerve_message)

        self.setup_ui()
        self.animate_progress()

    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        top_row = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 10))

        self.brand_label = ctk.CTkLabel(
            top_row, 
            text="GIFTLY.LITE", 
            font=ctk.CTkFont(family="Courier", size=10, weight="bold"),
            text_color="#444444"
        )
        self.brand_label.pack(side="left")

        self.path_label = ctk.CTkLabel(
            top_row,
            text="[ SELECCIONAR_SPRITESHEET ]",
            font=ctk.CTkFont(family="Courier", size=9),
            text_color="#666666",
            width=260,
            anchor="w"
        )
        self.path_label.pack(side="left", padx=15, fill="x", expand=True)
        self.path_label.bind("<Button-1>", lambda e: self.manual_select())

        self.mode_switch = ctk.CTkSegmentedButton(
            top_row,
            values=["MANUAL", "DIRECTORIO"],
            command=self.toggle_mode,
            font=ctk.CTkFont(family="Courier", size=9),
            selected_color="#333333",
            unselected_color="#0A0A0A",
            selected_hover_color="#444444",
            border_width=1,
            corner_radius=0
        )
        self.mode_switch.set("MANUAL")
        self.mode_switch.pack(side="right")

        mid_row = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        mid_row.pack(fill="x", pady=5)

        dim_frame = ctk.CTkFrame(mid_row, fg_color="transparent")
        dim_frame.pack(side="left")

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

        cfg_frame = ctk.CTkFrame(mid_row, fg_color="transparent")
        cfg_frame.pack(side="left", padx=15)

        ctk.CTkLabel(
            cfg_frame, text="FPS/ESC:", 
            font=ctk.CTkFont(family="Courier", size=9), 
            text_color="#555555"
        ).pack(side="left", padx=(0, 5))

        self.fps_entry = ctk.CTkEntry(cfg_frame, **entry_style)
        self.fps_entry.insert(0, "12")
        self.fps_entry.pack(side="left")

        ctk.CTkLabel(
            cfg_frame, text="/", 
            font=ctk.CTkFont(family="Courier", size=10), 
            text_color="#222222"
        ).pack(side="left", padx=2)

        self.scale_entry = ctk.CTkEntry(cfg_frame, **entry_style)
        self.scale_entry.insert(0, "2")
        self.scale_entry.pack(side="left")

        bg_frame = ctk.CTkFrame(mid_row, fg_color="transparent")
        bg_frame.pack(side="left", padx=15)

        ctk.CTkLabel(
            bg_frame, text="BG:", 
            font=ctk.CTkFont(family="Courier", size=9), 
            text_color="#555555"
        ).pack(side="left", padx=(0, 5))

        self.bg_entry = ctk.CTkEntry(bg_frame, **entry_style)
        self.bg_entry.configure(width=50)
        self.bg_entry.insert(0, "NONE")
        self.bg_entry.pack(side="left")

        self.bg_btn = ctk.CTkButton(
            bg_frame,
            text="",
            width=20,
            height=20,
            fg_color="#333333",
            border_width=1,
            border_color="#555555",
            corner_radius=10,
            command=self.choose_color
        )
        self.bg_btn.pack(side="left", padx=5)

        self.nerve_switch = ctk.CTkSwitch(
            mid_row,
            text="NERVE BRIDGE",
            command=self.toggle_nerve,
            font=ctk.CTkFont(family="Courier", size=9),
            text_color="#555555",
            progress_color="#00FFFF",
            fg_color="#111111",
            corner_radius=0
        )
        self.nerve_switch.pack(side="right", padx=(10, 0))

        bottom_row = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        bottom_row.pack(fill="x", pady=(10, 0))

        self.run_btn = ctk.CTkButton(
            bottom_row,
            text="PROCESAR SPRITESHEET",
            command=self.on_run,
            height=28,
            corner_radius=0,
            fg_color="#1A1A1A",
            hover_color="#222222",
            border_width=1,
            border_color="#333333",
            font=ctk.CTkFont(family="Courier", size=10, weight="bold")
        )
        self.run_btn.pack(fill="x")

        self.progress_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="",
            font=ctk.CTkFont(family="Courier", size=14, weight="bold"),
            text_color="#00FFFF"
        )
        self.progress_label.pack(pady=45, fill="x")

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
        total_blocks = 58
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
            p = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp")])
        else:
            p = filedialog.askdirectory()
        if p:
            self.path = p
            name = os.path.basename(p) if len(os.path.basename(p)) < 30 else os.path.basename(p)[:27] + "..."
            self.path_label.configure(text=f"[ {name.upper()} ]", text_color="#00FFFF")

    def on_drop(self, event):
        data = event.data
        if data.startswith('{') and data.endswith('}'): data = data[1:-1]
        if data.startswith('file://'): data = data[7:]
        import urllib.parse
        self.path = urllib.parse.unquote(data).strip()
        print(f"[Giftly] on_drop received: {data}, parsed path: {self.path}, exists: {os.path.exists(self.path)}")
        
        if os.path.exists(self.path):
            name = os.path.basename(self.path) if len(os.path.basename(self.path)) < 30 else os.path.basename(self.path)[:27] + "..."
            self.path_label.configure(text=f"[ {name.upper()} ]", text_color="#00FFFF")

    def toggle_mode(self, value):
        self.mode = "folder" if value == "DIRECTORIO" else "manual"
        self.path = None
        self.path_label.configure(text="[ SELECCIONAR_SPRITESHEET ]" if self.mode == "manual" else "[ SELECCIONAR_DIRECTORIO ]", text_color="#666666")

    def toggle_nerve(self):
        self.nerve_bridge.toggle(self.nerve_switch.get() == 1)

    def send_to_framegrid(self):
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
        self.nerve_bridge.send("framegrid", msg)
        print(f"Sent to Framegrid: {msg}")

    def handle_nerve_message(self, msg):
        try:
            if msg.get("type") == "batch_ready":
                path = msg.get("path")
                w, h = msg.get("w"), msg.get("h")
                self.after(0, lambda: self.update_from_nerve(path, w, h))
        except Exception:
            pass

    def update_from_nerve(self, path, w, h):
        print(f"[Giftly] update_from_nerve triggered with path: {path}")
        self.path = path
        name = os.path.basename(path) if len(os.path.basename(path)) < 30 else os.path.basename(path)[:27] + "..."
        self.path_label.configure(text=f"[ NERVE: {name.upper()} ]", text_color="#00FFFF")
        self.width_entry.delete(0, "end")
        self.width_entry.insert(0, str(w))
        self.height_entry.delete(0, "end")
        self.height_entry.insert(0, str(h))

    def choose_color(self):
        self.attributes("-topmost", False)
        current = self.bg_entry.get()
        initial = current if current.startswith("#") else "#000000"
        color = colorchooser.askcolor(initialcolor=initial, title="ELEGIR COLOR DE FONDO")
        if color[1]:
            hex_color = color[1].upper()
            self.bg_entry.delete(0, "end")
            self.bg_entry.insert(0, hex_color)
            self.bg_btn.configure(fg_color=hex_color)

    def update_status(self, state):
        if state == "busy":
            self.target_p = 0
            self.current_p = 0
            self.main_frame.pack_forget()
            self.progress_frame.pack(fill="both", expand=True, padx=10, pady=10)
        else:
            self.progress_frame.pack_forget()
            self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def on_run(self):
        print(f"[Giftly] on_run called with path: {self.path}")
        if not self.path:
            print("[Giftly] on_run aborted: No path set.")
            return
        try:
            w = int(self.width_entry.get())
            h = int(self.height_entry.get())
            fps = int(self.fps_entry.get())
            scale = int(self.scale_entry.get())
            print(f"[Giftly] using w={w}, h={h}, fps={fps}, scale={scale}")
        except ValueError as e:
            print(f"[Giftly] on_run aborted due to ValueError: {e}")
            return
        
        self.update_status("busy")
        self.set_progress(0)
        bg_color = self.bg_entry.get()
        print("[Giftly] starting thread...")
        threading.Thread(target=self._process, args=(w, h, scale, fps, bg_color), daemon=True).start()

    def _process(self, w, h, scale, fps, bg_color):
        try:
            files = []
            if os.path.isfile(self.path):
                files = [self.path]
            elif os.path.isdir(self.path):
                valid_exts = (".png", ".jpg", ".jpeg", ".webp")
                files = [os.path.join(self.path, f) for f in os.listdir(self.path) if f.lower().endswith(valid_exts)]
            
            if not files:
                self.after(0, lambda: messagebox.showwarning("Sin imágenes", f"Nerve/Manual solicitó: {self.path} pero no hay imágenes válidas directamente allí."))
                self.target_p = 10
            
            Image.MAX_IMAGE_PIXELS = None
            processed = 0
            
            out_dir = os.path.join(self.path, "Preview")
            os.makedirs(out_dir, exist_ok=True)
            
            for f_idx, f_path in enumerate(files):
                try:
                    with open(f_path, 'rb') as debug_f:
                        print(f"DEBUG {f_path} header: {debug_f.read(8)}")
                    img = Image.open(f_path)
                    img.load()
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(f"Skipping {f_path} due to error: {e}")
                    continue
                width, height = img.size
                cols, rows = width // w, height // h
                
                frames = []
                for row in range(rows):
                    for col in range(cols):
                        box = (col * w, row * h, (col + 1) * w, (row + 1) * h)
                        frame = img.crop(box)
                        if scale != 1:
                            frame = frame.resize((w * scale, h * scale), Image.NEAREST)
                        frames.append(frame)

                if not frames:
                    continue

                processed = []
                total_frames = len(frames)
                for i, f in enumerate(frames):
                    if bg_color and bg_color.upper() != "NONE":
                        from PIL import ImageColor
                        try:
                            bg = Image.new("RGB", f.size, bg_color)
                            if f.mode == 'RGBA':
                                bg.paste(f, (0, 0), f)
                            else:
                                bg.paste(f, (0, 0))
                            processed.append(bg.quantize(colors=256, method=Image.Quantize.FASTOCTREE))
                        except:
                            processed.append(f.convert("RGB"))
                    else:
                        alpha = f.split()[3] if len(f.split()) == 4 else None
                        if alpha:
                            rgb_img = f.convert("RGB")
                            p_img = rgb_img.quantize(colors=255, method=Image.Quantize.FASTOCTREE)
                            mask = Image.eval(alpha, lambda a: 255 if a < 128 else 0)
                            p_img.paste(255, mask)
                            p_img.info["transparency"] = 255
                            p_img.info["disposal"] = 2
                            processed.append(p_img)
                        else:
                            processed.append(f.convert("RGB"))
                    
                    if i % 10 == 0 or i == total_frames - 1:
                        p = ((f_idx + (i / total_frames)) / len(files)) * 100
                        self.after(0, lambda v=int(p): self.set_progress(v))

                if processed:
                    base_dir = os.path.dirname(f_path)
                    out_dir = os.path.join(base_dir, "Individual_Gifs")
                    os.makedirs(out_dir, exist_ok=True)
                    out_name = f"{os.path.splitext(os.path.basename(f_path))[0]}.gif"
                    output_path = os.path.join(out_dir, out_name)

                    save_kwargs = {
                        "format": "GIF",
                        "save_all": True,
                        "append_images": processed[1:],
                        "duration": 1000 // fps,
                        "loop": 0,
                        "optimize": True,
                        "disposal": 2,
                        "transparency": 255
                    }
                    processed[0].save(output_path, **save_kwargs)
            self.after(0, lambda: self.set_progress(100))
            self.after(500, self.send_to_framegrid)
            self.after(1200, lambda: self.update_status("ready"))
        except Exception as e:
            print("ERROR IN PROCESS:", e)
            import traceback
            traceback.print_exc()
            from tkinter import messagebox
            self.after(0, lambda e=e: messagebox.showerror("Error", f"Fallo al procesar: {e}"))
            self.after(0, lambda: self.update_status("ready"))

if __name__ == "__main__":
    app = AleniaGiftlyLite()
    app.mainloop()
