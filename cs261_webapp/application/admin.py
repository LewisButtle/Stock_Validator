from django.contrib import admin
import difflib
from django import forms
from django.urls import reverse
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect, FileResponse
from .models import CompanyCodes, ProductSellers, Currencies, ProductPrices, StockPrices, CurrencyValues, DerivativeTrades
from .machine_learning import check_data
import datetime
from datetime import date


class DerivativeTradesForm(forms.ModelForm):

    class Meta:
        model = DerivativeTrades
        exclude = ('archived',)

    def clean(self):

        tradeID = self.cleaned_data.get('tradeID')
        dateOfTrade = self.cleaned_data.get('dateOfTrade')
        maturityDate = self.cleaned_data.get('maturityDate')
        product = self.cleaned_data.get('product')
        quantity = self.cleaned_data.get('quantity')
        strikePrice = self.cleaned_data.get('strikePrice')
        selling_party = self.cleaned_data.get('sellingParty')
        exists_product = len(ProductSellers.objects.filter(pk=product))
        exists_productSeller = len(ProductSellers.objects.filter(pk=product).filter(companyID=selling_party))
        # Converts all chars to uppercase
        if tradeID is not None:
            tradeID.upper()
            if len(tradeID) != 16:
                raise forms.ValidationError("Trade ID must be of length 16!")
            else:
                for i in range(0, 8):
                    # Checks if character
                    if not tradeID[i].isalpha():
                        raise forms.ValidationError("First eight characters must be letters!")

                for i in range(8, 16):
                    # Checks if numerical
                    if tradeID[i].isalpha():
                        raise forms.ValidationError("Last eight characters must be numbers!")
        if product is not None:
            if product == 'Stocks':
                exists_product += 1
                exists_productSeller += 1
            elif product == 'Stock':
                string = "Product does not exist! Did you mean Stocks?"

        if exists_product is not None and tradeID is not None:
            if exists_product == 0:
                products = list(ProductSellers.objects.filter(companyID = selling_party).values_list('product',flat=True))
                if product == None:
                    product = 'a'
                matches = difflib.get_close_matches(product,products)
                if len(matches) != 0:
                    string = "Product does not exist! Did you mean "
                    for prod in matches:
                        string = string + str(prod) + ', '
                    string = string[:-2] + "?"
                else:
                    string = "Product does not exist! Common items from the selected selling party are: "
                    for item in products:
                        string = string + str(item) + ", "
                    string = string[:-2]
                raise forms.ValidationError(string)
        
        if exists_productSeller:
            if exists_productSeller == 0:
                raise forms.ValidationError("The selling party does not sell the selected product!")
        
        if maturityDate is not None and dateOfTrade is not None:
            if maturityDate < dateOfTrade.date():
                raise forms.ValidationError("The maturity date cannot be prior to the date the trade was created on!")

        if quantity != None:
            if quantity < 1:
                raise forms.ValidationError("Quantity cannot be less than 1!")

        if strikePrice != None:
             if strikePrice <= 0:
                raise forms.ValidationError("Stike price cannot be less than 0.01!")

        today = datetime.date.today()

        if dateOfTrade is not None:
            if dateOfTrade.date() > today:
                raise forms.ValidationError("Please ensure that the date is prior to" + str(datetime.datetime.now()))
            if dateOfTrade.date() < date(2019,1,1):
                if CurrencyValues.objects.filter(currency='USD', date=dateOfTrade).first() is None:
                    raise forms.ValidationError("No data exists for currency values, product and strike prices for the given date. Please use the CSV Upload function")


