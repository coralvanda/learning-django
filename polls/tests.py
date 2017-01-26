import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Choice, Question

def create_question(question_text, days, have_choice=True, votes=False):
	"""
		Creates a question with the given 'question_text' and publshed the
		given number of 'days' offset to now (negative for questions published)
		in the past, positive for questions that have yet to be published).
		Automatically creates a choice for each question unless told not to.
		Accepts numbers as an optional 'votes' field, and assigns that
		number to the question's choice's vote count.
	"""
	time = timezone.now() + datetime.timedelta(days=days)
	question = Question.objects.create(
		question_text=question_text, pub_date=time)
	if have_choice:
		if votes:
			choice = Choice.objects.create(
				question=question,
				choice_text="A choice",
				votes=votes)
		else:
			choice = Choice.objects.create(
				question=question,
				choice_text="A choice")
	return question

def question_builder(number_of_normal_questions,
					number_of_future_questions=0,
					number_of_questions_with_no_choices=0,
					number_of_questions_with_various_votes=0):
	"""
		Creates a specified number of questions, with the option to create
		questions dated from the future, questions without choices, and
		questions with varying numbers of votes.  Returns a list of each
		question created that is dated in the past and has at least one choice,
		ordered by most recently created.
	"""
	question_response_text = []
	for x in range(number_of_normal_questions):
		create_question(
			question_text="Past question " + str(x + 1) + ".", days=-30)
		question_response_text.append(
			"<Question: Past question " + str(x + 1) + ".>")
	for x in range(number_of_future_questions):
		create_question(
			question_text="Future question " + str(x + 1) + ".", days=30)
	for x in range(number_of_questions_with_no_choices):
		create_question(
			question_text="No choices.", days=-30, have_choice=False)
	for x in range(number_of_questions_with_various_votes):
		create_question(
			question_text="Popular question " + str(x + 1) + ".", days=-30,
			votes=x + 1)
		question_response_text.append(
			"<Question: Popular question " + str(x + 1) + ".>")
	return question_response_text[::-1]


class QuestionMethodTests(TestCase):

	def test_was_published_recently_with_future_question(self):
		"""
			was_published_recently() should return False for questions
			whose pub_date is in the future
		"""
		time = timezone.now() + datetime.timedelta(days=30)
		future_question = Question(pub_date=time)
		self.assertIs(future_question.was_published_recently(), False)

	def test_was_published_recently_with_old_question(self):
		"""
			was_published_recently() should return False for questions whose
			pub_date is older than 1 day
		"""
		time = timezone.now() - datetime.timedelta(days=30)
		old_question = Question(pub_date=time)
		self.assertIs(old_question.was_published_recently(), False)

	def test_was_published_recently_with_recent_question(self):
		"""
			was_published_recently() should return True for questions whose
			pub_date is within the last day
		"""
		time = timezone.now() - datetime.timedelta(hours=1)
		recent_question = Question(pub_date=time)
		self.assertIs(recent_question.was_published_recently(), True)


