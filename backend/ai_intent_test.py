from ai import generate_response

messages = [
    'I will take the hoodie in medium!',
    'I want the black t-shirt in small',
    'do you have the jeans in size 32?',
    'nice store, cute stuff',
]

for m in messages:
    result = generate_response(m)
    print('CUSTOMER:', m)
    print('INTENT: ', result['intent'])
    print('REPLY:  ', result['reply'])
    print('-' * 50)
