import math
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


def naca4_points_components(code: str, n_side: int = 100, chord: float = 1.0):
    """
    Genera le componenti geometriche del profilo NACA 4 cifre.

    Restituisce:
    - x: coordinata lungo corda [0..chord]
    - yc: linea media
    - theta: angolo locale linea media
    - yt: semispessore

    Nota: usa trailing-edge chiuso (coefficiente -0.1036).
    """
    code = code.strip()
    if len(code) != 4 or not code.isdigit():
        raise ValueError("Il codice NACA deve avere 4 cifre, ad esempio 2412 o 0012.")

    m = int(code[0]) / 100.0
    p = int(code[1]) / 10.0
    t = int(code[2:4]) / 100.0

    beta = np.linspace(0.0, math.pi, n_side + 1)
    x = 0.5 * (1.0 - np.cos(beta))  # 0 -> 1

    # trailing edge geometrico chiuso
    a4 = -0.1036

    yt = 5.0 * t * (
        0.2969 * np.sqrt(np.maximum(x, 0.0))
        - 0.1260 * x
        - 0.3516 * x**2
        + 0.2843 * x**3
        + a4 * x**4
    )

    yc = np.zeros_like(x)
    dyc_dx = np.zeros_like(x)

    if m > 0 and p > 0:
        mask1 = x < p
        mask2 = ~mask1

        yc[mask1] = (m / p**2) * (2 * p * x[mask1] - x[mask1] ** 2)
        dyc_dx[mask1] = (2 * m / p**2) * (p - x[mask1])

        yc[mask2] = (m / (1 - p) ** 2) * ((1 - 2 * p) + 2 * p * x[mask2] - x[mask2] ** 2)
        dyc_dx[mask2] = (2 * m / (1 - p) ** 2) * (p - x[mask2])

    theta = np.arctan(dyc_dx)

    return x * chord, yc * chord, theta, yt * chord


def close_profile(x, y):
    """Garantisce che primo e ultimo punto coincidano."""
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    if len(x) == 0:
        return x, y
    if not (np.isclose(x[0], x[-1]) and np.isclose(y[0], y[-1])):
        x = np.append(x, x[0])
        y = np.append(y, y[0])
    return x, y


def build_base_airfoil_xy(code: str, n_side: int = 100, chord: float = 1.0):
    """
    Profilo piano NACA 4 cifre.
    Ordine punti: estradosso TE -> LE, poi intradosso LE -> TE.
    """
    x, yc, theta, yt = naca4_points_components(code=code, n_side=n_side, chord=chord)

    xu = x - yt * np.sin(theta)
    yu = yc + yt * np.cos(theta)

    xl = x + yt * np.sin(theta)
    yl = yc - yt * np.cos(theta)

    upper_x = xu[::-1]
    upper_y = yu[::-1]

    lower_x = xl[1:]
    lower_y = yl[1:]

    x_all = np.concatenate([upper_x, lower_x])
    y_all = np.concatenate([upper_y, lower_y])
    return close_profile(x_all, y_all)


def build_curved_airfoil_xy(
    code: str,
    n_side: int,
    chord: float,
    radius: float,
    convex: bool = True,
    keep_developed_chord: bool = True,
):
    """
    Genera il profilo curvato su arco di raggio R.

    Strategia:
    1) calcola componenti NACA locali (x, yc, theta, yt)
    2) mappa la linea media su arco
    3) applica lo scostamento locale lungo la normale locale dell'arco

    keep_developed_chord=True:
      x è sviluppo d'arco (theta = x / R)
    keep_developed_chord=False:
      x è proiezione lineare (theta = asin(x / R))
    """
    if radius <= 0:
        raise ValueError("Il raggio di curvatura deve essere maggiore di zero.")

    x, yc, theta_local, yt = naca4_points_components(code=code, n_side=n_side, chord=chord)

    if keep_developed_chord:
        phi = x / radius
    else:
        if np.max(x) > radius:
            raise ValueError(
                "Con corda in proiezione lineare è necessario raggio >= corda. "
                "Aumenta il raggio o attiva 'mantieni corda sviluppata'."
            )
        ratio = np.clip(x / radius, -1.0, 1.0)
        phi = np.arcsin(ratio)

    # verso curvatura: convesso (+1), concavo (-1)
    sign = 1.0 if convex else -1.0

    # base su arco passante per origine: x_base=R*sin(phi), y_base=sign*R*(1-cos(phi))
    x_base = radius * np.sin(phi)
    y_base = sign * radius * (1.0 - np.cos(phi))

    # tangente locale arco
    tx = np.cos(phi)
    ty = sign * np.sin(phi)

    # normale locale arco (ruotata +90°)
    nx = -ty
    ny = tx

    # angolo tra asse x locale e tangente arco
    alpha = np.arctan2(ty, tx)

    # linea media mappata su arco
    x_cam = x_base + yc * nx
    y_cam = y_base + yc * ny

    # normale complessiva locale profilo (arco + camber NACA)
    total_angle = alpha + theta_local
    npx = -np.sin(total_angle)
    npy = np.cos(total_angle)

    xu = x_cam + yt * npx
    yu = y_cam + yt * npy

    xl = x_cam - yt * npx
    yl = y_cam - yt * npy

    upper_x = xu[::-1]
    upper_y = yu[::-1]
    lower_x = xl[1:]
    lower_y = yl[1:]

    x_all = np.concatenate([upper_x, lower_x])
    y_all = np.concatenate([upper_y, lower_y])
    return close_profile(x_all, y_all)


