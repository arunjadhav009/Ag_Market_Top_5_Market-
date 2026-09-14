import sys
import json
import os
from PIL import Image, ImageDraw, ImageFont

def load_payload(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def create_market_image(state_data, output_path):
    # Create base image (Instagram portrait size: 1080x1350)
    img = Image.new('RGB', (1080, 1350), color='#f8f9fa')
    draw = ImageDraw.Draw(img)
    
    # Header Background
    draw.rounded_rectangle([40, 40, 1040, 180], radius=20, fill="#1b4332")
    
    try:
        title_font = ImageFont.truetype("usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
        sub_font = ImageFont.truetype("usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        table_font = ImageFont.truetype("usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        bold_table_font = ImageFont.truetype("usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        table_font = ImageFont.load_default()
        bold_table_font = ImageFont.load_default()

    # Titles
    draw.text((70, 70), f"कांदा बाजारभाव - {state_data.get('state', 'State')}", fill="#ffffff", font=title_font)
    draw.text((70, 125), f"दिनांक: {state_data.get('postDate', '')}", fill="#d8f3dc", font=sub_font)
    
    # Table Header Background
    draw.rounded_rectangle([40, 220, 1040, 300], radius=10, fill="#2d6a4f")
    
    draw.text((70, 245), "जिल्हा (District)", fill="#ffffff", font=bold_table_font)
    draw.text((380, 245), "बाजार समिती (Market)", fill="#ffffff", font=bold_table_font)
    draw.text((720, 245), "कमीत कमी", fill="#ffffff", font=bold_table_font)
    draw.text((890, 245), "जास्तीत जास्त", fill="#ffffff", font=bold_table_font)

    # Rows Data
    start_y = 330
    row_height = 80
    
    markets = state_data.get('topMarkets', [])
    for idx, market in enumerate(markets[:10]):  # Max top 10 rows
        y_pos = start_y + (idx * row_height)
        
        # Alternating row background
        bg_color = "#ffffff" if idx % 2 == 0 else "#e9f5ed"
        draw.rounded_rectangle([40, y_pos, 1040, y_pos + 70], radius=8, fill=bg_color)
        
        district = str(market.get('District', ''))
        market_name = str(market.get('Market', ''))
        min_price = str(market.get('MinPrice', ''))
        max_price = str(market.get('MaxPrice', ''))
        
        draw.text((70, y_pos + 20), district, fill="#212529", font=table_font)
        draw.text((380, y_pos + 20), market_name, fill="#212529", font=table_font)
        draw.text((720, y_pos + 20), f"Rs. {min_price}", fill="#2b9348", font=bold_table_font)
        draw.text((890, y_pos + 20), f"Rs. {max_price}", fill="#d90429", font=bold_table_font)

    # Footer
    draw.text((70, 1270), "Powered by Automated n8n & GitHub Workflow", fill="#6c757d", font=sub_font)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"Image saved successfully: {output_path}")

def main():
    if len(sys.argv) < 2:
        print("Error: Payload JSON file path required.")
        sys.exit(1)
        
    json_file = sys.argv[1]
    payload = load_payload(json_file)
    
    # Handle direct payload or workflow dispatch payload structure
    data = payload.get('client_payload', payload)
    
    # If data has states array or single state object
    states_data = data.get('market_data', [data])
    if not isinstance(states_data, list):
        states_data = [states_data]
        
    for state_item in states_data:
        state_name = state_item.get('state', 'market').lower().replace(' ', '_')
        output_filename = f"generated_images/onion_rates_{state_name}.png"
        create_market_image(state_item, output_filename)

if __name__ == '__main__':
    main()
