import sys
import json
import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont

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

def draw_centered_text(draw, xy, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((xy[0] - w/2, xy[1] - h/2 - 5), text, font=font, fill=fill)

def load_payload(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_combined_market_image(state_1, state_2, output_path, post_date):
    # एकाच इमेजमध्ये दोन राज्य बसवण्यासाठी उंची (Height) वाढवली आहे
    W, H = 1080, 2400
    img = Image.new('RGB', (W, H), color='#0c1017')
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("Roboto-Bold.ttf", 55)
        date_font = ImageFont.truetype("Roboto-Bold.ttf", 35)
        state_font = ImageFont.truetype("Roboto-Bold.ttf", 40)
        col_font = ImageFont.truetype("Roboto-Regular.ttf", 25)
        num_font = ImageFont.truetype("Roboto-Bold.ttf", 35)
        market_font = ImageFont.truetype("Roboto-Bold.ttf", 32)
        district_font = ImageFont.truetype("Roboto-Regular.ttf", 26)
        price_font = ImageFont.truetype("Roboto-Bold.ttf", 40)
        hindi_font = ImageFont.truetype("NotoSansDevanagari-Bold.ttf", 32)
        fb_btn_font = ImageFont.truetype("Roboto-Bold.ttf", 42)
    except:
        title_font = date_font = state_font = col_font = num_font = market_font = district_font = price_font = hindi_font = fb_btn_font = ImageFont.load_default()

    # 1. मुख्य टॉप हेडर्स (लाल बॉक्स)
    draw.rounded_rectangle([40, 40, 1040, 160], radius=15, fill="#b91c1c")
    draw_centered_text(draw, (W/2, 80), "DAILY ONION MANDI RATES", title_font, "#ffffff")
    draw_centered_text(draw, (W/2, 130), f"DATE: {post_date} | TOP 5 MAXIMUM RATES", date_font, "#fca5a5")
    
    current_y = 190

    # फंक्शन: एका राज्याचा डेटा टेबल फॉरमॅटमध्ये टाकण्यासाठी
    def draw_state_section(st_data, y_offset, is_orange_header=False):
        state_name = str(st_data.get('state', 'STATE')).upper()
        header_color = "#ea580c" if is_orange_header else "#0284c7"
        
        # स्टेटचे नाव (निळा किंवा भगवा बॉक्स)
        draw.rounded_rectangle([40, y_offset, 1040, y_offset + 70], radius=12, fill=header_color)
        draw_centered_text(draw, (W/2, y_offset + 35), f"{state_name} - TOP 5 HIGH RATES", state_font, "#ffffff")
        
        # कॉलम हेडिंग्स
        draw.text((60, y_offset + 85), "#", font=col_font, fill="#fbbf24")
        draw.text((120, y_offset + 85), "DISTRICT & MARKET / MANDI", font=col_font, fill="#94a3b8")
        draw.text((850, y_offset + 85), "MAX RATE", font=col_font, fill="#0284c7")
        
        row_y = y_offset + 125
        markets = st_data.get('topMarkets', [])
        
        for idx, market in enumerate(markets[:5]):
            # प्रत्येक मार्केटची रो (Row)
            draw.rounded_rectangle([40, row_y, 1040, row_y + 95], radius=8, fill="#17202e")
            
            # नंबरचा गोल (पिवळा किंवा निळा)
            circle_color = "#f59e0b" if is_orange_header else "#0ea5e9"
            draw.ellipse([60, row_y + 20, 120, row_y + 80], fill=circle_color)
            draw_centered_text(draw, (90, row_y + 50), str(idx + 1), num_font, "#ffffff")
            
            market_name = str(market.get('Market', ''))
            district = str(market.get('District', ''))
            max_price = str(market.get('MaxPrice', ''))
            
            draw.text((150, row_y + 20), market_name, font=market_font, fill="#ffffff")
            draw.text((150, row_y + 58), f"District: {district}", font=district_font, fill="#94a3b8")
            
            price_str = f"Rs. {max_price} /Qtl"
            bbox = draw.textbbox((0, 0), price_str, font=price_font)
            price_w = bbox[2] - bbox[0]
            draw.text((1000 - price_w, row_y + 28), price_str, font=price_font, fill="#4ade80")
            
            row_y += 105
            
        return row_y

    # पहिले राज्य प्रिंट करा (निळा बॉक्स)
    if len(state_1) > 0:
        current_y = draw_state_section(state_1, current_y, is_orange_header=False)
        current_y += 20 # दोन राज्यांमधील अंतर

    # दुसरे राज्य प्रिंट करा (भगवा/ऑरेंज बॉक्स - हुबेहूब तुमच्या दुसऱ्या फोटोसारखा)
    if len(state_2) > 0:
        current_y = draw_state_section(state_2, current_y, is_orange_header=True)
        current_y += 30

    # तळाची हिंदी ॲड (Ad Box)
    ad_y = current_y
    draw.rounded_rectangle([40, ad_y, 1040, ad_y + 380], radius=15, outline="#fbbf24", width=3)
    
    hindi_text_1 = "क्या आप प्याज व्यापारी या किसान हैं और बाजार भाव जानना चाहते हैं?"
    hindi_text_2 = "आज ही हमारा फेसबुक पेज लाइक करें और पाएं ताजा भाव!"
    
    draw_centered_text(draw, (W/2, ad_y + 50), hindi_text_1, hindi_font, "#fbbf24")
    draw_centered_text(draw, (W/2, ad_y + 95), hindi_text_2, hindi_font, "#ffffff")
    
    # Facebook Button
    draw.rounded_rectangle([300, ad_y + 140, 780, ad_y + 220], radius=12, fill="#1877f2")
    draw_centered_text(draw, (W/2, ad_y + 180), "Facebook", fb_btn_font, "#ffffff")
    
    # Green Box & Page name
    draw.rectangle([250, ad_y + 250, 305, ad_y + 305], fill="#22c55e")
    draw.text((330, ad_y + 252), "Facebook Page : GREEN SOURCE", font=market_font, fill="#4ade80")
    draw.text((330, ad_y + 292), "Link in description / Bio me di gayi hai", font=district_font, fill="#94a3b8")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"Combined image saved successfully: {output_path}")

def main():
    if len(sys.argv) < 2:
        print("Error: Payload JSON file path required.")
        sys.exit(1)
        
    download_fonts()
        
    json_file = sys.argv[1]
    payload = load_payload(json_file)
    data = payload.get('client_payload', payload)
    post_date = str(data.get('date', ''))
    
    states_data = data.get('market_data', [])
    if not isinstance(states_data, list):
        states_data = [states_data]
        
    # जर डेटा एकापेक्षा जास्त राज्यांचा असेल, तर त्यांना जोड्यांमध्ये (२-२ च्या जोड्या) एकाच इमेजमध्ये टाका
    if len(states_data) >= 2:
        for i in range(0, len(states_data) - 1, 2):
            st1 = states_data[i]
            st2 = states_data[i+1]
            
            name1 = st1.get('state', 'market1').lower().replace(' ', '_')
            name2 = st2.get('state', 'market2').lower().replace(' ', '_')
            
            output_filename = f"generated_images/onion_rates_{name1}_and_{name2}.png"
            create_combined_market_image(st1, st2, output_filename, post_date)
    elif len(states_data) == 1:
        # समजा एखाद्या वेळी एकच राज्य असेल तर
        st1 = states_data[0]
        name1 = st1.get('state', 'market1').lower().replace(' ', '_')
        output_filename = f"generated_images/onion_rates_{name1}.png"
        create_combined_market_image(st1, {}, output_filename, post_date)

if __name__ == '__main__':
    main()
