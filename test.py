def string_to_grid(s, s2):
    res = []
    res2 = []
    for i in range(9):
        res.append(s[i * 9:i * 9 + 9])

    for i in range(9):
        res2.append(s2[i * 9:i * 9 + 9])
    return res, res2


def get_number(inp):
    out = []
    d = {'а': 0, 'б': 1, 'в': 2, 'г': 3, 'д': 4, 'е': 5, 'ж': 6, 'з': 7, 'и': 8}
    for i in range(len(inp)):
        if not len(out):
            if inp[i].isalpha():
                if len(inp[i]) == 1 and 'а' <= inp[i] <= 'и' and inp[i] != 'ё':
                    out.append(d[inp[i]])
                    continue
        if inp[i].isdigit() and len(out):
            out.append(int(inp[i]))
    print(out)
    return [out[1], out[0] + 1, int(out[2])]


out = get_number('Г 6 3'.lower().split())


a = '.6.3.9.41..5.27..9.93.4.7.69.8.6...2521..83.4...2519....2.146...3..7..18.849.627.'
b = '267389541415627839893145726978463152521798364346251987752814693639572418184936275'
a, b = string_to_grid(a, b)
a[out[1] - 1] = a[out[1] - 1][:out[0] - 1] + str(out[2]) + \
                          a[out[1] - 1][out[0]:]
print(a)
out = out[:min(3, len(out))]
print(out)
print(a[out[1] - 1][out[0] - 1])
print(b[out[1] - 1][out[0] - 1])
print(out[2])

print(a)
print(b)
print(len('.6.3.9.41..5.27..9.93.4.7.69.8.6...2521..83.4...2519....2.146...3..7..18.849.627.'))