class QuestionViewTests(TestCase):

	def test_index_view_with_no_questions(self):
		"""
			If no questions exist, an appropriate message should be displayed
		"""
		response = self.client.get(reverse('polls:index'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(response.context['latest_question_list'], [])

	def test_index_view_with_a_past_question(self):
		"""
			Questions with a pub_date in the past should be displayed
			on the index page
		"""
		create_question(question_text="Past question.",
			days=-30, have_choice=True)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(
			response.context['latest_question_list'],
			['<Question: Past question.>'])

	def test_index_view_with_a_future_question(self):
		"""
			Questions with a pub_date in the future should not be displayed
			on the index page
		"""
		create_question(question_text="Future question.",
			days=30, have_choice=True)
		response = self.client.get(reverse('polls:index'))
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(response.context['latest_question_list'], [])

	def test_index_view_with_future_question_and_past_question(self):
		"""
			Even if both past and future questions exist, only past questions
			should be displayed
		"""
		response_text = question_builder(1, number_of_future_questions=1)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(
			response.context['latest_question_list'],
			response_text)

	def test_index_view_with_two_past_questions(self):
		"""
			The questions index page may display multiple questions
		"""
		response_text = question_builder(2)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(
			response.context['latest_question_list'],
			response_text)

	def test_index_view_with_question_that_has_no_choice(self):
		"""
			Questions that do not have at least 1 choice should not
			be displayed
		"""
		create_question(question_text="No choice.", days=-5, have_choice=False)
		response = self.client.get(reverse('polls:index'))
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(response.context['latest_question_list'], [])


class QuestionDetailViewTests(TestCase):

	def test_detail_view_with_a_future_question(self):
		"""
			The detail view of a question with a pub_date in the future
			should return a 404 not found
		"""
		future_question = create_question(question_text='Future question.',
			days=5, have_choice=True)
		url = reverse('polls:detail', args=(future_question.id,))
		response = self.client.get(url)
		self.assertEqual(response.status_code, 404)

	def test_detail_view_with_a_past_question(self):
		"""
			The detail view of a question with a pub_date in the past should
			display the question's text
		"""
		past_question = create_question(question_text='Past question.',
			days=-5, have_choice=True)
		url = reverse('polls:detail', args=(past_question.id,))
		response = self.client.get(url)
		self.assertContains(response, past_question.question_text)

	def test_detail_view_with_question_that_has_no_choice(self):
		"""
			The detail view of a question without at least 1 choice
			should return a 404 not found
		"""
		no_choice_question = create_question(
			question_text="No choice.", days=-5, have_choice=False)
		url = reverse('polls:detail', args=(no_choice_question.id,))
		response = self.client.get(url)
		self.assertEqual(response.status_code, 404)


class QuestionResultViewTests(TestCase):

	def test_results_view_with_a_future_question(self):
		"""
			The results view of a question with a pub_date in the future
			should return a 404 not found
		"""
		future_question = create_question(question_text='Future question.',
			days=5, have_choice=True)
		url = reverse('polls:results', args=(future_question.id,))
		response = self.client.get(url)
		self.assertEqual(response.status_code, 404)

	def test_results_view_with_a_past_question(self):
		"""
			The results view of a question with a pub_date in the past should
			display the question's text and voting results
		"""
		past_question = create_question(question_text='Past question.',
			days=-5, have_choice=True)
		url = reverse('polls:results', args=(past_question.id,))
		response = self.client.get(url)
		self.assertContains(response, past_question.question_text)

	def test_results_view_with_question_that_has_no_choice(self):
		"""
			The results view of a question without at least 1 choice
			should return a 404 not found
		"""
		no_choice_question = create_question(
			question_text="No choice.", days=-5, have_choice=False)
		url = reverse('polls:results', args=(no_choice_question.id,))
		response = self.client.get(url)
		self.assertEqual(response.status_code, 404)


class QuestionAllViewTests(TestCase):

	def test_all_view_with_no_questions(self):
		"""
			If no questions exist, an appropriate message should be displayed
		"""
		response = self.client.get(reverse('polls:all'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(response.context['full_question_list'], [])

	def test_all_view_with_a_past_question(self):
		"""
			Questions with a pub_date in the past should be displayed
			on the all page
		"""
		create_question(question_text="Past question.", days=-30)
		response = self.client.get(reverse('polls:all'))
		self.assertQuerysetEqual(
			response.context['full_question_list'],
			['<Question: Past question.>'])

	def test_all_view_with_a_future_question(self):
		"""
			Questions with a pub_date in the future should not be displayed
			on the all page
		"""
		create_question(question_text="Future question.", days=30)
		response = self.client.get(reverse('polls:all'))
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(response.context['full_question_list'], [])

	def test_all_view_with_future_question_and_past_question(self):
		"""
			Even if both past and future questions exist, only past questions
			should be displayed
		"""
		response_text = question_builder(1, number_of_future_questions=1)
		response = self.client.get(reverse('polls:all'))
		self.assertQuerysetEqual(
			response.context['full_question_list'],
			response_text)

	def test_all_view_with_many_past_questions(self):
		"""
			The all page may display multiple questions
		"""
		response_text = question_builder(10)
		response = self.client.get(reverse('polls:all'))
		self.assertQuerysetEqual(
			response.context['full_question_list'],
			response_text)

	def test_all_view_with_question_that_has_no_choice(self):
		"""
			Questions that do not have at least 1 choice should not
			be displayed
		"""
		create_question(question_text="No choice.", days=-5, have_choice=False)
		response = self.client.get(reverse('polls:all'))
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(response.context['full_question_list'], [])

	def text_all_view_with_many_questions_incl_future_and_choiceless(self):
		"""
			Displays all past questions, ignores future and choiceless questions
		"""
		response_text = question_builder(10, number_of_future_questions=1,
			number_of_questions_with_no_choices=1)
		response = self.client.get(reverse('polls:all'))
		self.assertQuerysetEqual(
			response.context['full_question_list'],
			response_text)


class QuestionPopularViewTests(TestCase):

	def test_popular_view_with_no_questions(self):
		"""
			If no questions exist, an appropriate message should be displayed
		"""
		response = self.client.get(reverse('polls:popular'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(response.context['popular_question_list'], [])

	def test_popular_view_with_a_past_question(self):
		"""
			Questions with a pub_date in the past should be displayed
			on the popular page
		"""
		create_question(question_text="Past question.", days=-30)
		response = self.client.get(reverse('polls:popular'))
		self.assertQuerysetEqual(
			response.context['popular_question_list'],
			['<Question: Past question.>'])

	def test_popular_view_with_a_future_question(self):
		"""
			Questions with a pub_date in the future should not be displayed
			on the popular page
		"""
		create_question(question_text="Future question.", days=30)
		response = self.client.get(reverse('polls:popular'))
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(response.context['popular_question_list'], [])

	def test_popular_view_with_future_question_and_past_question(self):
		"""
			Even if both past and future questions exist, only past questions
			should be displayed
		"""
		response_text = question_builder(1, number_of_future_questions=1)
		response = self.client.get(reverse('polls:popular'))
		self.assertQuerysetEqual(
			response.context['popular_question_list'],
			response_text)

	def test_popular_view_with_many_past_questions(self):
		"""
			The popular page may display multiple questions
		"""
		response_text = question_builder(10)
		response = self.client.get(reverse('polls:popular'))
		self.assertEqual(len(response.context['popular_question_list']), 5)

	def test_popular_view_with_question_that_has_no_choice(self):
		"""
			Questions that do not have at least 1 choice should not
			be displayed
		"""
		create_question(question_text="No choice.", days=-5, have_choice=False)
		response = self.client.get(reverse('polls:popular'))
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(response.context['popular_question_list'], [])

	def test_popular_view_with_many_questions_some_with_votes(self):
		"""
			Displays only 5 most popular questions, ignores others
		"""
		response_text = question_builder(5, number_of_future_questions=1,
			number_of_questions_with_no_choices=1,
			number_of_questions_with_various_votes=5)
		response = self.client.get(reverse('polls:popular'))
		self.assertQuerysetEqual(response.context['popular_question_list'],
			response_text[:5:-1])