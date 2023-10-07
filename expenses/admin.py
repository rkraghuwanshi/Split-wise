from django.contrib import admin

from expenses.models import UserProfile,  Group, Expense, ExpenseUser, Debt

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Group)
admin.site.register(Expense)
admin.site.register(ExpenseUser)
admin.site.register(Debt)