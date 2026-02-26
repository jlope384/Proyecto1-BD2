# Preliminar Design

\_Restaurants|
--------------> Name: string
--------------> Avg-rating: decimal
--------------> Location: geospatial
--------------> Type-of-food: string[]
--------------> Price-range: (decimal,decimal)
|
--------------> \_Menu-Items|

\_Users|
-------->
--------> \_Orders: [] various orders models|
|
---------------------------------------------> Order-number-per-restaurant: integer
---------------------------------------------> For-restaurant: reference_restaurant
---------------------------------------------> Menu-items: reference_to_menu_items_in_resutaurant []
---------------------------------------------> Payed: decimal
---------------------------------------------> Note: Text

\_Reviews|
----------> From-user: reference_user
----------> For-restaurant: reference_restaurant
----------> Comment: text
----------> Score: decimal between 0..5 (like a star rating)
----------> Photos-url: string [] (c'mon is just a bucket)
