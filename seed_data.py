# 1. Create the database tables first
# python manage.py migrate
# 2. Run the seed script to load all products and images
# python manage.py shell < seed_data.py

import os
import requests
from django.utils.text import slugify
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from core.models import Product

print(f"{'='*60}")
print("STARTING DATA INITIALIZATION")
print(f"{'='*60}\n")

# 1. DATA DEFINITIONS
products_data = [
    {
        "name": "Monocrystalline Solar Panel 330W",
        "description": "High-efficiency monocrystalline solar panel with 21% efficiency. Perfect for residential rooftop installations. 25-year performance warranty.",
        "price": 8500.00,
        "image_url": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800&q=80",
        "stock": 50, "min": 2, "max": 20
    },
    {
        "name": "Polycrystalline Solar Panel 270W",
        "description": "Cost-effective polycrystalline panel ideal for large-scale commercial installations. 18% efficiency with reliable performance.",
        "price": 6800.00,
        "image_url": "https://images.unsplash.com/photo-1508514177221-188b1cf16e9d?w=800&q=80",
        "stock": 30, "min": 2, "max": 15
    },
    {
        "name": "Bifacial Solar Panel 450W",
        "description": "Advanced bifacial technology captures sunlight from both sides. Up to 30% more energy generation. Premium choice for MSMEs.",
        "price": 12500.00,
        "image_url": "https://images.unsplash.com/photo-1559302504-64aae6ca6b6d?w=800&q=80",
        "stock": 10, "min": 1, "max": 5
    },
    {
        "name": "5kW On-Grid Solar Inverter",
        "description": "High-performance grid-tied inverter with 97.5% efficiency. WiFi monitoring, MPPT technology, and 5-year warranty.",
        "price": 35000.00,
        "image_url": "https://images.unsplash.com/photo-1621905252507-b35492cc74b4?w=800&q=80",
        "stock": 15, "min": 1, "max": 2
    },
    {
        "name": "3kW Hybrid Solar Inverter",
        "description": "Hybrid inverter with battery backup support. Seamless grid-to-battery switching. Perfect for homes with power cuts.",
        "price": 42000.00,
        "image_url": "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=800&q=80",
        "stock": 8, "min": 1, "max": 2
    },
    {
        "name": "150Ah Tubular Solar Battery",
        "description": "Deep-cycle tubular battery designed for solar applications. 5-year warranty with excellent charge retention.",
        "price": 15500.00,
        "image_url": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=800&q=80",
        "stock": 25, "min": 2, "max": 8
    },
    {
        "name": "Solar Water Heater 200L",
        "description": "Premium GI tank with marine-grade coating and PUF insulation. Heats water even on cloudy days. 7-year warranty.",
        "price": 28000.00,
        "image_url": "https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=800&q=80",
        "stock": 5, "min": 1, "max": 1
    },
    {
        "name": "Solar Panel Cleaning Kit",
        "description": "Complete cleaning kit with telescopic pole, soft brush, and eco-friendly cleaning solution. Maintain peak efficiency.",
        "price": 3500.00,
        "image_url": "https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?w=800&q=80",
        "stock": 40, "min": 1, "max": 5
    },
    {
        "name": "Solar Mounting Structure (10 Panels)",
        "description": "Hot-dip galvanized mounting structure for 10 panels. Wind-resistant design suitable for Gujarat weather. Easy installation.",
        "price": 18000.00,
        "image_url": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800&q=80",
        "stock": 12, "min": 1, "max": 3
    },
    {
        "name": "Automatic Solar Panel Cleaning System",
        "description": "Robotic sprinkler system for automatic panel cleaning. Programmable timers, water-efficient design. Increases output by 15%.",
        "price": 45000.00,
        "image_url": "https://images.unsplash.com/photo-1497435334941-8c899ee9e8e9?w=800&q=80",
        "stock": 3, "min": 1, "max": 1
    },
]

# 2. SEEDING LOGIC
created_count = 0
updated_count = 0

for data in products_data:
    slug = slugify(data["name"])

    # Create or update product
    product, created = Product.objects.get_or_create(
        slug=slug,
        defaults={
            "name": data["name"],
            "description": data["description"],
            "price": data["price"],
            "is_active": True,
        }
    )

    # Update stock and limits
    product.stock_quantity = data["stock"]
    product.min_order_quantity = data["min"]
    product.max_order_quantity = data["max"]

    # Handle Image Download (only if product doesn't have one or to refresh)
    if not product.image or product.image.name == '':
        try:
            print(f"↓ Downloading image for: {data['name']}...")
            response = requests.get(data["image_url"], timeout=10)
            if response.status_code == 200:
                img_temp = NamedTemporaryFile()
                img_temp.write(response.content)
                img_temp.flush()
                filename = f"{slug}.jpg"
                product.image.save(filename, File(img_temp), save=False)
        except Exception as e:
            print(f"✗ Image download failed for {data['name']}: {e}")

    product.save()

    if created:
        print(f"✓ Created: {data['name']}")
        created_count += 1
    else:
        print(f"↺ Updated: {data['name']} (Stock: {data['stock']})")
        updated_count += 1

print(f"\n{'='*60}")
print("INITIALIZATION COMPLETE")
print(f"  Created: {created_count} new products")
print(f"  Updated: {updated_count} existing products")
print(f"{'='*60}")
