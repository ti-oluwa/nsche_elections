from django.contrib import admin

from .models import Election, Office, Candidate
from .forms import ElectionForm, OfficeForm, CandidateForm


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "start_date",
        "end_date",
        "is_ongoing",
        "is_upcoming",
        "has_ended",
    )
    list_filter = ("start_date", "end_date")
    search_fields = ("name",)
    date_hierarchy = "start_date"
    ordering = ("-start_date", "name")
    fields = ("name", "start_date", "end_date")
    actions = None
    save_on_top = True
    save_as = True
    list_per_page = 20
    form = ElectionForm

    def has_add_permission(self, request):
        # Only allow superusers or staff to add elections
        return request.user.is_superuser or request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of elections
        return False

    def has_change_permission(self, request, obj=None):
        # Only allow superusers to change ongoing or ended elections
        if obj and (obj.is_ongoing or obj.has_ended):
            return request.user.is_superuser
        return True

    def is_ongoing(self, obj):
        return obj.is_ongoing

    is_ongoing.boolean = True
    is_ongoing.short_description = "Ongoing"

    def is_upcoming(self, obj):
        return obj.is_upcoming

    is_upcoming.boolean = True
    is_upcoming.short_description = "Upcoming"

    def has_ended(self, obj):
        return obj.has_ended

    has_ended.boolean = True
    has_ended.short_description = "Ended"


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ("name", "election", "is_active", "leading_candidate")
    list_filter = ("election__name", "is_active")
    search_fields = ("name", "election__name")
    ordering = ("name",)
    fields = ("name", "description", "election", "is_active")
    actions = None
    save_on_top = True
    save_as = True
    form = OfficeForm

    def get_queryset(self, request):
        return super().get_queryset(request).with_leading_candidate()

    def has_add_permission(self, request):
        # Only allow superusers to add new offices
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Restrict changes to ongoing or ended elections
        if obj and (obj.election.is_ongoing or obj.election.has_ended):
            return request.user.is_superuser
        return True

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of offices once they are part of ongoing or ended elections
        if obj and (obj.election.is_ongoing or obj.election.has_ended):
            return False
        return request.user.is_superuser

    def leading_candidate(self, obj):
        return obj.leading_candidate or "--"

    leading_candidate.short_description = "Leading Candidate"


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("name", "office", "disqualified", "votes_count")
    list_filter = ("office__name", "disqualified")
    search_fields = ("name", "office__name")
    ordering = ("name",)
    fields = ("name", "office", "manifesto", "disqualified")
    actions = None
    save_on_top = True
    save_as = True
    form = CandidateForm
    
    def get_queryset(self, request):
        return super().get_queryset(request).with_votes_count()

    def has_add_permission(self, request):
        # Only allow superusers or election managers to add candidates
        return (
            request.user.is_superuser
            or request.user.groups.filter(name="Election Managers").exists()
        )

    def has_change_permission(self, request, obj=None):
        # Prevent changes to candidates in ongoing or ended elections unless by superuser
        if obj and (obj.office.election.is_ongoing or obj.office.election.has_ended):
            return request.user.is_superuser
        return True

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of candidates in ongoing or ended elections
        if obj and (obj.office.election.is_ongoing or obj.office.election.has_ended):
            return False
        return request.user.is_superuser

    def votes_count(self, obj):
        return obj.votes_count

    votes_count.short_description = "Valid Votes"
