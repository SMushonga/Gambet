from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from fantasy_chess import db, bcrypt
from fantasy_chess.models import User, User_Product, Product
import stripe, json
from fantasy_chess.config import Config


stripe.api_key= Config.STRIPE_SECRET_KEY

payments = Blueprint('payments', __name__)

@payments.route('/memberships', methods=['GET', 'POST'])
def memberships():
    subscriptions = Product.query.filter_by(subscription=True).all()
    if request.method == 'POST':
        return redirect(url_for('membership', product_id=request.form.get('submit')))
    render_template('memberships.html', subscriptions=subscriptions)


@payments.route('/membership/<int: product_id>', methods=['POST'])
def membership(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': product.stripe_price_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url= url_for('payment.success'),
            cancel_url= url_for('payment.cancel'),
        )
    except Exception as e:
        print(e)
        flash('Something went wrong, try again later', 'failure')
        return redirect(url_for('payments.memberships'))

    return redirect(checkout_session.url, code=303)

@payments.route('/league_entry/<int: product_id>', methods=['POST'])
def league_entry(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': product.stripe_price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url= url_for('payment.success'),
            cancel_url= url_for('payment.cancel'),
        )
    except Exception as e:
        print(e)
        flash('Something went wrong, try again later', 'failure')
        return redirect(url_for('fantasy.home'))

    return redirect(checkout_session.url, code=303)

endpoint_secret = ''
@payments.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data
    try:
        event = json.loads(payload)
    except:
        print('⚠️  Webhook error while parsing basic request.' + str(e))
        return jsonify(success=False)
    if endpoint_secret:
        # Only verify the event if there is an endpoint secret defined
        # Otherwise use the basic event deserialized with json
        sig_header = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except stripe.error.SignatureVerificationError as e:
            print('⚠️  Webhook signature verification failed.' + str(e))
            return jsonify(success=False)

    # Handle the event
    if event and event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']  # contains a stripe.PaymentIntent
        print('Payment for {} succeeded'.format(payment_intent['amount']))
        # Then define and call a method to handle the successful payment intent.
        # handle_payment_intent_succeeded(payment_intent)
    elif event['type'] == 'payment_method.attached':
        payment_method = event['data']['object']  # contains a stripe.PaymentMethod
        # Then define and call a method to handle the successful attachment of a PaymentMethod.
        # handle_payment_method_attached(payment_method)
    else:
        # Unexpected event type
        print('Unhandled event type {}'.format(event['type']))

    return jsonify(success=True)