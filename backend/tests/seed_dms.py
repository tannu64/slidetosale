import requests, time

URL = 'http://127.0.0.1:8000/simulate-dm'

dms = [
    ('sarah_k', 'I will take the hoodie in medium!'),
    ('mike_92', 'I want the black t-shirt in small'),
    ('lena.style', 'can I get the slim fit jeans in size 32?'),
    ('tomreyes', 'I will take the leather crossbody bag in black'),
    ('ayesha_w', 'do you have the hoodie in small? I want to buy it'),
    ('daniela.m', 'how much is the face serum?'),
    ('kev_in', 'is the white t-shirt available in medium?'),
    ('priya.shops', 'love your store! so cute'),
    ('noah_b', 'do you ship internationally?'),
    ('emma.rose', 'I want the navy t-shirt in small please'),
    ('jaydev', 'whats your cheapest item?'),
    ('lucia_m', 'I will take the cotton t-shirt in white medium'),
]

for cid, text in dms:
    r = requests.post(URL, json={'customer_id': cid, 'text': text})
    d = r.json()
    tag = 'LINK' if d.get('checkout_link') else '----'
    intent = d.get('intent', '?')
    print(f'[{tag}] {intent:6} | {cid:12} | {text[:40]}')
    time.sleep(0.4)

print('\nDone seeding DMs.')
