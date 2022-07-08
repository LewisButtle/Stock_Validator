from django import forms
import datetime

# These methods are used for validation #

# Checks the trade ID follows the format of AAAAAAAA11111111 (8 characters followed by 8 letters)
def tradeID(data):
	# Converts all chars to uppercase
	data = data.upper()
	if(len(data)!=16):
		return False
	else:
		for i in range(0,8):
			# Checks if character
			if not data[i].isalpha():
				return False

		for i in range(8,16):
			# Checks if numerical
			if data[i].isalpha():
				return False

		return True

# Checks the company code to ensure it follows the format AAAA00 (4 characters and then 2 digits)
def companyCode(data):
	if(len(data)!=6):
		return False
	else:
		# Converts all chars to uppercase
		data=data.upper()
		for i in range(0,4):
			# Checks if a character
			if not data[i].isalpha():
				return False
		for i in range(4,6):
			# Checks if numerical
			if data[i].isalpha():
				return False

		return True

# Checks the notional currency to ensure it is three characters long
def notionalCurrency(data):
	if(len(data)!=3):
		return False
	else:
		# Converts all chars to uppercase
		data = data.upper()
		for i in range(0,3):
			# Checks if a character
			if not data[i].isalpha():
				return False
		return True

# Ensures the date is not in the future
def dateOfTradeValidate(date):
	#if(date>date.today()):
	#datetime.strptime(inputdate, "%d/%m/%Y").date()
	if(date>datetime.now()):
		return False
	else:
		return True

# Ensures the date of maturity is not in the past
def maturityDateValidation(date):
	if(date>=date.today()):
		return True
	else:
		return False

# A form for creating a new trade
class CreateTradeForm(forms.Form):
	date_of_trade = forms.DateTimeField(label='Date of Trade',initial=datetime.date.today())
	# The TextInput widget is used to customise the input on the webpage
	trade_id = forms.CharField(label='Trade ID', widget=forms.TextInput(
		attrs={
			# Calls the Bootstrap style class
			"class": "form-control error_handle",
			#"placeholder" : "Ensure alphanumeric characters only",
		}
	))
	product = forms.CharField(label='Product', widget=forms.TextInput(
		attrs={
			"class":"form-control",
			#"placeholder" : "Ensure alphanumeric characters only",
		}
	))
	buying_party = forms.CharField(label='Buying Party', widget=forms.TextInput(
		attrs={
			"class" : "form-control"
		}
	))
	selling_party = forms.CharField(label='Selling Party',widget=forms.TextInput(
		attrs={
			"class" : "form-control"
		}
	))
	notional_amount = forms.DecimalField(label='Notional Amount', decimal_places = 2)
	notional_currency = forms.CharField(label='Notional Currency')
	quantity = forms.IntegerField(label='Quantity')
	maturity_date = forms.DateField(label='Maturity Date',widget=forms.SelectDateWidget)
	underlying_price = forms.DecimalField(label='Underlying Price', decimal_places = 2)
	underlying_currency = forms.CharField(label='Underlying Currency')
	strike_price = forms.DecimalField(label='Strike Price', decimal_places = 2)

	# Cleans the date of trade data
	# def clean_date_of_trade(self):
	# 	data = self.cleaned_data.get('date_of_trade')
	# 	if not dateOfTradeValidate(data):
	# 		raise forms.ValidationError("Ensure the date is in the past")
	# 	return data

	# Cleans the trade ID data
	def clean_trade_id(self):
		data = self.cleaned_data.get('trade_id')
		if not tradeID(data):
			raise forms.ValidationError("Ensure the input has eight characters followed by eight numerical digits")
		return data

	# Cleans the buying_party data
	def clean_buying_party(self):
		data = self.cleaned_data.get('buying_party')
		if not companyCode(data):
			raise forms.ValidationError("Ensure the input is of length 6; 4 characters and 2 numerical digits")
		return data

	# Cleans the buying_party data
	def clean_selling_party(self):
		data = self.cleaned_data.get('selling_party')
		if not companyCode(data):
			raise forms.ValidationError("Ensure the input is of length 6; 4 characters and 2 numerical digits")
		return data

	# Cleans the notional currency data
	def clean_notional_currency(self):
		data = self.cleaned_data.get('notional_currency')
		if not notionalCurrency(data):
			raise forms.ValidationError("Ensure the input is of three characters")
		return data

	# Cleans the underlying currency data
	def clean_underlying_currency(self):
		data = self.cleaned_data.get('underlying_currency')
		if not notionalCurrency(data):
			raise forms.ValidationError("Ensure the input is of three characters")
		return data

	

