import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import sqlite3
import datetime
import os

# ---- RENK VE TEMA ----
COLOR_BG = "#F7F9FB"
COLOR_MAIN = "#232946"
COLOR_ACCENT = "#f6c177"
COLOR_CARD = "#FFF"
COLOR_TEXT = "#232946"
COLOR_CARD_ACCENT = "#f8f1e5"
COLOR_CARD_SHADOW = "#ececec"

ICONS = ["🏢", "✉️", "📈", "🕒", "⚡"]

# ---- MODERN CARD SINIFI ----
class ModernCard(ctk.CTkFrame):
    def __init__(self, parent, icon, title, value, accent=COLOR_ACCENT):
        super().__init__(parent, fg_color="white", corner_radius=28, width=210, height=110)
        self.grid_propagate(False)
        self.icon_label = ctk.CTkLabel(self, text=icon, font=("Arial", 36), text_color=accent)
        self.icon_label.grid(row=0, column=0, padx=14, pady=(12,2), sticky="w")
        self.title_label = ctk.CTkLabel(self, text=title, font=("Inter", 13, "bold"), text_color="#707070")
        self.title_label.grid(row=1, column=0, padx=14, sticky="w")
        self.value_label = ctk.CTkLabel(self, text=value, font=("Inter", 29, "bold"), text_color=COLOR_TEXT)
        self.value_label.grid(row=2, column=0, padx=14, sticky="w")

