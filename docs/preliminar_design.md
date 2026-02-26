# Preliminar Design

\_Restaurants|
|
------------->Name: string
------------->Avg-Rating: decimal
------------->Location: geospatial
------------->Type-of-food: string[]
------------->Price-Range: (decimal,decimal)
|
------------->\_Menu-Items|
|

\_Users|
|
------->\_Orders|

\_Reviews|
|
--------->\_From-User:reference_user
--------->\_For-Restaurant:reference_restaurant
