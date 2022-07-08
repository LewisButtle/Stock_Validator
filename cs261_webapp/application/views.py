from django.shortcuts import render
from django.views import generic
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect,FileResponse
from django.shortcuts import get_object_or_404
from .models import CompanyCodes,ProductSellers, ProductPrices, Currencies, StockPrices, CurrencyValues, DerivativeTrades
from .forms import CreateTradeForm, DailyReportForm, SearchReportForm, SearchTradeForm
from .machine_learning import *
import os

# For reading CSV files into DB
import csv, io
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import messages
import datetime

# For generating daily report
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus.tables import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Paragraph

# Set archived field to True of trades which should no longer be editable
def updateArchivedTrades():
    date_from = datetime.datetime.now() - datetime.timedelta(days=1)
    updating_trades = DerivativeTrades.objects.filter(dateOfTrade__lt=date_from, archived= False)
    if len(updating_trades) != 0:
        for trade in range(len(updating_trades)):
            updating_trades[trade].archived = True
        DerivativeTrades.objects.bulk_update(updating_trades,['archived'])

# Render index page
@login_required(login_url='/admin/login/')
def index(request):
    # Update trades
    updateArchivedTrades()
    context = {}
    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

# Render edit trade list
@login_required(login_url='/admin/login/')
def EditTradeView(request):
    #return HttpResponseRedirect('/admin/application/derivativetrades/')
    updateArchivedTrades()
    return HttpResponseRedirect('/admin/application/derivativetrades/')

# Render create new trade form
@login_required(login_url='/admin/login/')
def CreateTradeView(request):
    return HttpResponseRedirect('/admin/application/derivativetrades/add')

# Render edit trade list
@login_required(login_url='/admin/login/')
def DeleteTradeView(request):
    updateArchivedTrades()
    return HttpResponseRedirect('/admin/application/derivativetrades/')
    # context = {}
    # return render(request, 'delete_trade.html', context=context)

# The daily report page has two forms: one for generating and one for searching
@login_required(login_url='/admin/login/')
def DailyReportView(request):
    updateArchivedTrades()
    # Have to check the values of the submit button to know which form was pressed
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # The generate trade form was submitted
    time = str(datetime.datetime.now().time())
    if 'generate' in request.POST or '23:59' in time:
        # create a form instance and populate it with data from the request:
        form1 = DailyReportForm(request.POST)
        # check whether it's valid:
        if form1.is_valid():
            report_request_date = form1.cleaned_data['date_of_trade']

            # Fetch the derivative trades object for the given date
            daily_report_trades = DerivativeTrades.objects.filter(dateOfTrade__contains=report_request_date)

            # Create a new SimpleDocTemplate object in landscape
            doc = SimpleDocTemplate(BASE_DIR+"/reports/"+str(report_request_date)+".pdf",pagesize=(A4[1],A4[0]),leftMargin=0.5,rightMargin=0.5, topMargin=0.5, bottomMargin=0.5)
            # Initialise elements to add to doc
            elem = []
            # Set doc styling
            styles = getSampleStyleSheet()
            style = styles["Normal"]
            # Data is what will be contained in the daily report table and is a list of lists. This initialises the list with the column headings
            data = [
                ['Trade ID', 'Date of Trade', 'Product', 'Buying Party', 'Selling Party', 'Notional Amount',
                'Notional Currency', 'Quantity', 'Maturity Date','Underlying Price','Underlying Currency',
                'Strike Price', 'Archived']
            ]
            styleH = styles['Heading1']
            date_str = str(report_request_date)
            paragraph_1 = Paragraph("Daily Report for "+date_str, styleH)
            elem.append(paragraph_1)
            # Loop through all data fields for each derivative trade
            for i in range(len(daily_report_trades)):
                # Generate strings for each data field
                tradeID = str(daily_report_trades[i].tradeID)
                dateOfTrade = str(daily_report_trades[i].dateOfTrade)
                dateOfTrade = dateOfTrade[:-9]
                product = str(daily_report_trades[i].product)
                buyingParty = str(daily_report_trades[i].buyingParty.companyID)
                sellingParty = str(daily_report_trades[i].sellingParty.companyID)
                notionalAmount = str(daily_report_trades[i].notionalAmount)
                notionalAmount = notionalAmount[:-4]
                notionalCurrency = str(daily_report_trades[i].notionalCurrency.currency)
                quantity = str(daily_report_trades[i].quantity)
                maturityDate = str(daily_report_trades[i].maturityDate)
                underlyingPrice = str(daily_report_trades[i].underlyingPrice)
                underlyingPrice = underlyingPrice[:-4]
                underlyingCurrency = str(daily_report_trades[i].underlyingCurrency.currency)
                strikePrice = str(daily_report_trades[i].strikePrice)
                strikePrice = strikePrice[:-4]
                archived = str(daily_report_trades[i].archived)
                # Adds a new list to the data list
                temp_list = []
                temp_list = [tradeID, dateOfTrade, product, buyingParty, sellingParty, notionalAmount, notionalCurrency,
                    quantity, maturityDate, underlyingPrice, underlyingCurrency,strikePrice, archived
                ]
                # Add list to the data list
                data.append(temp_list)
            # Set table contents to be the data list
            table = Table(data)
            # Set table style and alignment
            table.hAlign = "LEFT"
            db_color = colors.HexColor('#0098db')
            table.setStyle(TableStyle([
                                    ('BACKGROUND',(0,0),(-1,0),db_color),
                                    ('GRID',(0,1),(-1,-1),0.01*inch,(0,0,0,)),
                                    ('FONTSIZE', (0,0), (-1,-1), 6.5)]))
            # Add table to doc
            elem.append(table)
            # Build doc
            doc.build(elem)
            fs = FileSystemStorage(BASE_DIR+"/reports")
            # Open doc and download doc for the user
            with fs.open(BASE_DIR+"/reports/"+str(report_request_date)+".pdf") as pdf:
                        response = HttpResponse(pdf, content_type='application/pdf')
                        response['Content-Disposition'] = 'attachment; filename="dailyreport.pdf"'
                        return FileResponse(open(str(BASE_DIR+"/reports/"+str(report_request_date)+".pdf"), 'rb'), content_type='application/pdf')
        form2=SearchReportForm()

    # The search a trade form was submitted
    elif 'search' in request.POST:
        form2=SearchReportForm(request.POST)
        if form2.is_valid():
            fs = FileSystemStorage(BASE_DIR+"/reports")
            report_request_date = form2.cleaned_data['date_of_trade']
            try:
                with fs.open(BASE_DIR+"/reports/"+str(report_request_date)+".pdf") as pdf:
                        response = HttpResponse(pdf, content_type='application/pdf')
                        response['Content-Disposition'] = 'attachment; filename="dailyreport.pdf"'
                        return FileResponse(open(str(BASE_DIR+"/reports/"+str(report_request_date)+".pdf"), 'rb'), content_type='application/pdf')
                        #return response
            except FileNotFoundError:
                messages.warning(request,'No report exists for the given date. Please generate the report.')
                form1 = DailyReportForm()
                return render(request, 'daily_report.html', {'form1': form1, 'form2':form2})

    
    form1 = DailyReportForm()
    form2 = SearchReportForm()
    return render(request, 'daily_report.html', {'form1': form1, 'form2':form2})


