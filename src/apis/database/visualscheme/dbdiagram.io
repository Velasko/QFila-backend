//// -- LEVEL 1
//// -- Tables and References

// Creating tables
Table Users as U {
  id int [pk, increment]
  name varchar
  birthday date
  email email
  passwd varchar
  phone int
}

Table FoodCourt {
  id int [pk, increment]
  name string
  address string
  latitude Float
  longitude Float
}

Table Restaurants as R {
  id int [pk, increment]
  name varchar
  bank_info bank
  email varchar
  passwd varchar
  location int
  //CNPj???
  //Any information so it's open?
}

Ref: FoodCourt.id < Restaurants.location

Table Meal {
  id int [pk, increment]
  rest int [pk]
  name varchar
  foodtype int
  price float
  description varchar
  //Add complements?
  //Sortings?
}

Ref: Meal.rest > R.id 

Table FoodType {
  name varchar [pk]
}

Ref: FoodType.name < Meal.foodtype

Table Cart as C {
  //fazer uma tabela com cada item uma compra?
  //fazer uma tabela para a compra e outra para os itens da compra?
  time datetime [pk]
  user int [pk]
  total_price float

  //Total prices modifyers?
}

Ref: C.user > U.id

Table Item as I {
  time datetime [pk]
  user int [pk]
  meal int [pk]
  rest int [pk]
  total_price float
}

Ref: I.user > C.user
Ref: I.time > C.time
Ref: I.rest > Meal.rest
Ref: I.meal > Meal.id

//Review table?