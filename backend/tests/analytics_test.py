from analytics import get_analytics

for window in [30, 7]:
    a = get_analytics(merchant_id=1, days=window)
    print(f'--- Last {window} days ---')
    print('  DM volume       :', a['dm_volume'])
    print('  High intent     :', a['high_intent'])
    print('  Checkout starts :', a['checkout_starts'])
    print('  Checkout clicks :', a['checkout_clicks'])
    print('  Orders          :', a['orders'])
    print('  Revenue         : $', a['revenue'])
    print()
