from ai import generate_reply

questions = [
    'do u have the hoody in medium?',
    'whats your cheapest item?',
    'can you recommend a good gift under 40 dollars?',
]

for q in questions:
    print('CUSTOMER:', q)
    print('AI:', generate_reply(q))
    print('-' * 50)
