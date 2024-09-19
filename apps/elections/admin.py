from django.contrib import admin
from django.http import HttpRequest

from .models import ElectionConfig
from .forms import ElectionConfigForm


@admin.register(ElectionConfig)
class ElectionConfigAdmin(admin.ModelAdmin):
    list_display = (
        "election_starts",
        "election_ends",
        "election_ongoing",
        "election_upcoming",
        "election_ended",
    )
    list_filter = ("election_starts", "election_ends")
    search_fields = ("election_starts", "election_ends")
    date_hierarchy = "election_starts"
    ordering = ("election_starts",)
    fields = (
        "election_starts",
        "election_ends",
    )
    actions = None
    save_on_top = True
    save_as = True
    list_per_page = 10
    list_max_show_all = 100
    list_editable = ()
    list_display_links = ()
    list_select_related = False
    list_display_links = ()
    form = ElectionConfigForm

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request: HttpRequest) -> bool:
        return request.user.is_admin
    

    def get_election_ongoing(self, obj: ElectionConfig):
        return obj.election_ongoing

    def get_election_upcoming(self, obj: ElectionConfig):
        return obj.election_upcoming

    def get_election_ended(self, obj: ElectionConfig):
        return obj.election_ended

    get_election_ongoing.boolean = True
    get_election_upcoming.boolean = True
    get_election_ended.boolean = True

    get_election_ongoing.short_description = "Election Ongoing"
    get_election_upcoming.short_description = "Election Upcoming"
    get_election_ended.short_description = "Election Ended"
