import os
import requests
from bs4 import BeautifulSoup
import json
import bson
import pandas as pd

# --- 1️⃣ Web sayfasından veri çek ---
url = "https://yokatlas.yok.gov.tr/universite.php"
response = requests.get(url)
response.encoding = "utf-8"
soup = BeautifulSoup(response.text, "html.parser")

universiteler_full = []

for li in soup.select("li.unilist"):
    uni = {}
    uni["ad"] = li.select_one("h3.baslik").get_text(strip=True) if li.select_one("h3.baslik") else None
    uni["tur"] = li.select_one("span.tur").get_text(strip=True) if li.select_one("span.tur") else None
    uni["sehir"] = li.select_one("span.sehir").get_text(strip=True) if li.select_one("span.sehir") else None
    website = li.select_one("a[href^=http]")
    uni["website"] = website["href"] if website else None
    logo = li.select_one("img.logo")
    uni["logo"] = logo["src"] if logo else None
    adres_strong = li.find("strong", string="Adres: ")
    uni["adres"] = adres_strong.next_sibling.strip() if adres_strong and adres_strong.next_sibling else None
    universiteler_full.append(uni)

print("✅ Web’den çekilen toplam üniversite sayısı:", len(universiteler_full))

# --- 2️⃣ Klasörleri oluştur ---
main_folder = "universiteler_data"
full_folder = os.path.join(main_folder, "full")
names_folder = os.path.join(main_folder, "names")

os.makedirs(full_folder, exist_ok=True)
os.makedirs(names_folder, exist_ok=True)

# --- 3️⃣ Fonksiyon: JSON, BSON, CSV, Excel kaydet ---
def save_versions(data, folder, prefix):
    # JSON
    with open(os.path.join(folder, f"{prefix}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    # BSON
    with open(os.path.join(folder, f"{prefix}.bson"), "wb") as f:
        f.write(bson.BSON.encode({"universiteler": data}))
    # CSV ve Excel
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(folder, f"{prefix}.csv"), index=False, encoding="utf-8-sig")
    df.to_excel(os.path.join(folder, f"{prefix}.xlsx"), index=False)

# --- 4️⃣ Full veriler ---
save_versions(universiteler_full, full_folder, "universiteler_full")
print("✅ Full veriler kaydedildi.")

# --- 5️⃣ Sadece üniversite adları ---
universiteler_names = [{"ad": u["ad"]} for u in universiteler_full]
save_versions(universiteler_names, names_folder, "universiteler_names")
print("✅ Sadece üniversite adları kaydedildi.")
