from django.shortcuts import render, redirect
import random
from datetime import timedelta, datetime

# Create your views here.

# directs the application to display the main.html template
def main(request):
    return render(request, 'restaurant/main.html')

# create a “daily special” item, and add it to the context dictionary for the page
def order(request):
    daily_specials = ["Leaf Village Stamina Ramen", "Kakashi's Secret Ingredient Ramen", 
                      "Toad Sage Ramen", "Ninja Energy Ramen", "Fire Style Dragon Ramen",
                      "Hokage's Favorite Deluxe Ramen", "Forest of Death Mushroom Ramen"]
    special_item = random.choice(daily_specials)
    
    context = {
        'daily_special': special_item
    }
    return render(request, 'restaurant/order.html', context)

# process the submission of an order, and display a confirmation page
def confirmation(request):
    
    if request.method == 'POST':
        # getting form data
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        special_instructions = request.POST.get('special_instructions', 'None')  

        # get ordered items and their toppings
        item_prices = {
            'Miso Chashu Ramen': 2250, 
            'Shio Ramen': 2000, 
            'Tonkotsu Ramen': 2349, 
            'Spicy Ramen': 3234,
            'Naruto Ramen Special': 3553,
        }

        daily_special = request.POST.get('daily_special_name')
        if daily_special:
            item_prices[daily_special] = 9999

        total_price = 0
        toppings_price = 500  

        # structure to hold items and their toppings
        order_summary = []

        # for each item, check if it was selected and handle its toppings
        for item in item_prices:
            if item in request.POST.getlist('items'):  # check if item is selected
                # get the toppings for this item
                topping_items = f'{item}_toppings'
                toppings = request.POST.getlist(topping_items)
                
                # calculate total price for the item and its toppings
                item_total_price = item_prices[item] + len(toppings) * toppings_price
                total_price += item_total_price

                # add item and its toppings to the order summary
                order_summary.append({
                    'item': item,
                    'price': item_prices[item],
                    'toppings': toppings,
                    'item_total_price': item_total_price,  
                })

        ready_time = datetime.now() + timedelta(minutes=random.randint(30, 60))
        
        # Prepare context for the template
        context = {
            'name': name,
            'phone': phone,
            'email': email,
            'special_instructions': special_instructions,
            'order_summary': order_summary,  
            'total_price': total_price,  
            'ready_time': ready_time.strftime("%a %b %d %H:%M:%S %Y"),  
        }

        return render(request, 'restaurant/confirmation.html', context)
    
    # if GET request, redirect to the form page
    return redirect('order')  # Redirect to the order form