class DerivativeTradesAdmin(admin.ModelAdmin):

    made_changes = False
    times_submitted = 0
    form = DerivativeTradesForm
    original_values = [0,0,0,None,None]
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["tradeID","dateOfTrade","underlyingPrice","product","sellingParty","buyingParty","notionalAmount",]
        else:
            return ["underlyingPrice", "notionalAmount", ]

    def get_queryset(self, request):
        self.original_values[0] = 0
        qs = DerivativeTrades.objects.filter(archived=False)
        # Here's where we specify what to filter our queryset by.
        return qs

    # Overrides the ModelAdmin method to allow pre/post data operations
    def save_model(self, request, obj, form, change):
        
        if obj.dateOfTrade.date() > date(2019, 12, 31):
            search_date = date(2019, 12, 31)
        else:
            search_date = obj.dateOfTrade.date()

        if self.times_submitted < 1 or self.original_values[1] != obj.quantity or self.original_values[2] != obj.strikePrice or self.original_values[3] != obj.notionalCurrency or self.original_values[4] != obj.underlyingCurrency:
            if self.original_values[0] == 0:
                self.original_values[0] = 1
                self.original_values[1] = obj.quantity
                self.original_values[2] = obj.strikePrice
                self.original_values[3] = obj.notionalCurrency
                self.original_values[4] = obj.underlyingCurrency
            # Retrieve currency values
            currency_values_on_date = CurrencyValues.objects.filter(date=search_date)
            notional_currency_value = float(currency_values_on_date.filter(currency=obj.notionalCurrency)[0].valueInUSD)
            underlying_currency_value = float(currency_values_on_date.filter(currency=obj.underlyingCurrency)[0].valueInUSD)
            usd_price = float(obj.strikePrice) * notional_currency_value

            prices, price_response_type, quantities, quantity_response_type = check_data(
                obj.sellingParty, obj.product, obj.quantity, usd_price, obj.dateOfTrade, notional_currency_value)

            if price_response_type == 2:
                self.made_changes = True
                string = 'Perhaps you meant '
                if len(prices) == 0:
                    string = 'The algorithm did not find any alternatives,' + \
                             ' but the input is quite different from historical data'
                elif len(prices) == 1:
                    string = string+str(prices[0])
                elif len(prices) == 2:
                    string = string+str(prices[0])+' or '+str(prices[1])
                else:
                    for i in range(len(prices) - 1):
                        string = string+str(prices[i])+', '
                    string = string+'or '+str(prices[len(prices)-1])
                messages.warning(request, 'Please double-check the Strike Price. '+string)

            elif price_response_type == 3:
                self.made_changes = True
                if len(prices) > 0:
                    messages.error(request, 'The Strike Price has been corrected from ' +
                                   str(obj.strikePrice)+' to '+str(prices[0]))
                    obj.strikePrice = prices[0]
                else:
                    messages.error(request, 'The Strike Price has been detected as significantly different from ' +
                                            'historical data, but no alternative has been found')

            if quantity_response_type == 2:
                self.made_changes = True
                string = 'Perhaps you meant '
                if len(quantities) == 0:
                    string = 'The algorithm did not find any alternatives,' + \
                             ' but the input is quite different from historical data'
                elif len(quantities) == 1:
                    string = string+str(quantities[0])
                elif len(quantities) == 2:
                    string = string+str(quantities[0])+' or '+str(quantities[1])
                else:
                    for i in range(len(quantities) - 1):
                        string = string+str(quantities[i])+', '
                    string = string+'or '+str(quantities[len(quantities)-1])
                messages.warning(request, 'Please double-check the Quantity. '+string)

            elif quantity_response_type == 3:
                self.made_changes = True
                if len(quantities) > 0:
                    messages.error(request, 'The Quantity has been corrected from ' +
                                   str(obj.quantity)+' to '+str(quantities[0]))
                    obj.quantity = quantities[0]
                else:
                    messages.error(request, 'The Quantity has been detected as significantly different from ' +
                                            'historical data, but no alternative has been found')

        
        # Retrieve derivative cost
        if obj.product != 'Stocks':
            price = float(ProductPrices.objects.filter(date=search_date, product=obj.product)[0].marketPrice)
        else:
            price = float(StockPrices.objects.filter(date=search_date, companyID=obj.sellingParty)[0].stockPrice)
        currency_values_on_date = CurrencyValues.objects.filter(date=search_date)
        notional_currency_value = float(currency_values_on_date.filter(currency=obj.notionalCurrency)[0].valueInUSD)
        underlying_currency_value = float(currency_values_on_date.filter(currency=obj.underlyingCurrency)[0].valueInUSD)
        # Calculate fields
        obj.notionalAmount = round(price*float(obj.quantity)*notional_currency_value,2)
        obj.underlyingPrice = round(price*underlying_currency_value,2)

        if self.times_submitted == 1 and self.original_values[1] != obj.quantity and self.original_values[2] != obj.strikePrice and self.original_values[3] != obj.notionalCurrency and self.original_values[4] != obj.underlyingCurrency:
            self.made_changes = False
            self.times_submitted = 0
        if self.made_changes:
            self.times_submitted += 1
        else:
            self.times_submitted = 0
        obj.save()

    def response_add(self, request, obj, post_url_continue=None):
        if self.made_changes:
            self.made_changes = False
            return HttpResponseRedirect("/admin/application/derivativetrades/" + str(obj.id) + "/change")
        else:
            messages.success(request, 'Derivative trade has been added successfully')
            return HttpResponseRedirect("/admin/application/derivativetrades/")

    def response_change(self, request, obj, post_url_continue=None):
        if self.made_changes:
            self.made_changes = False
            return HttpResponseRedirect("/admin/application/derivativetrades/" + str(obj.id) + "/change")
        else:
            messages.success(request, 'Derivative trade has been updated successfully')
            return HttpResponseRedirect("/admin/application/derivativetrades/")

    list_display = (
        'tradeID', 'dateOfTrade', 'product', 'get_buyer', 'get_seller', 'notionalAmount', 'get_notionalCurrency',
        'quantity', 'maturityDate', 'underlyingPrice', 'get_underlyingCurrency', 'strikePrice')

    autocomplete_fields = ['buyingParty', 'sellingParty', 'underlyingCurrency', 'notionalCurrency']

    search_fields = ['tradeID', 'dateOfTrade', 'product', 'notionalAmount', 'quantity',
                     'maturityDate', 'underlyingPrice', 'strikePrice', 'sellingParty__companyID',
                     'buyingParty__companyID', 'notionalCurrency__currency', 'underlyingCurrency__currency']
    list_filter = ('product',)
    list_per_page = 20
    list_max_show_all = 10

    def get_buyer(self, obj):
        return obj.buyingParty.companyID

    get_buyer.admin_order_field = 'buyingParty'  # Allows column order sorting
    get_buyer.short_description = 'BuyingParty'  # Renames column head

    def get_seller(self, obj):
        return obj.sellingParty.companyID

    get_seller.admin_order_field = 'sellingParty'  # Allows column order sorting
    get_seller.short_description = 'SellingParty'  # Renames column head

    def get_notionalCurrency(self, obj):
        return obj.notionalCurrency.currency

    get_notionalCurrency.admin_order_field = 'notionalCurrency'  # Allows column order sorting
    get_notionalCurrency.short_description = 'notionalCurrency'  # Renames column head

    def get_underlyingCurrency(self, obj):
        return obj.underlyingCurrency.currency

    get_underlyingCurrency.admin_order_field = 'underlyingCurrency'  # Allows column order sorting
    get_underlyingCurrency.short_description = 'underlyingCurrency'  # Renames column head


class CompanyCodesAdmin(admin.ModelAdmin):
    search_fields = ['companyID']


class CurrenciesAdmin(admin.ModelAdmin):
    search_fields = ['currency']


admin.site.register(DerivativeTrades, DerivativeTradesAdmin)
admin.site.register(CompanyCodes, CompanyCodesAdmin)
admin.site.register(Currencies, CurrenciesAdmin)
admin.site.register(ProductSellers)
admin.site.register(ProductPrices)
admin.site.register(StockPrices)
admin.site.register(CurrencyValues)
