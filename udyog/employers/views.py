from django.shortcuts import render, redirect, get_object_or_404
from .models import Job, Applicants, Selected, JobReport 
from candidates.models import Profile, Skill, User
from .forms import NewJobForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db import connection
from django.db.models import F
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete


def rec_details(request):
    context = {
        'rec_home_page': "active",
        'rec_navbar': 1,
    }
    return render(request, 'employers/details.html', context)


@login_required
def add_job(request):
    user = request.user
    if request.method == "POST":
        form = NewJobForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.employer = user
            data.save()

            # Call the stored procedure to update the job report
            with connection.cursor() as cursor:
                cursor.execute("CALL GenerateJobReport();")
            
            # Commit the transaction
            connection.commit()

            return redirect('job-list')
    else:
        form = NewJobForm()
    context = {
        'add_job_page': "active",
        'form': form,
        'rec_navbar': 1,
    }
    return render(request, 'employers/add_job.html', context)


@login_required
def edit_job(request, slug):
    user = request.user
    job = get_object_or_404(Job, slug=slug)
    if request.method == "POST":
        form = NewJobForm(request.POST, instance=job)
        if form.is_valid():
            data = form.save(commit=False)
            data.save()
            return redirect('add-job-detail', slug)
    else:
        form = NewJobForm(instance=job)
    context = {
        'form': form,
        'rec_navbar': 1,
        'job': job,
    }
    return render(request, 'employers/edit_job.html', context)


@login_required
def job_detail(request, slug):
    job = get_object_or_404(Job, slug=slug)
    context = {
        'job': job,
        'rec_navbar': 1,
    }
    return render(request, 'employers/job_detail.html', context)


@login_required
def all_jobs(request):
    jobs = Job.objects.filter(employer=request.user).order_by('-date_posted')
    paginator = Paginator(jobs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'manage_jobs_page': "active",
        'jobs': page_obj,
        'rec_navbar': 1,
    }
    return render(request, 'employers/job_posts.html', context)


@login_required
def search_candidates(request):
    profile_list = Profile.objects.exclude(user=request.user)
    profiles = profile_list.filter(resume__isnull=False).distinct()

    rec1 = request.GET.get('r')
    rec2 = request.GET.get('s')
    rec_filter = request.GET.get('filter', 'recent')

    if rec1:
        profiles = profiles.filter(location__icontains=rec1)

    if rec2:
        profiles = profiles.filter(looking_for__icontains=rec2)

    if rec_filter == 'recent':
        profiles = profiles.filter(user__date_joined__gte=F('user__last_login'))

    paginator = Paginator(profiles, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'search_candidates_page': "active",
        'rec_navbar': 1,
        'profiles': page_obj,
        'filter_option': rec_filter,  # Pass the filter option to the template
    }
    return render(request, 'employers/candidate_search.html', context)


