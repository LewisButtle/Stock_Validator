from django.db import models

class CompanyCodes(models.Model):
	companyID = models.CharField(max_length=30, primary_key = True)
	companyName = models.CharField(max_length=50)
	def __str__(self):
		return '%s %s' % (self.companyID, self.companyName)
	class Meta:
		verbose_name_plural = "Company Codes"

class ProductSellers(models.Model):
	product = models.CharField(max_length=30, primary_key= True)
	companyID = models.ForeignKey(CompanyCodes, on_delete=models.CASCADE)
	def __str__(self):
		return '%s %s' % (self.product, self.companyID)
	class Meta:
		verbose_name_plural = "Product Sellers"

class Currencies(models.Model):
	currency = models.CharField(max_length=30, primary_key= True)
	def __str__(self):
		return '%s' % (self.currency)
	class Meta:
		verbose_name_plural = "Currencies"

class ProductPrices(models.Model):
	date = models.DateField()
	product = models.ForeignKey(ProductSellers, on_delete=models.CASCADE)
	marketPrice = models.DecimalField(max_digits = 10, decimal_places=2)
	class Meta:
		verbose_name_plural = "Product Prices"
		unique_together = ('date','product')

class StockPrices(models.Model):
	date = models.DateField()
	companyID = models.ForeignKey(CompanyCodes, on_delete=models.CASCADE)
	stockPrice = models.DecimalField(max_digits = 10, decimal_places=2)
	class Meta:
		verbose_name_plural = "Stock Prices"
		unique_together = ('date','companyID')

class CurrencyValues(models.Model):
	date = models.DateField()
	currency = models.ForeignKey(Currencies, on_delete=models.CASCADE)
	valueInUSD = models.DecimalField(max_digits = 10, decimal_places=4) 
	class Meta:
		verbose_name_plural = "Currency Values"
		unique_together = ('date','currency')

class DerivativeTrades(models.Model):
	tradeID = models.CharField(max_length=30, unique= True)
	dateOfTrade = models.DateTimeField()
	product = models.CharField(max_length=30)
	buyingParty = models.ForeignKey(CompanyCodes, related_name = "buyingParty_CompanyCode", on_delete=models.CASCADE)
	sellingParty = models.ForeignKey(CompanyCodes, related_name = "sellingParty_CompanyCode",on_delete=models.CASCADE)
	notionalAmount = models.DecimalField(max_digits = 20, decimal_places=6)
	notionalCurrency = models.ForeignKey(Currencies, related_name = "notionalCurrency_Currencies",on_delete=models.CASCADE)
	quantity = models.IntegerField()
	maturityDate = models.DateField()
	underlyingPrice = models.DecimalField(max_digits = 20, decimal_places=6)
	underlyingCurrency = models.ForeignKey(Currencies, related_name = "underlyingCurrency_Currencies",on_delete=models.CASCADE)
	strikePrice = models.DecimalField(max_digits = 20, decimal_places=6)
	archived = models.BooleanField(default = False)
	class Meta:
		verbose_name_plural = "Derivative Trades"


	