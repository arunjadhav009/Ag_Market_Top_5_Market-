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
    W, H = 1080, 2400
    img = Image.new('RGB', (W, H), color='#0c1017')
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("Roboto-Bold.ttf", 52)
        date_font = ImageFont.truetype("Roboto-Bold.ttf", 32)
        state_font = ImageFont.truetype("Roboto-Bold.ttf", 38)
        col_font = ImageFont.truetype("Roboto-Regular.ttf", 24)
        num_font = ImageFont.truetype("Roboto-Bold.ttf", 32)
        market_font = ImageFont.truetype("Roboto-Bold.ttf", 30)
        district_font = ImageFont.truetype("Roboto-Regular.ttf", 24)
        price_font = ImageFont.truetype("Roboto-Bold.ttf", 38)
        hindi_font = ImageFont.truetype("NotoSansDevanagari-Bold.ttf", 30)
        fb_btn_font = ImageFont.truetype("Roboto-Bold.ttf", 40)
    except:
        title_font = date_font = state_font = col_font = num_font = market_font = district_font = price_font = hindi_font = fb_btn_font = ImageFont.load_default()

    # 1. मुख्य टॉप हेडर (लाल बॉक्स)
    draw.rounded_rectangle([40, 30, 1040, 145], radius=15, fill="#b91c1c")
    draw_centered_text(draw, (W/2, 70), "DAILY ONION MANDI RATES", title_font, "#ffffff")
    draw_centered_text(draw, (W/2, 115), f"DATE: {post_date} | TOP 5 MAXIMUM RATES", date_font, "#fca5a5")
    
    current_y = 175

    def draw_state_section(st_data, y_offset, is_orange_header=False):
        state_name = str(st_data.get('state', 'STATE')).upper()
        header_color = "#ea580c" if is_orange_header else "#0284c7"
        
        # वरच्या राज्यासाठी निळा, खालच्यासाठी ऑरेंज बॉक्स
        draw.rounded_rectangle([40, y_offset, 1040, y_offset + 65], radius=12, fill=header_color)
        draw_centered_text(draw, (W/2, y_offset + 32), f"{state_name} - TOP 5 HIGH RATES", state_font, "#ffffff")
        
        # कॉलम हेडिंग्स
        draw.text((60, y_offset + 75), "#", font=col_font, fill="#fbbf24")
        draw.text((120, y_offset + 75), "DISTRICT & MARKET / MANDI", font=col_font, fill="#94a3b8")
        draw.text((850, y_offset + 75), "MAX RATE", font=col_font, fill="#0284c7")
        
        row_y = y_offset + 110
        markets = st_data.get('topMarkets', [])
        
        for idx, market in enumerate(markets[:5]):
            draw.rounded_rectangle([40, row_y, 1040, row_y + 85], radius=8, fill="#17202e")
            
            circle_color = "#f59e0b" if is_orange_header else "#0ea5e9"
            draw.ellipse([60, row_y + 17, 115, row_y + 72], fill=circle_color)
            draw_centered_text(draw, (87, row_y + 44), str(idx + 1), num_font, "#ffffff")
            
            market_name = str(market.get('Market', ''))
            district = str(market.get('District', ''))
            max_price = str(market.get('MaxPrice', ''))
            
            draw.text((145, row_y + 16), market_name, font=market_font, fill="#ffffff")
            draw.text((145, row_y + 50), f"District: {district}", font=district_font, fill="#94a3b8")
            
            price_str = f"Rs. {max_price} /Qtl"
            bbox = draw.textbbox((0, 0), price_str, font=price_font)
            price_w = bbox[2] - bbox[0]
            draw.text((1000 - price_w, row_y + 22), price_str, font=price_font, fill="#4ade80")
            
            row_y += 95
            
        return row_y

    # २. पहिले राज्य प्रिंट करा
    if state_1 and len(state_1.get('topMarkets', [])) > 0:
        current_y = draw_state_section(state_1, current_y, is_orange_header=False)
        current_y += 15

    # ३. दुसरे राज्य त्याच्या खाली प्रिंट करा
    if state_2 and len(state_2.get('topMarkets', [])) > 0:
        current_y = draw_state_section(state_2, current_y, is_orange_header=True)
        current_y += 20

    # ४. तळाची हिंदी ॲड बॉक्स
    ad_y = current_y
    draw.rounded_rectangle([40, ad_y, 1040, ad_y + 340], radius=15, outline="#fbbf24", width=3)
    
    hindi_text_1 = "क्या आप सभी राज्यों के पूरे भाव देखना चाहते हैं?"
    hindi_text_2 = "देश की सभी मंडियों के दैनिक रेट्स के लिए पेज को फॉलो करें!"
    
    draw_centered_text(draw, (W/2, ad_y + 45), hindi_text_1, hindi_font, "#fbbf24")
    draw_centered_text(draw, (W/2, ad_y + 85), hindi_text_2, hindi_font, "#ffffff")
    
    # Facebook Button
    draw.rounded_rectangle([300, ad_y + 125, 780, ad_y + 200], radius=12, fill="#1877f2")
    draw_centered_text(draw, (W/2, ad_y + 162), "Facebook", fb_btn_font, "#ffffff")
    
    # Green Box & Page name
    draw.rectangle([210, ad_y + 225, 270, ad_y + 285], fill="#22c55e")
    draw.text((295, ad_y + 230), "Facebook Page : GREEN SOURCE", font=market_font, fill="#4ade80")
    draw.text((295, ad_y + 268), "Link in description / Bio me di gayi hai", font=district_font, fill="#94a3b8")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"Combined 10-market image saved successfully: {output_path}")

def main():
    if len(sys.argv) < 2:
        print("Error: Payload JSON file path required.")
        sys.exit(1)
        
    download_fonts()
        
    json_file = sys.argv[1]
    payload = load_payload(json_file)
    data = payload.get('client_payload', payload)
    post_date = str(data.get('date', ''))
    
    raw_market_data = data.get('market_data', [])
    states_data = []
    if isinstance(raw_market_data, list):
        states_data = raw_market_data
    elif isinstance(raw_market_data, dict):
        states_data = [raw_market_data]
        
    if len(states_data) == 1 and "market_data" in states_data[0]:
        states_data = states_data[0]["market_data"]

    # दोन-दोन राज्यांची जोडी करून एकाच इमेजवर १० मार्केट तयार करणे
    if len(states_data) >= 2:
        for i in range(0, len(states_data) - 1, 2):
            st1 = states_data[i]
            st2 = states_data[i+1]
            
            name1 = str(st1.get('state', 'market1')).lower().replace(' ', '_')
            name2 = str(st2.get('state', 'market2')).lower().replace(' ', '_')
            
            output_filename = f"generated_images/onion_rates_{name1}_and_{name2}.png"
            create_combined_market_image(st1, st2, output_filename, post_date)
            
        if len(states_data) % 2 != 0:
            st1 = states_data[-1]
            name1 = str(st1.get('state', 'market1')).lower().replace(' ', '_')
            output_filename = f"generated_images/onion_rates_{name1}_single.png"
            create_combined_market_image(st1, {}, output_filename, post_date)
            
    elif len(states_data) == 1:
        st1 = states_data[0]
        name1 = str(st1.get('state', 'market1')).lower().replace(' ', '_')
        output_filename = f"generated_images/onion_rates_{name1}.png"
        create_combined_market_image(st1, {}, output_filename, post_date)

if __name__ == '__main__':
    main()
