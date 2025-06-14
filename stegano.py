# Jakub Opólski
import sys
import argparse
import re

def read_message_bits(filename):
    with open(filename, 'r') as f:
        hexstr = f.read().strip().replace('\n', '')
    bits = []
    for c in hexstr:
        b = bin(int(c, 16))[2:].zfill(4)
        bits.extend([int(x) for x in b])
    return bits

def bits_to_hex(bits):
    hexstr = ''
    for i in range(0, len(bits), 4):
        chunk = bits[i:i+4]
        if len(chunk) < 4:
            chunk += [0] * (4 - len(chunk))
        val = int(''.join(str(b) for b in chunk), 2)
        hexstr += format(val, 'x')
    return hexstr

def clean_cover(cover, method):
    if method == 1:
        cover = '\n'.join(line.rstrip() for line in cover.splitlines())
        return cover
    elif method == 2:
        cover = re.sub(r' {2,}', ' ', cover)
    elif method == 3:
        cover = re.sub(r'lineheight\s*:', 'line-height:', cover)
        cover = re.sub(r'margin-botom\s*:', 'margin-bottom:', cover)
        return cover
    elif method == 4:
        cover = re.sub(r'(<font[^>]*>)\1', r'\1', cover)
        cover = re.sub(r'(<font[^>]*>)</font>\1', r'\1', cover)
        return cover
    return cover

def embed_1(cover, bits):
    lines = cover.splitlines()
    if len(bits) > len(lines):
        raise ValueError("nośnik jest za mały do przekazania całej wiadomości")
    return '\n'.join(line + (' ' if i < len(bits) and bits[i] else '') 
                    for i, line in enumerate(lines))

def detect_1(watermark):
    bits = [1 if line.endswith(' ') else 0 for line in watermark.splitlines()]
    while bits and bits[-1] == 0:
        bits.pop()
    return bits

def embed_2(cover, bits):
    spaces = [m.start() for m in re.finditer(r'(?<! ) (?! )', cover)]
    if len(bits) > len(spaces):
        raise ValueError("nośnik jest za mały do przekazania całej wiadomości")
    
    result = list(cover)
    for i, pos in enumerate(spaces[:len(bits)]):
        if bits[i]:
            result[pos] = '  '
    return ''.join(result)

def detect_2(watermark):
    bits = []
    for m in re.finditer(r' {1,2}', watermark):
        space = m.group(0)
        if space == ' ':
            bits.append(0)
        elif space == '  ':
            bits.append(1)
    while bits and bits[-1] == 0:
        bits.pop()
    return bits

def embed_3(cover, bits):
    p_tags = list(re.finditer(r'<p\b[^>]*style\s*=\s*["\'][^"\']*["\'][^>]*>', cover))
    if len(bits) > len(p_tags):
        raise ValueError("nośnik jest za mały do przekazania całej wiadomości")
    
    result = []
    last_pos = 0
    for i, m in enumerate(p_tags):
        tag = m.group(0)
        result.append(cover[last_pos:m.start()])
        
        if i < len(bits):
            if bits[i]:
                modified_tag = tag.replace('style="margin-bottom: 0cm; line-height: 100%"', 'style="margin-bottom: 0cm; lineheight: 100%"')
                modified_tag = modified_tag.replace('style=\'', 'style=\'lineheight:100%;')
            else:
                modified_tag = tag.replace('style="margin-bottom: 0cm; line-height: 100%"', 'style="margin-botom: 0cm; line-height: 100%"')
                modified_tag = modified_tag.replace('style=\'', 'style=\'margin-botom:0cm;')
            result.append(modified_tag)
        else:
            result.append(tag)
            
        last_pos = m.end()
    
    result.append(cover[last_pos:])
    return ''.join(result)

def detect_3(watermark):
    bits = []
    for m in re.finditer(r'<p\b[^>]*style\s*=\s*["\'][^"\']*["\'][^>]*>', watermark):
        style = m.group(0)
        if 'lineheight' in style:
            bits.append(1)
        elif 'margin-botom' in style:
            bits.append(0)
    while bits and bits[-1] == 0:
        bits.pop()
    return bits

def embed_4(cover, bits):
    font_tags = list(re.finditer(r'<font\b[^>]*>', cover))
    if len(bits) > len(font_tags):
        raise ValueError("nośnik jest za mały do przekazania całej wiadomości")

    result = []
    last_pos = 0

    for i, m in enumerate(font_tags):
        result.append(cover[last_pos:m.end()])
        last_pos = m.end()

        if i < len(bits):
            tag = m.group(0)
            if bits[i]:
                result.append(f"</font>{tag}")
            else:
                result.append("</font><font></font>")

    result.append(cover[last_pos:])
    return ''.join(result)

def detect_4(watermark):
    bits = []
    pattern = re.compile(r'<font\b[^>]*>(.*?)</font>', re.DOTALL)
    pos = 0

    while pos < len(watermark):
        match = pattern.search(watermark, pos)
        if not match:
            break

        end = match.end()

        after = watermark[end:end+50]
        if after.startswith('<font></font>'):
            bits.append(0)
            pos = end + len('<font></font>')
        elif re.match(r'<font\b[^>]*>', after):
            bits.append(1)
            next_tag = re.match(r'<font\b[^>]*>', after)
            pos = end + next_tag.end()
        else:
            pos = end

    return bits

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-e', action='store_true', help='embed')
    group.add_argument('-d', action='store_true', help='detect')
    
    method = parser.add_mutually_exclusive_group(required=True)
    method.add_argument('-1', action='store_true', help='method 1')
    method.add_argument('-2', action='store_true', help='method 2')
    method.add_argument('-3', action='store_true', help='method 3')
    method.add_argument('-4', action='store_true', help='method 4')
    
    args = parser.parse_args()
    
    method_num = 1 if args.__dict__['1'] else \
                2 if args.__dict__['2'] else \
                3 if args.__dict__['3'] else 4
    
    if args.e:
        bits = read_message_bits('mess.txt')
        with open('cover.html', 'r', encoding='utf-8') as f:
            cover = clean_cover(f.read(), method_num)
        
        embed_func = [embed_1, embed_2, embed_3, embed_4][method_num-1]
        try:
            watermark = embed_func(cover, bits)
        except ValueError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
        
        with open('watermark.html', 'w', encoding='utf-8') as f:
            f.write(watermark)
    else:
        with open('watermark.html', 'r', encoding='utf-8') as f:
            watermark = f.read()
        
        detect_func = [detect_1, detect_2, detect_3, detect_4][method_num-1]
        bits = detect_func(watermark)
        
        with open('detect.txt', 'w') as f:
            f.write(bits_to_hex(bits))

if __name__ == '__main__':
    main()