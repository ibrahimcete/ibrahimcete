import customtkinter as ctk
import tkinter as tk
import sqlite3
from dashboard import Dashboard

# Ana fonksiyonları main.py'den çek
from main import (
    full_b2b_pipeline,
    run_firm_extraction,
    run_report_export,
    send_mail,
    get_all_firmalar,
    run_ai_enrichment_for_company
)

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COLOR_BG = "#f6f7fa"
COLOR_MAIN = "#2e3b55"
COLOR_ACCENT = "#c5a657"
COLOR_CARD = "#fff"
COLOR_TEXT = "#23272f"
COLOR_GRAY = "#e6e7eb"

FONT_HEAD = ("Inter", 24, "bold")
FONT_MENU = ("Inter", 15, "bold")
FONT_CARD = ("Inter", 13)
FONT_BUT = ("Inter", 13, "bold")

MENUS = [
    ("🏠", "Dashboard"),
    ("🏢", "Firmalar"),
    ("🔍", "Firma Bul"),
    ("✉️", "Mail Gönder"),
    ("📈", "Raporlar"),
    ("🕓", "Geçmiş"),
    ("📊", "Analiz"),
    ("⚙️", "Ayarlar"),
    ("⏻", "Çıkış"),
]

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("B2B Otomasyon Sistemi")
        self.geometry("1320x800")
        self.minsize(1150, 700)
        self.configure(bg=COLOR_BG)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, fg_color=COLOR_MAIN, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=3, sticky="nsw")
        self.sidebar.grid_propagate(False)
        self.logo = ctk.CTkLabel(self.sidebar, text="B2B", font=("Inter", 29, "bold"), text_color="white")
        self.logo.grid(row=0, column=0, padx=30, pady=(38, 36), sticky="w")

        self.menu_buttons = []
        for i, (icon, name) in enumerate(MENUS):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{icon}  {name}",
                font=FONT_MENU,
                fg_color="white" if i == 0 else COLOR_MAIN,
                text_color=COLOR_MAIN if i == 0 else "white",
                hover_color=COLOR_ACCENT,
                corner_radius=16,
                height=42,
                width=158,
                anchor="w",
                command=lambda idx=i: self.switch_menu(idx)
            )
            btn.grid(row=i+1, column=0, padx=18, pady=6, sticky="w")
            self.menu_buttons.append(btn)

        # Top bar
        self.topbar = ctk.CTkFrame(self, fg_color=COLOR_CARD, height=65, corner_radius=18)
        self.topbar.grid(row=0, column=1, sticky="new", padx=(0, 32), pady=(16, 0))
        self.topbar.grid_columnconfigure(0, weight=1)
        self.topbar.grid_rowconfigure(0, weight=1)
        self.title_label = ctk.CTkLabel(self.topbar, text="Dashboard", font=FONT_HEAD, text_color=COLOR_TEXT)
        self.title_label.grid(row=0, column=0, sticky="w", padx=(34, 0), pady=15)
        self.user_avatar = ctk.CTkLabel(self.topbar, text="👤", font=("Arial", 22))
        self.user_avatar.grid(row=0, column=5, sticky="e", padx=(0, 12))
        self.user_label = ctk.CTkLabel(self.topbar, text="İbrahim", font=("Inter", 15, "bold"), text_color=COLOR_TEXT)
        self.user_label.grid(row=0, column=4, sticky="e", padx=(0, 13))
        self.bell = ctk.CTkLabel(self.topbar, text="🔔", font=("Arial", 22))
        self.bell.grid(row=0, column=3, sticky="e", padx=(0, 17))

        # Body (Ana panel)
        self.body = ctk.CTkFrame(self, fg_color=COLOR_BG)
        self.body.grid(row=1, column=1, sticky="nsew", padx=(0, 32), pady=(8, 16))
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_rowconfigure(0, weight=1)

        self.screens = [
            Dashboard(self.body, db_path="firms.db"),
            self.firmalar_screen(),
            self.firma_bul_screen(),
            self.mail_screen(),
            self.raporlar_screen(),
            self.placeholder_screen("Geçmiş"),
            self.placeholder_screen("Analiz"),
            self.placeholder_screen("Ayarlar"),
            self.placeholder_screen("Çıkış"),
        ]
        self.active_screen = 0
        self.show_screen(0)

    def switch_menu(self, idx):
        for i, btn in enumerate(self.menu_buttons):
            if i == idx:
                btn.configure(fg_color="white", text_color=COLOR_MAIN)
            else:
                btn.configure(fg_color=COLOR_MAIN, text_color="white")
        self.title_label.configure(text=MENUS[idx][1])
        self.show_screen(idx)

    def show_screen(self, idx):
        for s in self.screens:
            s.grid_forget()
        self.screens[idx].grid(row=0, column=0, sticky="nsew")

    def dashboard_screen(self):
        frame = ctk.CTkFrame(self.body, fg_color=COLOR_BG)
        frame.grid_rowconfigure((0,1,2), weight=1)
        frame.grid_columnconfigure((0,1,2), weight=1)
        for i, (title, value) in enumerate([
            ("Toplam Firma", "120"),
            ("Gönderilen Mail", "350"),
            ("Cevap Oranı", "%18,5"),
        ]):
            card = ctk.CTkFrame(frame, fg_color=COLOR_CARD, width=185, height=80, corner_radius=18)
            card.grid(row=0, column=i, padx=14, pady=(14, 6), sticky="nw")
            ctk.CTkLabel(card, text=title, font=("Inter", 14), text_color="#4b4b4b").pack(anchor="nw", padx=17, pady=(9, 2))
            ctk.CTkLabel(card, text=value, font=("Inter", 23, "bold"), text_color=COLOR_TEXT).pack(anchor="w", padx=17)
        return frame

    def firmalar_screen(self):
        frame = ctk.CTkFrame(self.body, fg_color=COLOR_BG)
        card = ctk.CTkFrame(frame, fg_color=COLOR_CARD, width=850, height=420, corner_radius=20)
        card.pack(padx=36, pady=48)
        ctk.CTkLabel(card, text="Firma Listesi", font=("Inter", 17, "bold"), text_color=COLOR_TEXT).pack(anchor="w", padx=20, pady=(18, 7))
        try:
            firmalar = get_all_firmalar()
            datas = []
            for _, row in firmalar.iterrows():
                datas.append([
                    row.get("name", ""),
                    row.get("type", ""),
                    row.get("email", ""),
                    row.get("phone", "")
                ])
        except Exception:
            datas = []
        head_frame = ctk.CTkFrame(card, fg_color="transparent")
        head_frame.pack(anchor="w", padx=20)
        for i, col in enumerate(["Firma Adı", "Şirket Türü", "E-Posta", "Telefon"]):
            ctk.CTkLabel(head_frame, text=col, font=("Inter", 13, "bold"), text_color="#6b6b6b", width=160, anchor="w").grid(row=0, column=i, padx=6)
        for r, row in enumerate(datas):
            for c, val in enumerate(row):
                ctk.CTkLabel(card, text=str(val), font=FONT_CARD, text_color=COLOR_TEXT, width=160, anchor="w").place(x=20 + c*165, y=85 + r*34)
        return frame

    def firma_bul_screen(self):
        frame = ctk.CTkFrame(self.body, fg_color=COLOR_BG)
        card = ctk.CTkFrame(frame, fg_color=COLOR_CARD, width=860, height=560, corner_radius=22)
        card.pack(padx=48, pady=62)
        ctk.CTkLabel(card, text="🔍 Gelişmiş Firma Bul", font=("Inter", 21, "bold"), text_color=COLOR_TEXT).pack(anchor="w", padx=26, pady=(18, 2))
        ctk.CTkLabel(card, text="Şehir ve sektör girerek firma çekin. (main.py ile full otomasyon!)", font=("Inter", 12), text_color="#929292").pack(anchor="w", padx=26, pady=(0, 10))
        input_frame = ctk.CTkFrame(card, fg_color="transparent")
        input_frame.pack(anchor="w", padx=24, pady=(5, 12))
        city_entry = ctk.CTkEntry(input_frame, placeholder_text="Şehir (örn. Istanbul)", width=160, font=("Inter", 13))
        city_entry.grid(row=0, column=0, padx=4)
        sector_entry = ctk.CTkEntry(input_frame, placeholder_text="Sektör (örn. mattress store)", width=160, font=("Inter", 13))
        sector_entry.grid(row=0, column=1, padx=4)
        num_entry = ctk.CTkEntry(input_frame, placeholder_text="Firma sayısı (örn. 10)", width=120, font=("Inter", 13))
        num_entry.grid(row=0, column=2, padx=4)
        result_label = ctk.CTkLabel(card, text="", font=FONT_CARD, text_color="#6d6d6d")
        result_label.pack(anchor="w", padx=26, pady=(2,8))
        head_frame = ctk.CTkFrame(card, fg_color="transparent")
        head_frame.pack(anchor="w", padx=24, pady=(8, 2))
        for i, col in enumerate(["Firma Adı", "Şirket Türü", "E-Posta", "Telefon"]):
            ctk.CTkLabel(head_frame, text=col, font=("Inter", 13, "bold"), text_color="#6b6b6b", width=180, anchor="w").grid(row=0, column=i, padx=4)
        results_frame = ctk.CTkFrame(card, fg_color="transparent")
        results_frame.pack(anchor="w", padx=24, pady=(2, 0))

        def ara():
            for widget in results_frame.winfo_children():
                widget.destroy()
            city = city_entry.get().strip()
            sector = sector_entry.get().strip()
            try:
                num = int(num_entry.get())
            except Exception:
                num = 10
            if not city or not sector:
                result_label.configure(text="Lütfen şehir ve sektör girin.")
                return
            result_label.configure(text="Firma aranıyor, lütfen bekleyin...")
            self.update()
            try:
                sonuc = run_firm_extraction(sector, city, num)
                if sonuc:
                    for r, firma in enumerate(sonuc):
                        ad = firma.get('name', firma.get('ad', ''))
                        tur = firma.get('type', firma.get('tur', ''))
                        mail = firma.get('email', firma.get('mail', ''))
                        tel = firma.get('phone', firma.get('tel', ''))
                        ctk.CTkLabel(results_frame, text=ad, font=FONT_CARD, text_color=COLOR_TEXT, width=180, anchor="w").grid(row=r, column=0, padx=4, pady=2)
                        ctk.CTkLabel(results_frame, text=tur, font=FONT_CARD, text_color=COLOR_TEXT, width=180, anchor="w").grid(row=r, column=1, padx=4, pady=2)
                        ctk.CTkLabel(results_frame, text=mail, font=FONT_CARD, text_color=COLOR_TEXT, width=180, anchor="w").grid(row=r, column=2, padx=4, pady=2)
                        ctk.CTkLabel(results_frame, text=tel, font=FONT_CARD, text_color=COLOR_TEXT, width=180, anchor="w").grid(row=r, column=3, padx=4, pady=2)
                    result_label.configure(text=f"{len(sonuc)} firma listelendi.")
                else:
                    result_label.configure(text="Firma bulunamadı.")
            except Exception as e:
                result_label.configure(text=f"Hata: {e}")

        ctk.CTkButton(card, text="🔍 Firma Ara", font=FONT_BUT, fg_color=COLOR_ACCENT, text_color="white", width=150, corner_radius=13, command=ara).pack(anchor="w", padx=26, pady=(10, 18))
        return frame

    def mail_screen(self):
        frame = ctk.CTkFrame(self.body, fg_color=COLOR_BG)
        card = ctk.CTkFrame(frame, fg_color=COLOR_CARD, width=820, height=400, corner_radius=18)
        card.pack(padx=45, pady=75)
        ctk.CTkLabel(card, text="Mail Gönder", font=("Inter", 17, "bold"), text_color=COLOR_TEXT).pack(anchor="w", padx=20, pady=(18, 9))
        to_entry = ctk.CTkEntry(card, placeholder_text="E-posta adresi", width=400, font=("Inter", 13))
        to_entry.pack(anchor="w", padx=20, pady=4)
        subject_entry = ctk.CTkEntry(card, placeholder_text="Başlık", width=400, font=("Inter", 13))
        subject_entry.pack(anchor="w", padx=20, pady=4)
        body_box = ctk.CTkTextbox(card, width=700, height=150, font=("Inter", 13))
        body_box.pack(anchor="w", padx=20, pady=(10, 20))
        result_label = ctk.CTkLabel(card, text="", font=FONT_CARD, text_color="#6d6d6d")
        result_label.pack(anchor="w", padx=20, pady=(2,8))
        def gonder():
            to_email = to_entry.get().strip()
            subject = subject_entry.get().strip()
            body = body_box.get("1.0", "end-1c")
            if not to_email or not subject or not body:
                result_label.configure(text="Lütfen tüm alanları doldurun.")
                return
            try:
                sonuc = send_mail(to_email, subject, body)
                result_label.configure(text=sonuc)
            except Exception as e:
                result_label.configure(text=f"Hata: {e}")
        ctk.CTkButton(card, text="Gönder", font=FONT_BUT, fg_color=COLOR_ACCENT, text_color="white", width=150, corner_radius=13, command=gonder).pack(anchor="w", padx=20)
        return frame

    def raporlar_screen(self):
        frame = ctk.CTkFrame(self.body, fg_color=COLOR_BG)
        card = ctk.CTkFrame(frame, fg_color=COLOR_CARD, width=840, height=420, corner_radius=20)
        card.pack(padx=48, pady=62)
        ctk.CTkLabel(card, text="Raporlar", font=("Inter", 18, "bold"), text_color=COLOR_TEXT).pack(anchor="w", padx=24, pady=(20, 7))
        ctk.CTkLabel(card, text="Burada gelişmiş rapor, grafik ve analizler gösterilebilir.", font=FONT_CARD, text_color="#6d6d6d").pack(anchor="w", padx=24, pady=(2, 10))
        result_label = ctk.CTkLabel(card, text="", font=FONT_CARD, text_color="#6d6d6d")
        result_label.pack(anchor="w", padx=24, pady=(2,10))
        def rapor_export():
            try:
                sonuc = run_report_export()
                result_label.configure(text=str(sonuc))
            except Exception as e:
                result_label.configure(text=f"Hata: {e}")
        ctk.CTkButton(card, text="Excel'e Aktar", font=FONT_BUT, fg_color=COLOR_ACCENT, text_color="white", width=150, corner_radius=12, command=rapor_export).pack(anchor="w", padx=24, pady=14)
        return frame

    def placeholder_screen(self, name):
        frame = ctk.CTkFrame(self.body, fg_color=COLOR_BG)
        ctk.CTkLabel(frame, text=f"{name} ekranı burada olacak.", font=FONT_CARD, text_color=COLOR_TEXT).pack(padx=44, pady=56)
        return frame

if __name__ == "__main__":
    app = App()
    app.mainloop()
