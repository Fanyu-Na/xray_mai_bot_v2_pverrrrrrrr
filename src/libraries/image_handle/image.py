import base64
from io import BytesIO
from PIL import ImageFont, ImageDraw, Image
from src.libraries.GLOBAL_PATH import FONT_PATH

boy_friend_font_path = f"{FONT_PATH}/boy_friend.ttf"

def draw_text(img_pil, text, offset_x):
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(boy_friend_font_path, 48)
    width, height = draw.textsize(text, font)
    x = 5
    if width > 390:
        font = ImageFont.truetype(boy_friend_font_path, int(390 * 48 / width))
        width, height = draw.textsize(text, font)
    else:
        x = int((400 - width) / 2)
    draw.rectangle((x + offset_x - 2, 360, x + 2 + width + offset_x, 360 + height * 1.2), fill=(0, 0, 0, 255))
    draw.text((x + offset_x, 360), text, font=font, fill=(255, 255, 255, 255))


def text_to_image(text):
    font = ImageFont.truetype(boy_friend_font_path, 30)
    padding = 10
    margin = 4
    text_list = text.split('\n')
    max_width = 0
    for text in text_list:
        w, h = font.getsize(text)
        max_width = max(max_width, w)
    wa = max_width + padding * 2
    ha = h * len(text_list) + margin * (len(text_list) - 1) + padding * 2
    i = Image.new('RGB', (wa, ha), color=(255, 255, 255))
    draw = ImageDraw.Draw(i)
    for j in range(len(text_list)):
        text = text_list[j]
        draw.text((padding, padding + j * (margin + h)), text, font=font, fill=(0, 0, 0))
    return i

def image_to_base64(img, format='PNG'):
    output_buffer = BytesIO()
    img.save(output_buffer, format)
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return base64_str

# 辅助函数：分割文本以适应最大宽度  
def split_text_to_lines(text, max_width, font):  
    lines = []  
    current_line = ""  
    for char in text:  
        # 检查当前行的宽度加上新字符的宽度是否超过最大宽度  
        text_width, text_height = font.getsize(current_line + char)
        if text_width <= max_width:  
            current_line += char  
        else:  
            # 如果超过最大宽度，则将当前行添加到列表中，并开始新行  
            lines.append(current_line)  
            current_line = char  
    # 添加最后一行（如果有的话）  
    if current_line:
        lines.append(current_line)
    return "\n".join(lines)