@login_required(login_url='/admin/login/')
def MainView(request):
    context = {}
    return render(request, 'index.html', context=context)

# Utility function to add data from CSVs to database
@login_required(login_url='/admin/login/')
def UploadCSV(request):
    # HTML template for uploading a CSV file
    template = "csv_upload.html"
    context = {}

    # Landing page on GET request
    if request.method == "GET":
        return render(request, template, context)

    name = request.FILES['file'].name

    # Get CSV file from HTTP upload form
    csv_file = request.FILES['file']

    # Check if its a CSV file
    if not csv_file.name.endswith('.csv'):
        messages.error(request,'Not a CSV file!')

    # Set dataset & io stream (csv data)
    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)

    # Skip first line of CSV (column names)
    next(io_string)

    if "companyCodes" in name:
        for column in csv.reader(io_string, delimiter=',', quotechar="|"):
            _, created = CompanyCodes.objects.update_or_create(
                companyID = column[1],
                companyName = column[0])

    elif "productSellers" in name:
        for column in csv.reader(io_string, delimiter=',', quotechar="|"):
            _, created = ProductSellers.objects.update_or_create(
                product = column[0],
                companyID = get_object_or_404(CompanyCodes, pk=column[1]))

    elif "productPrices" in name:
        for column in csv.reader(io_string, delimiter=',', quotechar="|"):
            _, created = ProductPrices.objects.update_or_create(
                date = datetime.datetime.strptime(column[0],"%d/%m/%Y"),
                product = get_object_or_404(ProductSellers, pk=column[1]),
                marketPrice = column[2])

    elif "stockPrices" in name:
        for column in csv.reader(io_string, delimiter=',', quotechar="|"):
            _, created = StockPrices.objects.update_or_create(
                date = datetime.datetime.strptime(column[0],"%d/%m/%Y"),
                companyID = get_object_or_404(CompanyCodes, pk=column[1]),
                stockPrice = column[2])

    elif "currencies" in name:
        for column in csv.reader(io_string, delimiter=',', quotechar="|"):
            _, created = Currencies.objects.update_or_create(
                currency = column[1])

    elif "currencyValues" in name:
        for column in csv.reader(io_string, delimiter=',', quotechar="|"):
            _, created = CurrencyValues.objects.update_or_create(
                date = datetime.datetime.strptime(column[0],"%d/%m/%Y"),
                currency = get_object_or_404(Currencies, pk=column[1]),
                valueInUSD = column[2])

    elif "derivativeTrades" in name:
        for column in csv.reader(io_string, delimiter=',', quotechar="|"):
            _, created = DerivativeTrades.objects.update_or_create(
                tradeID = column[1],
                dateOfTrade = datetime.datetime.strptime(column[0],"%d/%m/%Y %H:%M"),
                product = column[2],
                buyingParty = get_object_or_404(CompanyCodes, pk=column[3]),
                sellingParty = get_object_or_404(CompanyCodes, pk=column[4]),
                notionalAmount = column[5],
                notionalCurrency = get_object_or_404(Currencies, pk=column[6]),
                quantity = column[7],
                maturityDate = datetime.datetime.strptime(column[8],"%d/%m/%Y"),
                underlyingPrice = column[9],
                underlyingCurrency = get_object_or_404(Currencies, pk=column[10]),
                strikePrice = column[11])

    return render(request, template, context)
