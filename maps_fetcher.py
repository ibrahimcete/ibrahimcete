# maps_fetcher.py
import requests
from config import GOOGLE_MAPS_API_KEY

def fetch_companies_from_maps(query, location, num=10):
    """
    Google Maps Places API ile verilen query ve location için firma arar,
    her firma için place_id ile detaylarını çeker.
    """
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{query} in {location}",
        "key": GOOGLE_MAPS_API_KEY
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
    except Exception as e:
        print(f"[ERROR] Google Maps API isteği başarısız: {e}")
        return []

    companies = []
    results = data.get("results", [])
    if not results:
        print("[INFO] Google Maps sonucu bulunamadı.")
        return []

    for result in results[:num]:
        place_id = result.get("place_id")
        if not place_id:
            continue

        # Place Details API ile daha fazla bilgi çekiyoruz
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        details_params = {
            "place_id": place_id,
            "fields": "name,formatted_address,website,url,international_phone_number,formatted_phone_number,opening_hours,rating,user_ratings_total,review",
            "key": GOOGLE_MAPS_API_KEY
        }
        try:
            details_resp = requests.get(details_url, params=details_params, timeout=15)
            details_data = details_resp.json()
            details = details_data.get("result", {})
        except Exception as e:
            print(f"[ERROR] Place Details API hatası: {e}")
            details = {}

        company = {
            "name": details.get("name") or result.get("name"),
            "address": details.get("formatted_address") or result.get("formatted_address"),
            "website": details.get("website", ""),
            "maps_url": details.get("url") or f"https://www.google.com/maps/place/?q=place_id:{place_id}",
            "phone": details.get("international_phone_number") or details.get("formatted_phone_number") or "",
            "rating": details.get("rating", ""),
            "reviews": details.get("user_ratings_total", 0),
            "opening_hours": details.get("opening_hours", {}),
            "place_id": place_id
        }
        companies.append(company)

    return companies

# ŞABLON: Alternatif kaynak (örn. Foursquare) eklemek için altyapı
def fetch_from_foursquare(query, location, num=10, api_key=None):
    """
    Foursquare API ile firma arama şablonu.
    İstersen gerçek Foursquare API key ve endpoint ile doldurabilirsin.
    """
    # Foursquare API kodu buraya
    return []

# Tüm kaynakları birleştirip tek listede dönen fonksiyon (şu an sadece Google aktif)
def fetch_from_all_sources(query, location, num=10):
    """
    Google Maps ve ileride eklenen diğer kaynaklardan firmaları toplar,
    birleşik sonuç döner.
    """
    companies = fetch_companies_from_maps(query, location, num)
    # foursquare_results = fetch_from_foursquare(query, location, num)
    # companies.extend(foursquare_results)
    # Diğer kaynaklar için yukarıdaki gibi eklemeler yapabilirsin.
    return companies

