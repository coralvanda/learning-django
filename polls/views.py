from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.views import generic
from django.db.models import F, Count
from django.utils import timezone

from .models import Choice, Question


class IndexView(generic.ListView):
	"""
		Displays a landing page showing the latest 5 poll questions
	"""
	template_name = 'polls/index.html'
	context_object_name = 'latest_question_list'

	def get_queryset(self):
		"""
			Return the last five published questions (not including those
			set to be published in the future or ones without a choice)
		"""
		return Question.objects \
			.annotate(choice_cnt=Count('choice')) \
			.exclude(choice_cnt=0) \
			.filter(pub_date__lte=timezone.now()) \
			.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
	"""
		Shows info for a specific question based on its ID number
	"""
	model = Question
	template_name = 'polls/detail.html'

	def get_queryset(self):
		"""
			Excludes any questions that aren't published yet, and
			any questions without a choice
		"""
		return Question.objects \
			.annotate(choice_cnt=Count('choice')) \
			.exclude(choice_cnt=0) \
			.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
	"""
		Shows results for a specific question based on its ID number
	"""
	model = Question
	template_name = 'polls/results.html'

	def get_queryset(self):
		"""
			Excludes any questions that aren't published yet, and
			any questions without a choice
		"""
		return Question.objects \
			.annotate(choice_cnt=Count('choice')) \
			.exclude(choice_cnt=0) \
			.filter(pub_date__lte=timezone.now())


def vote(request, question_id):
	"""
		Vote on a specific question based on its ID number
	"""
	question = get_object_or_404(Question, pk=question_id)
	try:
		selected_choice = question.choice_set.get(pk=request.POST['choice'])
	except (KeyError, Choice.DoesNotExist):
		# Redisplay the question voting form
		return render(request, 'polls/detail.html',
			{'question': question,
			'error_message': "You didn't select a choice."})
	else:
		selected_choice.votes = F('votes') + 1
		selected_choice.save()
		# Always return an HttpResponseRedirect after successfully dealing
		# with POST data. This prevents data from being posted twice if a
		# user hits the Back button.
		return HttpResponseRedirect(reverse('polls:results',
			args=(question.id,)))
