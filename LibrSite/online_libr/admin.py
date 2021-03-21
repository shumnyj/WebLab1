from django.contrib import admin

from . import models as olm

admin.site.register(olm.LibUser)
admin.site.register(olm.Book)
admin.site.register(olm.ReadStatus)
admin.site.register(olm.Review)
