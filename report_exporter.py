import pandas as pd

def export_contacts_to_excel(df, path="contacts_report.xlsx"):
    """Contacts tablosunu Excel'e aktarır."""
    df.to_excel(path, index=False)
    print(f"[REPORT] Excel çıktısı kaydedildi: {path}")

def export_contacts_to_csv(df, path="contacts_report.csv"):
    """Contacts tablosunu CSV olarak kaydeder."""
    df.to_csv(path, index=False)
    print(f"[REPORT] CSV çıktısı kaydedildi: {path}")

def export_managers_to_excel(df, path="managers_report.xlsx"):
    """Managers tablosunu Excel'e aktarır."""
    df.to_excel(path, index=False)
    print(f"[REPORT] Yöneticiler Excel çıktısı: {path}")

def export_managers_to_csv(df, path="managers_report.csv"):
    """Managers tablosunu CSV olarak kaydeder."""
    df.to_csv(path, index=False)
    print(f"[REPORT] Yöneticiler CSV çıktısı: {path}")

def export_companies_to_excel(df, path="companies_report.xlsx"):
    """Companies tablosunu Excel'e aktarır."""
    df.to_excel(path, index=False)
    print(f"[REPORT] Firmalar Excel çıktısı: {path}")

def export_companies_to_csv(df, path="companies_report.csv"):
    """Companies tablosunu CSV olarak kaydeder."""
    df.to_csv(path, index=False)
    print(f"[REPORT] Firmalar CSV çıktısı: {path}")

# PDF export için:
from fpdf import FPDF

def export_contacts_to_pdf(df, path="contacts_report.pdf"):
    """Contacts tablosunu sade bir PDF olarak kaydeder."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=8)
    col_width = pdf.w / (len(df.columns) + 1)
    row_height = pdf.font_size * 1.2
    # Başlıklar
    for col in df.columns:
        pdf.cell(col_width, row_height, str(col), border=1)
    pdf.ln(row_height)
    # Satırlar
    for i, row in df.iterrows():
        for val in row:
            pdf.cell(col_width, row_height, str(val), border=1)
        pdf.ln(row_height)
    pdf.output(path)
    print(f"[REPORT] PDF çıktısı kaydedildi: {path}")

def export_managers_to_pdf(df, path="managers_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=8)
    col_width = pdf.w / (len(df.columns) + 1)
    row_height = pdf.font_size * 1.2
    for col in df.columns:
        pdf.cell(col_width, row_height, str(col), border=1)
    pdf.ln(row_height)
    for i, row in df.iterrows():
        for val in row:
            pdf.cell(col_width, row_height, str(val), border=1)
        pdf.ln(row_height)
    pdf.output(path)
    print(f"[REPORT] PDF çıktısı kaydedildi: {path}")

def export_companies_to_pdf(df, path="companies_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=8)
    col_width = pdf.w / (len(df.columns) + 1)
    row_height = pdf.font_size * 1.2
    for col in df.columns:
        pdf.cell(col_width, row_height, str(col), border=1)
    pdf.ln(row_height)
    for i, row in df.iterrows():
        for val in row:
            pdf.cell(col_width, row_height, str(val), border=1)
        pdf.ln(row_height)
    pdf.output(path)
    print(f"[REPORT] PDF çıktısı kaydedildi: {path}")

# Örnek kullanım:
if __name__ == "__main__":
    import database
    df_contacts = database.get_all_contacts()
    export_contacts_to_excel(df_contacts)
    export_contacts_to_csv(df_contacts)
    export_contacts_to_pdf(df_contacts)

    df_managers = database.get_all_managers()
    export_managers_to_excel(df_managers)
    export_managers_to_csv(df_managers)
    export_managers_to_pdf(df_managers)

    df_companies = pd.read_sql("SELECT * FROM companies", sqlite3.connect("firms.db"))
    export_companies_to_excel(df_companies)
    export_companies_to_csv(df_companies)
    export_companies_to_pdf(df_companies)
