import stripe
from fantasy_chess.config import Config
from fantasy_chess.models import Product, League


stripe.api_key= Config.STRIPE_SECRET_KEY

#populate products 
def insert_products():
    product = Product(title='Basic Membership', description='Monthly Subscription to Basic Memberhsip', cost=10, subscription=True, stripe_price_id='price_1MFephBnteUfgja4oSQj8Aza')
    product = Product(title='Basic Membership', description='Yearly Subscription to Basic Membership', cost=80, subscription=True, stripe_price_id='price_1MFephBnteUfgja4ctS0YiAa')
    product = Product(title='Yearly Membership', description='Monthly Subscription to Premium Membership', cost=20, subscription=True, stripe_price_id='price_1MFekFBnteUfgja4QzmmOYN4')
    product = Product(title='Yearly Membership', description='Yearly Subscription to Premium Membership', cost=160, subscription=True, stripe_price_id='price_1MFekFBnteUfgja4dcS60Y82')

def create_product_for_league(league_id, cost_in_cents:int):
    league = League.query.get(league_id)
    if not league: return False
    product_object = stripe.Product.create(name=f"{league.title}",
        default_price_data = {
            'currency': 'usd',
            'unit_amount': cost_in_cents,
        },
        metadata = {
            'key':'value'
        })
    #There is the scenario where there is an error, for now we ignore this - to be fixed later
    try:
        league_entry = Product(title=f'{league.title}', description=f'entry to {league.title} league', cost=cost_in_cents, stripe_price_id=product_object['default_price'], stripe_product_id=product_object['id'],league=league)
        return True
    except:
        return False