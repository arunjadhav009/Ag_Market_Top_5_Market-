import sys
import json
import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont

# फॉन्ट डाउनलोड करण्याचे फंक्शन (हिंदी आणि इंग्लिशसाठी)
def download_fonts():
    fonts = {
        "Roboto-Bold.ttf": "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf",
        "Roboto-Regular.ttf": "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf",
        "NotoSansDevanagari-Bold.ttf": "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Bold.ttf"
    }
    for name, url in fonts.items():
        if not os.path.exists(name):
            try:
                urllib.request.urlretrieve(url, name)
            except Exception as e:
                print(f"Error downloading {name}: {e}")

# मजकूर मध्यभागी (Center) आणण्यासाठी हेल्पर
def draw_centered_text(draw, xy, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((xy[0] - w/2, xy[1] - h/2 - 5), text, font=font, fill=fill)

def load_payload(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_market_image(state_data, output_path, post_date):
    # इमेजची साईझ (डार्क थीम)
    W, H = 1080, 1650
    img = Image.new('RGB', (W, H), color='#0c1017')
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("Roboto-Bold.ttf", 55)
        date_font = ImageFont.truetype("Roboto-Bold.ttf", 35)
        state_font = ImageFont.truetype("Roboto-Bold.ttf", 45)
        col_font = ImageFont.truetype("Roboto-Regular.ttf", 25)
        num_font = ImageFont.truetype("Roboto-Bold.ttf", 40)
        market_font = ImageFont.truetype("Roboto-Bold.ttf", 35)
        district_font = ImageFont.truetype("Roboto-Regular.ttf", 28)
        price_font = ImageFont.truetype("Roboto-Bold.ttf", 45)
        
        # शुद्ध हिंदी फॉन्ट
        hindi_font = ImageFont.truetype("NotoSansDevanagari-Bold.ttf", 35)
        fb_btn_font = ImageFont.truetype("Roboto-Bold.ttf", 45)
    except:
        print("Fonts not found, using default.")
        title_font = date_font = state_font = col_font = num_font = market_font = district_font = price_font = hindi_font = fb_btn_font = ImageFont.load_default()

    # 1. Top Red Header (लाल बॉक्स)
    draw.rounded_rectangle([40, 40, 1040, 180], radius=15, fill="#b91c1c")
    draw_centered_text(draw, (W/2, 90), "DAILY ONION MANDI RATES", title_font, "#ffffff")
    draw_centered_text(draw, (W/2, 145), f"DATE: {post_date} | TOP 5 MAXIMUM RATES", date_font, "#fca5a5")
    
    # 2. State Header (निळा बॉक्स)
    state_name = str(state_data.get('state', 'STATE')).upper()
    draw.rounded_rectangle([40, 210, 1040, 290], radius=15, fill="#0284c7")
    draw_centered_text(draw, (W/2, 250), f"{state_name} - TOP 5 HIGH RATES", state_font, "#ffffff")
    
    # 3. Column headers (कॉलमची नावे)
    draw.text((60, 320), "#", font=col_font, fill="#fbbf24")
    draw.text((120, 320), "DISTRICT & MARKET / MANDI", font=col_font, fill="#94a3b8")
    draw.text((850, 320), "MAX RATE", font=col_font, fill="#0284c7")
    
    # 4. Rows (टॉप ५ मार्केट्सची लिस्ट)
    start_y = 360
    row_height = 120
    spacing = 20
    
    markets = state_data.get('topMarkets', [])
    for idx, market in enumerate(markets[:5]):
        y = start_y + (idx * (row_height + spacing))
        
        # Row Background (डार्क ग्रे/निळा)
        draw.rounded_rectangle([40, y, 1040, y + row_height], radius=10, fill="#17202e")
        
        # Number Circle (निळा गोल)
        draw.ellipse([60, y + 25, 130, y + 95], fill="#0ea5e9")
        draw_centered_text(draw, (95, y + 60), str(idx + 1), num_font, "#ffffff")
        
        # Texts (मार्केट आणि जिल्हा)
        market_name = str(market.get('Market', ''))
        district = str(market.get('District', ''))
        max_price = str(market.get('MaxPrice', ''))
        
        draw.text((160, y + 25), market_name, font=market_font, fill="#ffffff")
        draw.text((160, y + 70), f"District: {district}", font=district_font, fill="#94a3b8")
        
        # Price (हिरव्या रंगात उजवीकडे)
        price_str = f"Rs. {max_price} /Qtl"
        bbox = draw.textbbox((0, 0), price_str, font=price_font)
        price_w = bbox[2] - bbox[0]
        draw.text((1000 - price_w, y + 40), price_str, font=price_font, fill="#4ade80")

    # 5. Bottom Ad box (पिवळ्या रंगाची बॉर्डर आणि शुद्ध हिंदी ॲड)
    ad_y = 1130
    draw.rounded_rectangle([40, ad_y, 1040, ad_y + 450], radius=15, outline="#fbbf24", width=3)
    
    hindi_text_1 = "क्या आप प्याज व्यापारी या किसान हैं और बाजार भाव जानना चाहते हैं?"
    hindi_text_2 = "आज ही हमारा फेसबुक पेज लाइक करें और पाएं ताजा भाव!"
    
    draw_centered_text(draw, (W/2, ad_y + 60), hindi_text_1, hindi_font, "#fbbf24")
    draw_centered_text(draw, (W/2, ad_y + 110), hindi_text_2, hindi_font, "#ffffff")
    
    # FB Button
    draw.rounded_rectangle([300, ad_y + 170, 780, ad_y + 260], radius=15, fill="#1877f2")
    draw_centered_text(draw, (W/2, ad_y + 215), "Facebook", fb_btn_font, "#ffffff")
    
    # Green Box & Page name
    draw.rectangle([250, ad_y + 300, 310, ad_y + 360], fill="#22c55e")
    draw.text((340, ad_y + 305), "Facebook Page : GREEN SOURCE", font=market_font, fill="#4ade80")
    draw.text((340, ad_y + 350), "Link in description / Bio me di gayi hai", font=district_font, fill="#94a3b8")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"Image saved successfully: {output_path}")

def main():
    if len(sys.argv) < 2:
        print("Error: Payload JSON file path required.")
        sys.exit(1)
        
    # रन होण्यापूर्वी फॉन्ट डाउनलोड करा
    download_fonts()
        
    json_file = sys.argv[1]
    payload = load_payload(json_file)
    
    data = payload.get('client_payload', payload)
    
    # तारखेचा फॉरमॅट घ्या
    post_date = str(data.get('date', ''))
    
    states_data = data.get('market_data', [data])
    if not isinstance(states_data, list):
        states_data = [states_data]
        
    for state_item in states_data:
        state_name = state_item.get('state', 'market').lower().replace(' ', '_')
        output_filename = f"generated_images/onion_rates_{state_name}.png"
        create_market_image(state_item, output_filename, post_date)

if __name__ == '__main__':
    main()
