from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404

from .models import Question

# Create your views here.

def index(request):
	"""Displays a landing page showing the latest 5 poll questions"""
	latest_question_list = Question.objects.order_by('-pub_date')[:5]
	context = {'latest_question_list': latest_question_list}
	return render(request, 'polls/index.html', context)

def detail(request, question_id):
	"""Shows info for a specific question based on its ID number"""
	question = get_object_or_404(Question, pk=question_id)
	return render(request, 'polls/detail.html', {'qusetion': question})

def results(request, question_id):
	"""Shows results for a specific question based on its ID number"""
	response = "You're looking at the results of question %s."
	return HttpResponse(response % question_id)

def vote(request, question_id):
	"""Vote on a specific question based on its ID number"""
	return HttpResponse("You're voting on question %s." %question_id)