from ai import generate_response

cases = [
    'I will take the hoodie in medium!',
    'I want to buy the hoodie',
]

for c in cases:
    r = generate_response(c)
    print('CUSTOMER:', c)
    print('  intent :', r['intent'])
    print('  product:', repr(r['product']))
    print('  variant:', repr(r['variant']))
    print('  reply  :', r['reply'])
    print('-' * 55)
