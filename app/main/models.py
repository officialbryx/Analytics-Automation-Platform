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

    # Task & Metadata
    task_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=9, choices=STATUS, default="running")
    logs = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    requester_email = models.EmailField()

    # User Request Inputs
    report_name = models.CharField(max_length=200)
    information = models.TextField()
    statement_type = models.CharField(max_length=2, choices=STATEMENT_TYPE, default="IS")
    period_type = models.CharField(max_length=2, choices=PERIOD_TYPE, default="FY")
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    display_unit = models.CharField(max_length=10, choices=DISPLAY_UNIT, default="1000000")

    # Financial Data Details
    ticker = models.CharField(max_length=10, db_index=True)
    company_name = models.CharField(max_length=200)
    fiscal_year = models.IntegerField(db_index=True)
    fiscal_period = models.CharField(max_length=5, choices=PERIOD_TYPE)
    metric_name = models.CharField(max_length=100, db_index=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = "Request"
        verbose_name_plural = "Requests"

    def __str__(self):
        return f"{self.report_name} - {self.ticker}"