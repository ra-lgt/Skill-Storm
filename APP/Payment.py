import os
from flask import Flask, render_template, abort, redirect, request
import stripe


class Payment:
    def create_payment_stripe(self,data,Admin,Host):
        url=''
        name=''
        price=''
        if(Host==True):
            url='/success_host'
            name=data['title']
            price=data['price']
        else:
            url='/success_join/'+data['contest_id'][0]+'/'+str(Admin)
            name=data['title'][0]
            price=data['price'][0]

        stripe.api_key="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"
        checkout_session=stripe.checkout.Session.create(
           line_items=[
            {
                'price_data': {
                    'product_data': {
                        'name': name,
                    },
                    'unit_amount': int(price)*100,
                    'currency': 'usd',
                },
                'quantity': 1,
            },
        ],
        payment_method_types=['card'],
        mode='payment',
        success_url=request.host_url + url,
        cancel_url=request.host_url + '/cancel',
    )
        return (checkout_session.url)

