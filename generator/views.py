from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Deal
from .forms import DealForm
from core.models import log_activity


@login_required
def deal_list(request):
    deals = Deal.objects.filter(is_active=True).select_related('company', 'assigned_to')
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    if query:
        deals = deals.filter(name__icontains=query)
    if status_filter:
        deals = deals.filter(status=status_filter)
    if priority_filter:
        deals = deals.filter(priority=priority_filter)
    paginator = Paginator(deals, 12)
    page = request.GET.get('page', 1)
    deals_page = paginator.get_page(page)
    return render(request, 'generators/deal_list.html', {
        'deals': deals_page,
        'query': query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    })


@login_required
def deal_detail(request, slug):
    deal = get_object_or_404(Deal.objects.select_related('company', 'assigned_to'), slug=slug)
    return render(request, 'generators/deal_detail.html', {'deal': deal})


@login_required
def deal_create(request):
    form = DealForm()
    if request.method == 'POST':
        form = DealForm(request.POST)
        if form.is_valid():
            deal = form.save(commit=False)
            deal.created_by = request.user
            deal.save()
            form.save_m2m()
            log_activity(request.user, 'created', f'Deal "{deal.name}"', deal)
            messages.success(request, 'Deal created successfully.')
            return redirect('generators:list')
    return render(request, 'generators/deal_create_page.html', {'form': form, 'title': 'Add Deal', 'is_page': True})


@login_required
def deal_edit(request, slug):
    deal = get_object_or_404(Deal, slug=slug)
    form = DealForm(instance=deal)
    if request.method == 'POST':
        form = DealForm(request.POST, instance=deal)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'updated', f'Deal "{deal.name}"', deal)
            messages.success(request, 'Deal updated successfully.')
            return redirect('generators:detail', slug=deal.slug)
    return render(request, 'generators/deal_edit_page.html', {
        'form': form,
        'title': 'Edit Deal',
        'deal': deal,
        'is_page': True,
    })


@login_required
def deal_delete(request, slug):
    deal = get_object_or_404(Deal, slug=slug)
    if request.method == 'POST':
        deal.is_active = False
        deal.save()
        log_activity(request.user, 'deleted', f'Deal "{deal.name}"')
        messages.success(request, 'Deal deleted successfully.')
    return redirect('generators:list')


@login_required
def deal_create_slide(request):
    form = DealForm()
    return render(request, 'generators/deal_form.html', {'form': form, 'title': 'Add Deal'})


@login_required
def deal_edit_slide(request, slug):
    deal = get_object_or_404(Deal, slug=slug)
    form = DealForm(instance=deal)
    return render(request, 'generators/deal_form.html', {'form': form, 'title': 'Edit Deal', 'deal': deal})