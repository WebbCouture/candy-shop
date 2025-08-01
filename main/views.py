from django.shortcuts import render

def home(request):
    return render(request, 'main/home.html')

def product_list(request):
    products = [
        {
            'name': 'Cherry Delight',
            'description': 'Sweet cherry flavored candy, perfect for any occasion.',
            'image_url': 'https://images.unsplash.com/photo-1603202902092-3eb7a76ecf5f?q=80&w=687&auto=format&fit=crop',
        },
        {
            'name': 'Chocolate Bliss',
            'description': 'Rich chocolate candy made with premium cocoa.',
            'image_url': 'https://images.unsplash.com/photo-1534119139482-b530a7f9a98b?q=80&w=735&auto=format&fit=crop',
        },
        {
            'name': 'Fruit Punch',
            'description': 'Refreshing fruity candy bursting with flavor.',
            'image_url': 'https://images.unsplash.com/photo-1600359746315-119f1360d663?q=80&w=688&auto=format&fit=crop',
        },
    ]

    query = request.GET.get('q', '').strip().lower()
    filtered_products = []

    if query:
        for product in products:
            if query in product['name'].lower():
                filtered_products.append(product)
    else:
        filtered_products = products

    no_results = query and not filtered_products

    context = {
        'products': products,
        'filtered_products': filtered_products,
        'no_results': no_results,
        'search_query': query,
    }

    return render(request, 'main/product_list.html', context)

def about(request):
    return render(request, 'main/about.html')

def contact(request):
    return render(request, 'main/contact.html')