class Dashboard(ctk.CTkFrame):
    def __init__(self, parent, db_path="firms.db"):
        super().__init__(parent, fg_color=COLOR_BG)
        self.db_path = db_path
        self.create_dashboard()
        self.pack(fill="both", expand=True)

    # --- VERİLERİ ÇEKME ---
    def get_stats(self):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM firms")
            total_firms = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM mails")
            total_mails = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM mails WHERE replied=1")
            total_replies = c.fetchone()[0]
            today = datetime.date.today().strftime("%Y-%m-%d")
            c.execute("SELECT COUNT(*) FROM firms WHERE DATE(created_at)=?", (today,))
            firms_today = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM mails WHERE DATE(sent_at)=?", (today,))
            mails_today = c.fetchone()[0]
            conn.close()
            reply_rate = (total_replies / total_mails * 100) if total_mails else 0
            return {
                "Toplam Firma": total_firms,
                "Gönderilen Mail": total_mails,
                "Cevap Oranı": f"%{reply_rate:.1f}",
                "Bugün Firma": firms_today,
                "Bugün Mail": mails_today,
            }
        except Exception:
            return {
                "Toplam Firma": 0, "Gönderilen Mail": 0, "Cevap Oranı": "%0",
                "Bugün Firma": 0, "Bugün Mail": 0,
            }

    def get_last_firms(self, limit=5):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT name, country, sector, email FROM firms ORDER BY created_at DESC LIMIT ?", (limit,))
            data = c.fetchall()
            conn.close()
            return data
        except:
            return []

    def get_last_mails(self, limit=5):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT company, sent_at, status FROM mails ORDER BY sent_at DESC LIMIT ?", (limit,))
            data = c.fetchall()
            conn.close()
            return data
        except:
            return []

    # ---- GRAFİKLER ----
    def plot_line_chart(self):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT DATE(sent_at), COUNT(*) FROM mails GROUP BY DATE(sent_at) ORDER BY DATE(sent_at) DESC LIMIT 14")
            rows = c.fetchall()
            conn.close()
            days = [row[0] for row in rows][::-1]
            counts = [row[1] for row in rows][::-1]
            plt.figure(figsize=(4.5,2.2))
            plt.plot(days, counts, marker='o', color="#232946", linewidth=2)
            plt.fill_between(days, counts, color="#f6c177", alpha=0.15)
            plt.xticks(rotation=30)
            plt.title("Son 14 Gün: Gönderilen Mailler")
            plt.grid(True, linestyle="--", alpha=0.25)
            plt.tight_layout()
            img_path = "line_chart.png"
            plt.savefig(img_path)
            plt.close()
            return img_path
        except:
            return None

    def plot_pie_chart(self):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM mails")
            total = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM mails WHERE replied=1")
            replied = c.fetchone()[0]
            conn.close()
            pie = [replied, total-replied]
            labels = ["Cevaplanan", "Cevapsız"]
            colors = ["#f6c177", "#b8c1ec"]
            plt.figure(figsize=(2.3,2.3))
            plt.pie(pie, labels=labels, colors=colors, autopct="%1.0f%%", startangle=110, textprops={'fontsize': 11})
            plt.title("Cevap Durumu")
            img_path = "pie_chart.png"
            plt.savefig(img_path, transparent=True)
            plt.close()
            return img_path
        except:
            return None

    # --- DASHBOARD OLUŞTUR ---
    def create_dashboard(self):
        for widget in self.winfo_children():
            widget.destroy()

        stats = self.get_stats()

        # --- MODERN KARTLAR ---
        frame_cards = ctk.CTkFrame(self, fg_color=COLOR_BG)
        frame_cards.grid(row=0, column=0, sticky="nw", padx=38, pady=30)
        for i, (title, value) in enumerate(stats.items()):
            ModernCard(frame_cards, ICONS[i % len(ICONS)], title, value).grid(row=0, column=i, padx=14)

        # --- GRAFİKLER ---
        line_path = self.plot_line_chart()
        if line_path and os.path.exists(line_path):
            img = Image.open(line_path)
            img = img.resize((320, 125))
            photo = ImageTk.PhotoImage(img)
            frame_chart = ctk.CTkFrame(self, fg_color=COLOR_CARD, width=340, height=155, corner_radius=18)
            frame_chart.grid(row=1, column=0, padx=(38,0), pady=(5,12), sticky="nw")
            lbl = tk.Label(frame_chart, image=photo, bg=COLOR_CARD)
            lbl.image = photo
            lbl.pack(padx=7, pady=7)
            ctk.CTkLabel(frame_chart, text="Mail Gönderim Trendi", font=("Inter", 12, "bold"), text_color=COLOR_MAIN).pack(anchor="s")

        pie_path = self.plot_pie_chart()
        if pie_path and os.path.exists(pie_path):
            img = Image.open(pie_path)
            img = img.resize((110,110))
            photo = ImageTk.PhotoImage(img)
            frame_pie = ctk.CTkFrame(self, fg_color=COLOR_CARD, width=155, height=140, corner_radius=16)
            frame_pie.grid(row=1, column=0, padx=(388,0), pady=(5,12), sticky="nw")
            lbl = tk.Label(frame_pie, image=photo, bg=COLOR_CARD)
            lbl.image = photo
            lbl.pack(padx=8, pady=6)
            ctk.CTkLabel(frame_pie, text="Cevaplanan Mailler", font=("Inter", 12, "bold"), text_color=COLOR_MAIN).pack(anchor="s")

        # --- TABLOLAR ---
        # Son Firmalar
        firmalar = self.get_last_firms()
        frame_firm = ctk.CTkFrame(self, fg_color=COLOR_CARD, width=380, height=185, corner_radius=20)
        frame_firm.grid(row=2, column=0, padx=(38, 0), pady=(6, 12), sticky="nw")
        ctk.CTkLabel(frame_firm, text="Son Eklenen Firmalar", font=("Inter", 14, "bold"), text_color=COLOR_MAIN).pack(anchor="w", padx=12, pady=5)
        columns = ("Firma", "Ülke", "Sektör", "E-mail")
        tree_firm = ttk.Treeview(frame_firm, columns=columns, show="headings", height=4)
        for col in columns:
            tree_firm.heading(col, text=col)
            tree_firm.column(col, width=80 if col != "E-mail" else 120)
        for row in firmalar:
            tree_firm.insert('', 'end', values=row)
        tree_firm.pack(padx=8, pady=(0,9))

        # Son Mailler
        mails = self.get_last_mails()
        frame_mail = ctk.CTkFrame(self, fg_color=COLOR_CARD, width=380, height=185, corner_radius=20)
        frame_mail.grid(row=2, column=0, padx=(430, 0), pady=(6, 12), sticky="nw")
        ctk.CTkLabel(frame_mail, text="Son Gönderilen Mailler", font=("Inter", 14, "bold"), text_color=COLOR_MAIN).pack(anchor="w", padx=12, pady=5)
        columns_mail = ("Firma", "Tarih", "Durum")
        tree_mail = ttk.Treeview(frame_mail, columns=columns_mail, show="headings", height=4)
        for col in columns_mail:
            tree_mail.heading(col, text=col)
            tree_mail.column(col, width=108)
        for row in mails:
            tree_mail.insert('', 'end', values=row)
        tree_mail.pack(padx=8, pady=(0,9))

        # --- YENİLE BUTONU ---
        btn_refresh = ctk.CTkButton(self, text="Yenile", command=self.create_dashboard, fg_color=COLOR_ACCENT)
        btn_refresh.place(x=1170, y=38)

        # --- LOG/BİLDİRİM PANELİ ---
        log_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD_ACCENT, width=790, height=68, corner_radius=17)
        log_frame.grid(row=3, column=0, padx=(38, 0), pady=(6,12), sticky="nw")
        log_text = tk.Text(log_frame, height=3, width=102, bg=COLOR_CARD_ACCENT, font=("Inter", 12), bd=0, relief="flat")
        log_text.insert("end", "🔔 Son olaylar: \n")
        logs = [
            f"🕒 {datetime.datetime.now().strftime('%H:%M')} - Yeni firma eklendi: ACME Corp.",
            "⚡ 1 mail bounce aldı.",
            "🛎️ Sektör verisi güncellendi.",
            "✅ 2 yeni cevaplanan mail!",
        ]
        for log in logs:
            log_text.insert("end", f"{log}\n")
        log_text.configure(state="disabled")
        log_text.pack(padx=7, pady=2)

# Test için:
if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("1420x700")
    Dashboard(app, db_path="firms.db")
    app.mainloop()
