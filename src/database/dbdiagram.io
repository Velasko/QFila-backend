//// -- LEVEL 1
//// -- Tables and References

// Creating tables
Table Users as U {
  id int [pk, increment]
  name varchar
  born date
  email email
  passwd varchar
  phone int
}

Table Restaurants as R {
  id int [pk, increment]
  name varchar
  address varchar
  open boolean
  bank_info bank
  login varchar //email?
  passwd varchar
}

Table Meal {
  rest int [pk]
  id int [pk, increment]
  type int
  price float
  description varchar
}

Ref: Meal.rest > R.id 

Table FoodType {
  id int [pk]
  name varchar
}

Ref: FoodType.id < Meal.type

Table Cart as C {
  //fazer uma tabela com cada item uma compra?
  //fazer uma tabela para a compra e outra para os itens da compra?
  user int [pk]
  time datetime [pk]
  total_price float

  //Total prices modifyers?
  //promo of 10%?
}

Ref: C.user > U.id

Table Item as I {
  user int [pk]
  time datetime [pk]
  rest int [pk]
  meal int [pk]
  price float
}

Ref: I.user > C.user
Ref: I.time > C.time
Ref: I.rest > Meal.rest
Ref: I.meal > Meal.id