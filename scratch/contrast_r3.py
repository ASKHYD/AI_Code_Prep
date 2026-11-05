def lum(hex_str):
    hex_str = hex_str.lstrip('#')
    r, g, b = [int(hex_str[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    def adj(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * adj(r) + 0.7152 * adj(g) + 0.0722 * adj(b)

def contrast(c1, c2):
    l1, l2 = lum(c1), lum(c2)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)

paper = '#FBFAF7'
surface = '#FFFFFF'
ink = '#171712'

print(f"Ink on Paper: {contrast(ink, paper):.2f}:1")
print(f"Ink on Surface: {contrast(ink, surface):.2f}:1")

print("\nMuted warm grey candidates on paper:")
for g in ['#716E65', '#66635A', '#5E5B52', '#59564D', '#525047']:
    print(f"  {g} on {paper}: {contrast(g, paper):.2f}:1")

print("\nPrimary CTA Green candidates:")
for gr in ['#1F9D63', '#16A34A', '#15803D', '#1B8A56', '#177A4B']:
    print(f"  {gr}: on White={contrast(gr, '#FFFFFF'):.2f}:1, with White text={contrast('#FFFFFF', gr):.2f}:1, with Ink={contrast(gr, ink):.2f}:1")

print("\nTint Pairs (Saturated partner text on Tint wash background):")
tints = [
    ('Mint/Green', '#DFF3E4', '#167B48', '#1F9D63'),
    ('Butter/Amber', '#FFF0C4', '#B45309', '#B45309'),
    ('Sky/Blue', '#DCEBFF', '#1D5EC2', '#2273E6'),
    ('Lilac/Violet', '#E8E2FF', '#5932EA', '#6C4CF1'),
    ('Peach/Coral', '#FFE8D1', '#C83B10', '#E4572E'),
    ('Rose/Red', '#FFE0E0', '#C5221F', '#D92D20'),
]

for name, wash, partner_text, partner_fill in tints:
    c_text = contrast(partner_text, wash)
    c_fill = contrast(partner_fill, wash)
    c_ink = contrast(ink, wash)
    print(f"  {name:15}: wash={wash} | partner_text={partner_text} ({c_text:.2f}:1) | partner_fill={partner_fill} ({c_fill:.2f}:1) | ink on wash={c_ink:.2f}:1")

print("\nEditor Inset:")
print(f"  Code text #F2F2ED on #14161A = {contrast('#F2F2ED', '#14161A'):.2f}:1")
