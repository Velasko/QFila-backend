head = """<!DOCTYPE html>
<html>
<head>
<style>
.Restaurant {
	border: 5px outset #7958c0;
	color: #eceffd;
	background-color: #7958c0;
	margin: 10px;
}
.Total{
	margin: 10px;
}
</style>
</head>
<body style="color:#7958c0;background-color:#88edc4;width:700px;font-size:medium">
	<h1>Confirmação de Pedido</h1>
"""

def restaurant_body(img, name):
	body = f"""
	<div class="Restaurant">
		<h1 style="margin-top:5px;margin-left:5px;">
			<img src="{img}" width="64" height="64">
			{name}
		</h1>"""

	return body

def meal_body(name, ammount, price):
	body = f"""
		<p style="text-align:left;">
			{name}:
			<span style="float:right;">
				{ammount} x R$ {price:.2f}
			</span>
		</p>"""
	return body


def restaurant_total(price):
	body = f"""
		<hr>
		<p style="text-align:left;">
			Total:
			<span style="float:right;">
				R$ {price:.2f}
			</span>
		</p>
	</div>
	<p></p>"""
	return body

def total(price, fee):
	total = price + fee
	body = f"""
	<div class="Total">
		<p style="text-align:left;"><b>
			Global:
			<span style="float:right;">
				R$ {price:.2f}
			</span>
		<p style="text-align:left;"><b>
			Taxa Qfila:
			<span style="float:right;">
				R$ {fee:.2f}
			</span>
		<hr>
		<p style="text-align:left;"><b>
			Total:
			<span style="float:right;">
				R$ {total:.2f}
			</span>
		</b></p>
		<p></p>
	</div>
	"""
	return body