@login_required
def job_candidate_search(request, slug):
    job = get_object_or_404(Job, slug=slug)
    relevant_candidates = []
    common = []
    applicants = Profile.objects.filter(looking_for=job.job_type)
    job_skills = []
    skills = str(job.skills_req).split(",")
    for skill in skills:
        job_skills.append(skill.strip().lower())
    for applicant in applicants:
        user = applicant.user
        skill_list = list(Skill.objects.filter(user=user))
        skills = []
        for i in skill_list:
            skills.append(i.skill.lower())
        common_skills = list(set(job_skills) & set(skills))
        if (len(common_skills) != 0 and len(common_skills) >= len(job_skills)//2):
            relevant_candidates.append(applicant)
            common.append(len(common_skills))
    objects = zip(relevant_candidates, common)
    objects = sorted(objects, key=lambda t: t[1], reverse=True)
    objects = objects[:100]
    context = {
        'rec_navbar': 1,
        'job': job,
        'objects': objects,
        'job_skills': len(job_skills),
        'relevant': len(relevant_candidates),

    }
    return render(request, 'employers/job_candidate_search.html', context)


@login_required
def applicant_list(request, slug):
    job = get_object_or_404(Job, slug=slug)
    
    # Get the filter option from the query parameter (recent or all)
    filter_option = request.GET.get('filter', 'recent')

    if filter_option == 'recent':
        applicants = Applicants.objects.filter(job=job).order_by('-date_posted')[:10]
    else:
        applicants = Applicants.objects.filter(job=job).order_by('-date_posted')

    profiles = [Profile.objects.filter(user=applicant.applicant).first() for applicant in applicants]

    context = {
        'rec_navbar': 1,
        'profiles': profiles,
        'job': job,
        'filter_option': filter_option,
    }

    return render(request, 'employers/applicant_list.html', context)


@login_required
def selected_list(request, slug):
    job = get_object_or_404(Job, slug=slug)

    # Get the filter option from the query parameter (recent or all)
    filter_option = request.GET.get('filter', 'recent')

    if filter_option == 'recent':
        selected = Selected.objects.filter(job=job).order_by('-date_posted')[:10]
    else:
        selected = Selected.objects.filter(job=job).order_by('-date_posted')

    profiles = [Profile.objects.filter(user=applicant.applicant).first() for applicant in selected]

    context = {
        'rec_navbar': 1,
        'profiles': profiles,
        'job': job,
        'filter_option': filter_option,
    }

    return render(request, 'employers/selected_list.html', context)


@login_required
def select_applicant(request, can_id, job_id):
    job = get_object_or_404(Job, slug=job_id)
    profile = get_object_or_404(Profile, slug=can_id)
    user = profile.user
    selected, created = Selected.objects.get_or_create(job=job, applicant=user)
    applicant = Applicants.objects.filter(job=job, applicant=user).first()
    applicant.delete()
    return HttpResponseRedirect('/hiring/job/{}/applicants'.format(job.slug))


@login_required
def remove_applicant(request, can_id, job_id):
    job = get_object_or_404(Job, slug=job_id)
    profile = get_object_or_404(Profile, slug=can_id)
    user = profile.user
    applicant = Applicants.objects.filter(job=job, applicant=user).first()
    applicant.delete()
    return HttpResponseRedirect('/hiring/job/{}/applicants'.format(job.slug))


def job_reports(request):
    # Retrieve the job reports
    job_reports = JobReport.objects.filter(job__employer=request.user)

    # Call MySQL functions to get total counts
    total_applicants_count = get_total_applicants_count(request.user.id)
    total_selected_count = get_total_selected_count(request.user.id)

    context = {
        'job_reports': job_reports,
        'total_applicants_count': total_applicants_count,
        'total_selected_count': total_selected_count,
        'rec_navbar': 1,
    }

    return render(request, 'employers/job_reports.html', context)

@login_required
def regenerate_job_report(request):
    # Call the stored procedure to generate the report
    with connection.cursor() as cursor:
        cursor.execute("CALL GenerateJobReport();")
    
    # Commit the transaction
    connection.commit()

    # Retrieve the generated report
    reports = JobReport.objects.all()  # Adjust this query to retrieve your reports

    # You should adjust the query above to retrieve the report data as needed

    return render(request, 'employers/job_reports.html', {'reports': reports})


@receiver(post_save, sender=Applicants)
def update_job_report(sender, instance, **kwargs):
    job = instance.job
    report, created = JobReport.objects.get_or_create(job=job)
    report.applicants.set(Applicants.objects.filter(job=job))
    report.selected.set(Selected.objects.filter(job=job))
    report.save()


def get_total_applicants_count(employer_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT CalculateTotalApplicants(%s);", [employer_id])
        total_applicants_count = cursor.fetchone()[0]
    return total_applicants_count


def get_total_selected_count(employer_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT CalculateTotalSelectedCandidates(%s);", [employer_id])
        total_selected_count = cursor.fetchone()[0]
    return total_selected_count