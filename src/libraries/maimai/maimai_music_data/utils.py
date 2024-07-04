def truncate_text(text, font, max_width):
    if font.getsize(text)[0] <= max_width:
        return text
    else:
        for i in range(len(text), 0, -1):
            if font.getsize(text[:i] + '...')[0] <= max_width:
                return text[:i] + '...'
        return '...'
    
def decimalPoints(num,count):
    num = str(int(round(num * 10**count,8)) / 10**count)  
    if '.0' == num[-2:]:
        num += ('0'* (count-1-(len(num.split('.')[1]))))
    if len(num.split('.')[1]) < count:
        num += ('0'* (count-(len(num.split('.')[1]))))
    return num
