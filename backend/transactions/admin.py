from django.contrib import admin
from .models import Transaction, TransactionItem

admin.site.register(Transaction)
admin.site.register(TransactionItem)
