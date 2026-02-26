# Preliminar Design

\_Restaurants|
--------------> Name: string
--------------> Avg-rating: decimal
--------------> Location: geospatial
--------------> Type-of-food: string[]
--------------> Price-range: (decimal,decimal)
{
--------------> \_Menu-Items []|
--------------------------------> Name: string
--------------------------------> Price: decimal
}

\_Users|
--------> Username: string
--------> hashed_passwod_with_user_sided_salt: string ( we going simple LMAO )
{
--------> \_Orders: [] various orders models|

---------------------------------------------> Order-number-per-restaurant: integer
---------------------------------------------> For-restaurant: reference_restaurant
---------------------------------------------> \_Menu-items: []|

-{
----------------------------------------------------------------> Quantity: decimal
----------------------------------------------------------------> Menu-item-id-from-restaurant: reference
----------------------------------------------------------------> Menu-note: Text
-}
}

---------------------------------------------> Payed: bool
---------------------------------------------> Quantity: bool
---------------------------------------------> Note: Text
---------------------------------------------> Completed

\_Reviews|
----------> From-user: reference
----------> For-restaurant: reference
----------> Comment: text
----------> Score: decimal between 0..5 (like a star rating)
----------> Photos-url: string [] (c'mon is just a bucket)
