from PIL import Image

d = {'а': 22, 'б': 45, 'в': 71, 'г': 99, 'д': 124, 'е': 150, 'ж': 178, 'з': 203, 'и': 230}
column = [175, 200, 225, 253, 281, 308, 337, 363, 390]
row = [22, 45, 70, 98, 123, 149, 177, 202, 229]
img1 = Image.open('img_test.png').convert('RGBA')
for i in column:
    for j in row:
        img2 = Image.open(f'digits/7.png').convert('RGBA')
        img1.paste(img2, (i, j), img2)
        img1.save('img_test.png')
