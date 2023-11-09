from django.contrib import admin

from collection.models import Artist, Genre, Style, Period, Artwork, Collection

#3class ArtWorlInline(admin.TabularInline):
#    model = Artwork

#class ArtworkAdmin(admin.ModelAdmin):
#    filter_horizontal = ('credits', )
#    inlines = (ArtWorlInline, )


admin.site.register(Artwork)
admin.site.register(Artist)
admin.site.register(Genre)
admin.site.register(Style)
admin.site.register(Period)
admin.site.register(Collection)