def transform_points(x, y, angle_deg=0.0, mirror_x=False, mirror_y=False):
    """Specchi e rotazione finali globali."""
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    if mirror_x:
        y = -y

    if mirror_y:
        x = -x

    if angle_deg:
        ang = math.radians(angle_deg)
        c = math.cos(ang)
        s = math.sin(ang)
        xr = x * c - y * s
        yr = x * s + y * c
        x, y = xr, yr

    return close_profile(x, y)


def format_number(value: float, decimals: int = 6) -> str:
    if abs(value) < 0.5 * 10 ** (-decimals):
        return "0"
    if abs(value - round(value)) < 0.5 * 10 ** (-decimals):
        return str(int(round(value)))
    return f"{value:.{decimals}f}"


def write_pts_text(x, y, decimals: int = 6):
    """Writer .pts compatibile: x TAB y TAB z con z=0."""
    x, y = close_profile(x, y)
    z = np.zeros_like(x)
    lines = []
    for xv, yv, zv in zip(x, y, z):
        lines.append(
            f"{format_number(float(xv), decimals)}\t"
            f"{format_number(float(yv), decimals)}\t"
            f"{format_number(float(zv), decimals)}"
        )
    return "\n".join(lines), x, y, z


def write_dxf_polyline(path: str, x, y, layer: str = "AIRFOIL"):
    """Esporta contorno chiuso come LWPOLYLINE 2D nel piano XY."""
    try:
        import ezdxf
    except ImportError as exc:
        raise RuntimeError(
            "La libreria 'ezdxf' non è installata. Installa con: pip install ezdxf"
        ) from exc

    x, y = close_profile(x, y)

    doc = ezdxf.new("R2010")
    if layer not in doc.layers:
        doc.layers.add(name=layer)

    msp = doc.modelspace()
    points_2d = [(float(xv), float(yv)) for xv, yv in zip(x, y)]
    msp.add_lwpolyline(points_2d, format="xy", dxfattribs={"layer": layer, "closed": True})

    doc.saveas(path)


def naca4_points_base(code: str, n_side: int = 100, chord: float = 1.0):
    """
    Compatibilità con API precedente:
    ritorna x, y, z per profilo piano in ordine TE estradosso -> LE -> TE intradosso.
    """
    x, y = build_base_airfoil_xy(code=code, n_side=n_side, chord=chord)
    z = np.zeros_like(x)
    return x, y, z


def build_pts_text(
    code: str,
    n_side: int,
    chord: float,
    angle_deg: float,
    mirror_x: bool,
    mirror_y: bool,
    decimals: int = 6,
):
    """
    Compatibilità con API precedente:
    genera testo .pts con trasformazioni globali applicate.
    """
    x, y, z = naca4_points_base(code=code, n_side=n_side, chord=chord)
    x, y = transform_points(x, y, angle_deg=angle_deg, mirror_x=mirror_x, mirror_y=mirror_y)
    pts_text, x, y, z = write_pts_text(x, y, decimals=decimals)
    return pts_text, x, y, z