# The form for searching daily reports
class SearchReportForm(forms.Form):
	date_of_trade = forms.DateField(label='Date of Trade',initial=datetime.date.today())

# The form for generating daily reports
class DailyReportForm(forms.Form):
	date_of_trade = forms.DateField(label='Date of Trade',initial=datetime.date.today())
	# Cleans the date of trade data
	# def clean_date_of_trade(self):
	# 	data = self.cleaned_data.get('date_of_trade')
	# 	if not dateOfTradeValidate(data):
	# 		raise forms.ValidationError("Ensure the date is in the past")
	# 	return data


class SearchTradeForm(forms.Form):
	date_option = forms.BooleanField(required=False, widget=forms.CheckboxInput(
		attrs={
			"onclick" : "date_option_clicked()",
			"autocomplete":"off",
		}
	))
	date_of_trade = forms.DateField(required=False)
	trade_id_option = forms.BooleanField(required=False, widget=forms.CheckboxInput(
		attrs={
			"onclick" : "trade_id_option_clicked()",
			"autocomplete":"off",
		}
	))
	trade_id = forms.CharField(label='Trade ID', required=False, widget=forms.TextInput(
		attrs={
			# Calls the Bootstrap style class
			"class": "form-control error_handle",
			#"placeholder" : "Ensure alphanumeric characters only",
		}
	))
	product_option = forms.BooleanField(required=False, widget=forms.CheckboxInput(
		attrs={
			"onclick" : "product_option_clicked()",
			"autocomplete":"off",
		}
	))
	product = product = forms.CharField(label='Product', required=False, widget=forms.TextInput(
		attrs={
			"class":"form-control",
			#"placeholder" : "Ensure alphanumeric characters only",
		}
	))
	buying_party_option = forms.BooleanField(required=False, widget=forms.CheckboxInput(
		attrs={
			"onclick" : "buying_party_option_clicked()",
			"autocomplete":"off",
		}
	))
	buying_party = buying_party = forms.CharField(label='Buying Party', required=False, widget=forms.TextInput(
		attrs={
			"class" : "form-control"
		}
	))
	selling_party_option = forms.BooleanField(required=False, widget=forms.CheckboxInput(
		attrs={
			"onclick" : "selling_party_option_clicked()",
			"autocomplete":"off",
		}
	))
	selling_party = selling_party = forms.CharField(label='Selling Party',required=False,widget=forms.TextInput(
		attrs={
			"class" : "form-control"
		}
	))
	underlying_currency_option = forms.BooleanField(required=False, widget=forms.CheckboxInput(
		attrs={
			"onclick" : "underlying_currency_option_clicked()",
			"autocomplete":"off",
		}
	))
	underlying_currency = forms.CharField(label='Underlying Currency',required=False)
	quantity_option = forms.BooleanField(required=False, widget=forms.CheckboxInput(
		attrs={
			"onclick" : "quantity_option_clicked()",
			"autocomplete":"off",
		}
	))
	quantity = forms.IntegerField(label='Quantity',required=False)
	maturity_date_option = forms.BooleanField(required=False, widget=forms.CheckboxInput(
		attrs={
			"onclick" : "maturity_date_option_clicked()",
			"autocomplete":"off",
		}
	))
	maturity_date = forms.DateField(label='Maturity Date',required=False,widget=forms.SelectDateWidget)

