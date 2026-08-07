from django.db import models

class Requests(models.Model):
    STATUS = (
        ("running", "RUNNING"),
        ("retrying", "RETRYING"),
        ("finished", "FINISHED"),
        ("failure", "FAILURE"),
        ("cancelled", "CANCELLED"),
    )

    STATEMENT_TYPE = (
        ("IS", "Income Statement"),
        ("BS", "Balance Sheet"),
        ("CF", "Cash Flow Statement"),
    )

    PERIOD_TYPE = (
        ("FY", "Annual (Full Year)"),
        ("Q", "Quarterly"),
    )

    DISPLAY_UNIT = (
        ("1", "Exact Dollars ($)"),
        ("1000", "Thousands ($K)"),
        ("1000000", "Millions ($M)"),
    )

    TICKER_CHOICES = (
        ("AAPL", "AAPL - Apple"),
        ("MSFT", "MSFT - Microsoft"),
        ("GOOGL", "GOOGL - Alphabet (Class A)"),
        ("GOOG", "GOOG - Alphabet (Class C)"),
        ("AMZN", "AMZN - Amazon"),
        ("META", "META - Meta Platforms"),
        ("NVDA", "NVDA - NVIDIA"),
        ("TSLA", "TSLA - Tesla"),
        ("AVGO", "AVGO - Broadcom"),
        ("CSCO", "CSCO - Cisco Systems"),
        ("ACN", "ACN - Accenture"),
        ("ADBE", "ADBE - Adobe"),
        ("AMD", "AMD - AMD"),
        ("INTC", "INTC - Intel"),
        ("ORCL", "ORCL - Oracle"),
        ("CRM", "CRM - Salesforce"),
        ("QCOM", "QCOM - Qualcomm"),
        ("IBM", "IBM - IBM"),
        ("BRK.B", "BRK.B - Berkshire Hathaway"),
        ("JPM", "JPM - JPMorgan Chase"),
        ("BAC", "BAC - Bank of America"),
        ("V", "V - Visa"),
        ("MA", "MA - Mastercard"),
        ("C", "C - Citigroup"),
        ("WFC", "WFC - Wells Fargo"),
        ("GS", "GS - Goldman Sachs"),
        ("MS", "MS - Morgan Stanley"),
        ("SCHW", "SCHW - Charles Schwab"),
        ("JNJ", "JNJ - Johnson & Johnson"),
        ("MRK", "MRK - Merck"),
        ("PFE", "PFE - Pfizer"),
        ("LLY", "LLY - Eli Lilly"),
        ("ABBV", "ABBV - AbbVie"),
        ("ABT", "ABT - Abbott Laboratories"),
        ("UNH", "UNH - UnitedHealth Group"),
        ("AMGN", "AMGN - Amgen"),
        ("CVS", "CVS - CVS Health"),
        ("WMT", "WMT - Walmart"),
        ("COST", "COST - Costco"),
        ("TGT", "TGT - Target"),
        ("HD", "HD - Home Depot"),
        ("LOW", "LOW - Lowe's"),
        ("MCD", "MCD - McDonald's"),
        ("NKE", "NKE - Nike"),
        ("NFLX", "NFLX - Netflix"),
        ("KO", "KO - Coca-Cola"),
        ("PEP", "PEP - PepsiCo"),
        ("PG", "PG - Procter & Gamble"),
        ("XOM", "XOM - ExxonMobil"),
        ("CVX", "CVX - Chevron"),
        ("CAT", "CAT - Caterpillar"),
        ("BA", "BA - Boeing"),
        ("GE", "GE - General Electric"),
        ("UNP", "UNP - Union Pacific"),
        ("MMM", "MMM - 3M"),
    )

    # Task & Metadata
    task_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=9, choices=STATUS, default="running")
    logs = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    requester_email = models.EmailField()

    # User Request Inputs
    report_name = models.CharField(max_length=200)
    information = models.TextField()
    tickers = models.JSONField(default=list)
    statement_type = models.CharField(max_length=2, choices=STATEMENT_TYPE, default="IS")
    period_type = models.CharField(max_length=2, choices=PERIOD_TYPE, default="FY")
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    display_unit = models.CharField(max_length=10, choices=DISPLAY_UNIT, default="1000000")

    class Meta:
        verbose_name = "Request"
        verbose_name_plural = "Requests"

    def __str__(self):
        return self.report_name