def generate_airfoil_xy(values):
    """Seleziona modalità di generazione e applica trasformazioni finali."""
    if values["mode"] == "flat":
        x, y = build_base_airfoil_xy(
            code=values["code"],
            n_side=values["n_side"],
            chord=values["chord"],
        )
    else:
        x, y = build_curved_airfoil_xy(
            code=values["code"],
            n_side=values["n_side"],
            chord=values["chord"],
            radius=values["radius"],
            convex=values["curvature_dir"] == "convex",
            keep_developed_chord=values["keep_developed_chord"],
        )

    x, y = transform_points(
        x,
        y,
        angle_deg=values["angle_deg"],
        mirror_x=values["mirror_x"],
        mirror_y=values["mirror_y"],
    )
    return x, y


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Generatore NACA 4 cifre -> .pts + .dxf con grafico live")
        self.root.geometry("1260x790")

        self._update_job = None

        main = ttk.Frame(root, padding=10)
        main.pack(fill="both", expand=True)

        left = ttk.Frame(main)
        left.pack(side="left", fill="y", padx=(0, 10))

        right = ttk.Frame(main)
        right.pack(side="left", fill="both", expand=True)

        params = ttk.LabelFrame(left, text="Parametri", padding=10)
        params.pack(fill="x")

        self.code_var = tk.StringVar(value="0030")
        self.chord_var = tk.StringVar(value="1.0")
        self.n_side_var = tk.StringVar(value="100")
        self.mode_var = tk.StringVar(value="Profilo piano")
        self.radius_var = tk.StringVar(value="5.0")
        self.curvature_dir_var = tk.StringVar(value="convex")
        self.keep_developed_var = tk.BooleanVar(value=True)
        self.angle_var = tk.StringVar(value="0")
        self.decimals_var = tk.StringVar(value="6")
        self.mirror_x_var = tk.BooleanVar(value=False)
        self.mirror_y_var = tk.BooleanVar(value=False)

        row = 0
        ttk.Label(params, text="Profilo NACA").grid(row=row, column=0, sticky="w", pady=4)
        e = ttk.Entry(params, textvariable=self.code_var, width=14)
        e.grid(row=row, column=1, sticky="w", pady=4)
        e.bind("<KeyRelease>", self.schedule_update)

        row += 1
        ttk.Label(params, text="Corda").grid(row=row, column=0, sticky="w", pady=4)
        e = ttk.Entry(params, textvariable=self.chord_var, width=14)
        e.grid(row=row, column=1, sticky="w", pady=4)
        e.bind("<KeyRelease>", self.schedule_update)

        row += 1
        ttk.Label(params, text="Punti per semiprofilo").grid(row=row, column=0, sticky="w", pady=4)
        e = ttk.Entry(params, textvariable=self.n_side_var, width=14)
        e.grid(row=row, column=1, sticky="w", pady=4)
        e.bind("<KeyRelease>", self.schedule_update)

        row += 1
        ttk.Label(params, text="Modalità").grid(row=row, column=0, sticky="w", pady=4)
        self.mode_map = {
            "Profilo piano": "flat",
            "Profilo curvato su raggio": "curved",
        }
        mode_combo = ttk.Combobox(
            params,
            textvariable=self.mode_var,
            values=list(self.mode_map.keys()),
            state="readonly",
            width=24,
        )
        mode_combo.current(0)
        mode_combo.grid(row=row, column=1, sticky="w", pady=4)
        mode_combo.bind("<<ComboboxSelected>>", self.on_mode_changed)
        self.mode_combo = mode_combo

        row += 1
        ttk.Label(params, text="Raggio curvatura").grid(row=row, column=0, sticky="w", pady=4)
        self.radius_entry = ttk.Entry(params, textvariable=self.radius_var, width=14)
        self.radius_entry.grid(row=row, column=1, sticky="w", pady=4)
        self.radius_entry.bind("<KeyRelease>", self.schedule_update)

        row += 1
        ttk.Label(params, text="Verso curvatura").grid(row=row, column=0, sticky="w", pady=4)
        self.curv_dir_combo = ttk.Combobox(
            params,
            textvariable=self.curvature_dir_var,
            values=["convex", "concave"],
            state="readonly",
            width=14,
        )
        self.curv_dir_combo.grid(row=row, column=1, sticky="w", pady=4)
        self.curv_dir_combo.bind("<<ComboboxSelected>>", self.schedule_update)

        row += 1
        self.keep_developed_check = ttk.Checkbutton(
            params,
            text="Mantieni corda sviluppata",
            variable=self.keep_developed_var,
            command=self.update_preview,
        )
        self.keep_developed_check.grid(row=row, column=0, columnspan=2, sticky="w", pady=4)

        row += 1
        ttk.Label(params, text="Rotazione finale (gradi)").grid(row=row, column=0, sticky="w", pady=4)
        e = ttk.Entry(params, textvariable=self.angle_var, width=14)
        e.grid(row=row, column=1, sticky="w", pady=4)
        e.bind("<KeyRelease>", self.schedule_update)

        row += 1
        ttk.Label(params, text="Decimali").grid(row=row, column=0, sticky="w", pady=4)
        e = ttk.Entry(params, textvariable=self.decimals_var, width=14)
        e.grid(row=row, column=1, sticky="w", pady=4)
        e.bind("<KeyRelease>", self.schedule_update)

        row += 1
        ttk.Checkbutton(
            params,
            text="Specchio asse X",
            variable=self.mirror_x_var,
            command=self.update_preview,
        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=4)

        row += 1
        ttk.Checkbutton(
            params,
            text="Specchio asse Y",
            variable=self.mirror_y_var,
            command=self.update_preview,
        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=4)

        row += 1
        ttk.Separator(params, orient="horizontal").grid(row=row, column=0, columnspan=2, sticky="ew", pady=8)

        row += 1
        ttk.Button(params, text="Aggiorna", command=self.update_preview).grid(row=row, column=0, sticky="ew", pady=4)
        ttk.Button(params, text="Salva .pts", command=self.save_pts).grid(row=row, column=1, sticky="ew", pady=4)

        row += 1
        ttk.Button(params, text="Salva .dxf", command=self.save_dxf).grid(row=row, column=0, sticky="ew", pady=4)
        ttk.Button(params, text="Copia anteprima", command=self.copy_preview).grid(
            row=row, column=1, sticky="ew", pady=4
        )

        note = ttk.LabelFrame(left, text="Formato output", padding=10)
        note.pack(fill="x", pady=(10, 0))
        ttk.Label(
            note,
            text=(
                "- .pts: x TAB y TAB z\n"
                "- z sempre = 0\n"
                "- profilo sempre chiuso\n"
                "- trailing edge sempre chiuso\n"
                "- ordine: TE estradosso -> LE -> TE intradosso\n"
                "- .dxf: polilinea 2D chiusa su layer AIRFOIL"
            ),
            justify="left",
        ).pack(anchor="w")

        graph_frame = ttk.LabelFrame(right, text="Grafico profilo (live)", padding=8)
        graph_frame.pack(fill="both", expand=True)

        self.figure = Figure(figsize=(7, 4.8), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Profilo")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.grid(True)
        self.ax.set_aspect("equal", adjustable="box")

        self.canvas = FigureCanvasTkAgg(self.figure, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        preview_frame = ttk.LabelFrame(right, text="Anteprima .pts", padding=8)
        preview_frame.pack(fill="both", expand=True, pady=(10, 0))

        self.text = tk.Text(preview_frame, wrap="none", font=("Consolas", 10), height=14)
        self.text.pack(fill="both", expand=True)

        xscroll = ttk.Scrollbar(preview_frame, orient="horizontal", command=self.text.xview)
        xscroll.pack(fill="x")
        yscroll = ttk.Scrollbar(preview_frame, orient="vertical", command=self.text.yview)
        yscroll.place(relx=1.0, rely=0.0, relheight=1.0, anchor="ne")
        self.text.configure(xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)

        self.last_pts_text = ""
        self.last_x = None
        self.last_y = None

        self.update_mode_fields()
        self.update_preview()

    def mode_internal_value(self):
        return self.mode_map.get(self.mode_combo.get().strip(), "flat")

    def on_mode_changed(self, event=None):
        self.update_mode_fields()
        self.update_preview()

    def update_mode_fields(self):
        is_curved = self.mode_internal_value() == "curved"
        state = "normal" if is_curved else "disabled"
        readonly_state = "readonly" if is_curved else "disabled"

        self.radius_entry.config(state=state)
        self.curv_dir_combo.config(state=readonly_state)
        self.keep_developed_check.config(state=state)

    def schedule_update(self, event=None):
        if self._update_job is not None:
            self.root.after_cancel(self._update_job)
        self._update_job = self.root.after(200, self.update_preview)

    def get_values(self):
        mode = self.mode_internal_value()
        code = self.code_var.get().strip()
        chord = float(self.chord_var.get().replace(",", "."))
        n_side = int(self.n_side_var.get())
        angle_deg = float(self.angle_var.get().replace(",", "."))
        decimals = int(self.decimals_var.get())

        if chord <= 0:
            raise ValueError("La corda deve essere maggiore di zero.")
        if n_side < 2:
            raise ValueError("I punti per semiprofilo devono essere almeno 2.")
        if decimals < 0 or decimals > 12:
            raise ValueError("I decimali devono essere compresi tra 0 e 12.")
        if mode not in {"flat", "curved"}:
            raise ValueError("Modalità non valida.")

        radius = None
        if mode == "curved":
            radius = float(self.radius_var.get().replace(",", "."))
            if radius <= 0:
                raise ValueError("Il raggio di curvatura deve essere maggiore di zero.")

        curvature_dir = self.curvature_dir_var.get().strip().lower()
        if curvature_dir not in {"convex", "concave"}:
            curvature_dir = "convex"

        return {
            "mode": mode,
            "code": code,
            "chord": chord,
            "n_side": n_side,
            "radius": radius,
            "curvature_dir": curvature_dir,
            "keep_developed_chord": self.keep_developed_var.get(),
            "angle_deg": angle_deg,
            "decimals": decimals,
            "mirror_x": self.mirror_x_var.get(),
            "mirror_y": self.mirror_y_var.get(),
        }

    def update_preview(self):
        self._update_job = None
        try:
            vals = self.get_values()
            x, y = generate_airfoil_xy(vals)
            pts_text, x, y, _ = write_pts_text(x, y, decimals=vals["decimals"])

            self.last_pts_text = pts_text
            self.last_x = x
            self.last_y = y

            self.text.delete("1.0", "end")
            self.text.insert("1.0", pts_text)

            self.redraw_plot(x, y, vals)
        except Exception as e:
            self.show_plot_error(str(e))

    def redraw_plot(self, x, y, vals):
        self.ax.clear()
        self.ax.plot(x, y, marker=".", markersize=2, linewidth=1.0)

        mode_txt = "Profilo piano" if vals["mode"] == "flat" else "Profilo curvato"
        title = f"NACA {vals['code']} | corda={vals['chord']} | {mode_txt}"
        if vals["mode"] == "curved":
            title += f" | R={vals['radius']}"
        if vals["angle_deg"]:
            title += f" | rot={vals['angle_deg']}°"

        self.ax.set_title(title)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.grid(True)
        self.ax.set_aspect("equal", adjustable="box")

        if len(x) > 0:
            xmin, xmax = float(np.min(x)), float(np.max(x))
            ymin, ymax = float(np.min(y)), float(np.max(y))
            dx = xmax - xmin
            dy = ymax - ymin
            base = max(vals["chord"] * 0.02, 1e-6)
            pad_x = max(dx * 0.08, base)
            pad_y = max(dy * 0.12, base)
            self.ax.set_xlim(xmin - pad_x, xmax + pad_x)
            self.ax.set_ylim(ymin - pad_y, ymax + pad_y)

        self.canvas.draw_idle()

    def show_plot_error(self, msg):
        self.ax.clear()
        self.ax.text(0.5, 0.5, msg, ha="center", va="center", wrap=True)
        self.ax.set_axis_off()
        self.canvas.draw_idle()

    def save_pts(self):
        try:
            vals = self.get_values()
            x, y = generate_airfoil_xy(vals)
            pts_text, _, _, _ = write_pts_text(x, y, decimals=vals["decimals"])

            default_name = f"NACA{vals['code']}.pts"
            path = filedialog.asksaveasfilename(
                title="Salva file .pts",
                defaultextension=".pts",
                initialfile=default_name,
                filetypes=[("PTS files", "*.pts"), ("Tutti i file", "*.*")],
            )
            if not path:
                return

            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(pts_text)

            messagebox.showinfo("Salvato", f"File salvato correttamente:\n{path}")
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def save_dxf(self):
        try:
            vals = self.get_values()
            x, y = generate_airfoil_xy(vals)

            default_name = f"NACA{vals['code']}.dxf"
            path = filedialog.asksaveasfilename(
                title="Salva file .dxf",
                defaultextension=".dxf",
                initialfile=default_name,
                filetypes=[("DXF files", "*.dxf"), ("Tutti i file", "*.*")],
            )
            if not path:
                return

            write_dxf_polyline(path, x, y)
            messagebox.showinfo("Salvato", f"DXF salvato correttamente:\n{path}")
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def copy_preview(self):
        txt = self.text.get("1.0", "end-1c")
        self.root.clipboard_clear()
        self.root.clipboard_append(txt)
        self.root.update()
        messagebox.showinfo("Copiato", "Anteprima copiata negli appunti.")


def main():
    root = tk.Tk()
    try:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
    except Exception:
        pass
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
