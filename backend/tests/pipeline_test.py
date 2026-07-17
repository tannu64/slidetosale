from orchestrator import handle_message

cases = [
    'I will take the hoodie in medium!',
    'I want to buy the hoodie',
    'nice store!',
]

for c in cases:
    result = handle_message(c)
    print('CUSTOMER:', c)
    print('  intent :', result['intent'])
    print('  link   :', result['checkout_link'])
    print('  reply  :', result['reply'])
    print('=' * 60)
