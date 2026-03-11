import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# بارگذاری تنظیمات از فایل .env
load_dotenv()

# ساخت Connection String
DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DB_URL)

def clean_data(df, direction):
    # ۱. حذف ستون‌های Unnamed و موارد غیرضروری که گفتی
    cols_to_drop = [c for c in df.columns if 'Unnamed' in c or '...' in c]
    df = df.drop(columns=cols_to_drop)
    
    # ۲. استانداردسازی نام ستون‌ها (حذف فاصله، پرانتز و تبدیل به حروف کوچک)
    # مثال: 'Cntr No' -> 'cntr_no'
    df.columns = [
        col.strip()
        .replace(' ', '_')
        .replace('/', '_')
        .replace('(', '')
        .replace(')', '')
        .replace('.', '')
        .lower() 
        for col in df.columns
    ]
    
    # ۳. اضافه کردن ستون جهت بار (Import/Export)
    df['shipment_direction'] = direction
    return df

def run_migration():
    import_path = "data/Import.xlsx"
    export_path = "data/Export.xlsx"
    
    all_data = []

    # ۱. خواندن و تمیزکاری هر دو فایل و ریختن در یک لیست
    if os.path.exists(import_path):
        df_i = pd.read_excel(import_path)
        all_data.append(clean_data(df_i, 'Import'))

    if os.path.exists(export_path):
        df_e = pd.read_excel(export_path)
        all_data.append(clean_data(df_e, 'Export'))

    if not all_data:
        print("No files found!")
        return

    # ۲. ترکیب هر دو دیتافریم (پانداز ستون‌های مشترک و غیرمشترک را مدیریت می‌کند)
    final_df = pd.concat(all_data, ignore_index=True)

    # ۳. حذف و بازسازی جدول با تمام ستون‌های موجود در هر دو فایل
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS shipments;"))
        conn.commit()

    # ۴. انتقال کل داده‌ها به صورت یکجا
    try:
        final_df.to_sql('shipments', con=engine, if_exists='replace', index=False)
        print(f"Migration successful! Total rows: {len(final_df)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_migration()