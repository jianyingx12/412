from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Voter
from typing import Any
from django.db.models import QuerySet
from django.utils.dateparse import parse_date
import plotly.graph_objects as go
from django.db.models import Count
from plotly.offline import plot

# Create your views here.

class VoterListView(ListView):
    '''View to show a list of voter records with filtering and pagination.'''
    model = Voter
    template_name = 'voter_analytics/voter_list.html'  
    context_object_name = 'voters'
    paginate_by = 100  # Show 100 voters per page

    def get_queryset(self) -> QuerySet[Any]:
        '''Filter the results based on the search parameters if provided.'''
        queryset = super().get_queryset()

        # Retrieve filter parameters from the GET request
        party = self.request.GET.get('party_affiliation')
        min_dob = self.request.GET.get('min_dob')
        max_dob = self.request.GET.get('max_dob')
        voter_score = self.request.GET.get('voter_score')
        
        # Filter by party affiliation
        if party:
            queryset = queryset.filter(party_affiliation=party)
        
        # Filter by minimum date of birth
        if min_dob:
            queryset = queryset.filter(date_of_birth__gte=parse_date(f"{min_dob}-01-01"))
        
        # Filter by maximum date of birth
        if max_dob:
            queryset = queryset.filter(date_of_birth__lte=parse_date(f"{max_dob}-12-31"))
        
        # Filter by voter score
        if voter_score:
            queryset = queryset.filter(voter_score=int(voter_score))

        # Filter by election participation checkboxes
        for field in ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']:
            if self.request.GET.get(field):
                queryset = queryset.filter(**{field: True})

        return queryset

    def get_context_data(self, **kwargs):
        '''Add additional context data for rendering the form.'''
        context = super().get_context_data(**kwargs)
        
        # Add unique party affiliations for the drop-down list
        context['party_affiliations'] = Voter.objects.values_list('party_affiliation', flat=True).distinct()
        
        # Add a range of years for filtering by date of birth
        context['year_range'] = range(1900, 2024)  
        
        # Add possible voter scores for the drop-down list
        context['voter_scores'] = range(0, 6)  
        
        return context

    
class VoterDetailView(DetailView):
    '''View to list voter details.'''
    model = Voter
    template_name = 'voter_analytics/voter_detail.html'

class GraphsView(ListView):
    '''View to display graphs.'''
    model = Voter
    template_name = 'voter_analytics/graphs.html'
    context_object_name = 'voters'

    def get_queryset(self) -> QuerySet[Any]:
        '''Filter the results based on the search parameters if provided.'''
        queryset = super().get_queryset()

        # Apply filters similar to those in VoterListView
        party = self.request.GET.get('party_affiliation')
        min_dob = self.request.GET.get('min_dob')
        max_dob = self.request.GET.get('max_dob')
        voter_score = self.request.GET.get('voter_score')

        # Filter by party affiliation
        if party:
            queryset = queryset.filter(party_affiliation=party)
        
        # Filter by minimum date of birth
        if min_dob:
            queryset = queryset.filter(date_of_birth__gte=parse_date(f"{min_dob}-01-01"))
        
        # Filter by maximum date of birth
        if max_dob:
            queryset = queryset.filter(date_of_birth__lte=parse_date(f"{max_dob}-12-31"))
        
        # Filter by voter score
        if voter_score:
            queryset = queryset.filter(voter_score=int(voter_score))

        # Filter by election participation checkboxes
        for field in ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']:
            if self.request.GET.get(field):
                queryset = queryset.filter(**{field: True})

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        # Add unique party affiliations for the drop-down list
        context['party_affiliations'] = Voter.objects.values_list('party_affiliation', flat=True).distinct()
        
        # Add a range of years for filtering by date of birth
        context['year_range'] = range(1900, 2024)  
        
        # Add possible voter scores for the drop-down list
        context['voter_scores'] = range(0, 6) 

        # Aggregate data: count voters by year of birth
        year_counts = queryset.values('date_of_birth__year').annotate(count=Count('id')).order_by('date_of_birth__year')
        years = [entry['date_of_birth__year'] for entry in year_counts]
        counts = [entry['count'] for entry in year_counts]

        # Histogram for Year of Birth 
        year_of_birth_chart = go.Figure(
            data=[go.Bar(x=years, y=counts, opacity=1)],  
            layout=go.Layout(
                title=f'Voter distribution by Year of Birth (n={queryset.count()})',
                xaxis_title='Year of Birth',
                yaxis_title='Number of Voters',
            )
        )
        year_of_birth_plot = plot(year_of_birth_chart, output_type='div')

        # Pie chart for Party Affiliation
        party_counts = queryset.values('party_affiliation').annotate(count=Count('id'))
        parties = [entry['party_affiliation'] for entry in party_counts]
        party_counts_values = [entry['count'] for entry in party_counts]

        party_chart = go.Figure(
            data=[go.Pie(labels=parties, values=party_counts_values)],
            layout=go.Layout(title=f'Voter distribution by Party Affiliation (n={queryset.count()})')
        )
        party_plot = plot(party_chart, output_type='div')

        # Histogram for Participation in Elections
        elections = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
        election_counts = [queryset.filter(**{election: True}).count() for election in elections]

        election_chart = go.Figure(
            data=[go.Bar(x=elections, y=election_counts)],
            layout=go.Layout(
                title=f'Vote Count by Election (n={queryset.count()})',
                xaxis_title='Election',
                yaxis_title='Number of Voters'
            )
        )
        election_plot = plot(election_chart, output_type='div')

        # Add plots to context
        context['year_of_birth_plot'] = year_of_birth_plot
        context['party_plot'] = party_plot
        context['election_plot'] = election_plot

        return context