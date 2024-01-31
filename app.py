from flask import Flask, render_template, request, jsonify
weasyprint_path = r'C:\path\to\weasyprint.exe'
HTML = f"{weasyprint_path} --format pdf -"

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('invoice_template.html')

@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    try:
        # Fetch input parameters from the form
        seller_details = request.form.get('seller_details')
        place_of_supply = request.form.get('place_of_supply')
        billing_details = request.form.get('billing_details')
        shipping_details = request.form.get('shipping_details')
        place_of_delivery = request.form.get('place_of_delivery')
        order_details = request.form.get('order_details')
        invoice_details = request.form.get('invoice_details')
        reverse_charge = request.form.get('reverse_charge')
        signature_image = request.form.get('signature_image')
        item_descriptions = request.form.getlist('item_description')
        unit_prices = [float(price) for price in request.form.getlist('unit_price')]
        quantities = [int(quantity) for quantity in request.form.getlist('quantity')]
        discounts = [float(discount) for discount in request.form.getlist('discount')]

        # Validate input parameters
        validate_inputs(seller_details, place_of_supply, billing_details, shipping_details,
                        place_of_delivery, order_details, invoice_details, reverse_charge, item_descriptions,
                        unit_prices, quantities, discounts)

        # Compute derived parameters for each item
        items = []
        total_amount = 0
        for description, unit_price, quantity, discount in zip(item_descriptions, unit_prices, quantities, discounts):
            net_amount = unit_price * quantity - discount

            # Tax Type computation
            if place_of_supply == place_of_delivery:
                tax_type = {'CGST': 9, 'SGST': 9}
            else:
                tax_type = {'IGST': 18}

            # Tax Amount computation
            tax_amount = {key: (net_amount * value / 100) for key, value in tax_type.items()}

            # Total Amount computation
            total_item_amount = net_amount + sum(tax_amount.values())
            total_amount += total_item_amount

            items.append({
                'description': description,
                'unit_price': unit_price,
                'quantity': quantity,
                'discount': discount,
                'net_amount': net_amount,
                'tax_type': tax_type,
                'tax_amount': tax_amount,
                'total_amount': total_item_amount
            })

        # Render HTML template with computed parameters
        invoice_html = render_template('invoice_template.html',
                                       seller_details=seller_details,
                                       place_of_supply=place_of_supply,
                                       billing_details=billing_details,
                                       shipping_details=shipping_details,
                                       place_of_delivery=place_of_delivery,
                                       order_details=order_details,
                                       invoice_details=invoice_details,
                                       reverse_charge=reverse_charge,
                                       items=items,
                                       total_amount=total_amount,
                                       signature_image=signature_image)

        # Generate PDF from HTML using WeasyPrint
        pdf_bytes = generate_pdf(invoice_html)

        return pdf_bytes, 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'inline; filename=invoice.pdf'}

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def validate_inputs(seller_details, place_of_supply, billing_details, shipping_details,
                    place_of_delivery, order_details, invoice_details, reverse_charge, item_descriptions,
                    unit_prices, quantities, discounts):
    # Implement input validation logic here
    pass

def generate_pdf(html_content):
    pdf = HTML(string=html_content).write_pdf()
    return pdf

if __name__ == '__main__':
    app.run(debug=True)
