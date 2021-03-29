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

Table SentSMS as sms {
  aws_id string [pk]
  user_id int [pk]
  time datetime
  operation string
}

Ref: sms.user_id > U.id

Table FoodCourt {
  id int [pk, increment]
  name string
  state string
  city string
  address string
  latitude Float
  longitude Float
}

Table Restaurants as R {
  id int [pk, increment]
  name varchar
  bank_info bank
  login varchar
  passwd varchar
  location int
  image link
  //CNPj???
  //Any information so it's open?
}

Ref: FoodCourt.id < Restaurants.location

Table FoodType {
  name varchar [pk]
}

Table Meal {
  id int [pk, increment]
  rest int [pk]
  section string
  name varchar
  foodtype int
  price float
  description varchar
  image link
  //Add complements?
  //Sortings?
}

Ref: Meal.rest > R.id 
Ref: Meal.foodtype > FoodType.name


Table MenuSection {
  name string [pk]
  rest int [pk]
  meal int [pk]  
}

Ref: MenuSection.rest > R.id
Ref: MenuSection.meal > Meal.id

Table Cart as C {
  time datetime [pk]
  user int [pk]
  price float
  payment_method string
  payment_status string
  qfila_fee int
}

Ref: C.user > U.id

Table Order as O {
  time datetime [pk]
  user int [pk]
  rest int [pk]
  price integer
  comment string
  // The code the restaurante uses 
  // to identificate the order
  rest_order_id string
}

Ref: O.user > C.user
Ref: O.time > C.time
Ref: O.rest > Meal.rest

Table Item as I {
  time datetime [pk]
  user int [pk]
  rest int [pk]
  meal int [pk]
  
  ammount int
  state string
  
  price float
  comment string
}

Ref: I.user > O.user
Ref: I.time > O.time
Ref: I.rest > O.rest
Ref: I.meal > Meal.id

Table Complemento as poll {
  rest int [pk]
  cid int [pk]
  head string
  name string
  min int
  max int
  stackable boolean
}

Ref: poll.rest > R.id

Table Meal_Compl_Relation as mcr {
  rest int [pk]
  meal int [pk]
  compl int [pk]
  ammount int
}

Ref: mcr.rest > R.id
Ref: mcr.meal > Meal.id
Ref: mcr.compl > poll.cid

Table comp_tag {
  rest int [pk]
  cid int [pk]
  tag string [pk]
}

Ref: comp_tag.rest > poll.rest
Ref: comp_tag.cid > poll.cid

Table comp_item as PI {
  rest int [pk]
  cid int [pk]
  Iid int [pk]
  item_name string
  price_modification int
}

Ref: PI.rest > poll.rest
Ref: PI.cid > poll.cid

Table order_item_compl as oic {
  time datetime [pk]
  user int [pk]
  rest int [pk]
  meal int [pk]
  
  data string [pk]
  value_mod int [pk]
}

Ref: oic.time > I.time
Ref: oic.user > I.user
Ref: oic.rest > I.rest
Ref: oic.meal > I.meal

Table Shortner {
  // url shortner table
  short int [pk]
  long string
  delete_time datetime
}