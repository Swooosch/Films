from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_review
from django.views.generic import ListView
from taggit.models import Tag
from .forms import DiscussionForm
from .models import review, discussion


def review_list(request):
    """
    The request parameter is required by all views!
    Here we get all reviews using our custom manager (i.e the PublishedManager)
    It retrieves all reviews with a status of PUBLISHED
    """
    review_list = review.published.all()
    # Pagination with 3 reviews per page
    paginator = Paginator(review_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        reviews = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer get the first page
        reviews = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range get last page of results
        reviews = paginator.page(paginator.num_pages)

    return render(
        request,
        'review/review/list.html',
        {'reviews': reviews}
    )


def review_detail(request, year, month, day, review):
    """
    This review detail view takes the id arguement of a review. It uses the
    get_object_or_404 shortcut.
    If the review is not found a HTTP 404 exception is raised.
    """
    review = get_object_or_404(
        Review,
        status=Review.Status.PUBLISHED,
        slug=review,
        created_on__year=year,
        created_on__month=month,
        created_on__day=day
    )

    discussions = review.discussions.filter(is_active=True)
    form = discussionForm()
    most_discussioned_reviews = Review.published.most_discussioned()

    return render(
        request,
        'review/review/detail.html',
        {
            'review': review,
            'discussions': discussions,
            'form': form,
            'most_discussioned_reviews': most_discussioned_reviews
        }
    )



class ReviewListView(ListView):
    """
    Alternative review list view
    """
    queryset = Review.published.all()
    context_object_name = 'reviews'
    paginate_by = 3
    template_name = 'review/review/list.html'

    def get_queryset(self):
        queryset = review.published.all()
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            self.tag = get_object_or_404(Tag, slug=tag_slug)
            queryset = queryset.filter(tags__in=[self.tag])
        else:
            self.tag = None
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        context['most_discussioned_reviews'] = review.published.most_discussioned()
        return context


@login_required
@require_review
def review_discussion(request, review_id):
    review = get_object_or_404(review, id=review_id, status=review.Status.PUBLISHED)
    form = discussionForm(data=request.review)
    if form.is_valid():
        discussion = form.save(commit=False)
        discussion.review = review
        discussion.user = request.user
        discussion.save()
        return redirect(
            'review:review_detail',
            year=review.created_on.year,
            month=review.created_on.month,
            day=review.created_on.day,
            review=review.slug
        )
    return render(
        request,
        'review/review/detail.html',
        {'review': review, 'form': form}
    )


@login_required
def edit_discussion(request, discussion_id):
    discussion = get_object_or_404(discussion, id=discussion_id, user=request.user)
    if request.method == 'review':
        form = DiscussionForm(request.review, instance=discussion)
        if form.is_valid():
            form.save()
            return redirect(
                'review:review_detail',
                year=discussion.review.created_on.year,
                month=discussion.review.created_on.month,
                day=discussion.review.created_on.day,
                review=discussion.review.slug
            )
    else:
        form = DiscussionForm(instance=discussion)
    return render(
        request,
        'review/review/discussion/edit_discussion.html',
        {'form': form}
    )


@login_required
def delete_discussion(request, discussion_id):
    discussion = get_object_or_404(Discussion, id=discussion_id, user=request.user)
    review = discussion.review
    if request.method == 'review':
        discussion.delete()
        return redirect(
            'review:review_detail',
            year=review.created_on.year,
            month=review.created_on.month,
            day=review.created_on.day,
            review=review.slug
        )
    return render(
        request,
        'review/review/discussion/delete_discussion.html',
        {'discussion': discussion}
    )