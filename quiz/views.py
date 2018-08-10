# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
import collections

from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect, HttpResponse, HttpResponseRedirect, reverse
from django.utils.decorators import method_decorator

# FileResponse - to display files
from django.http import FileResponse, Http404

from django.views import generic
from django.views.generic import DetailView, ListView, TemplateView, FormView, View

from .forms import QuestionForm, EssayForm
from .models import Quiz, Category, Progress, Sitting, Question
from essay.models import Essay_Question
from users.models import ProfileModel
#from jchart import Chart
#from jchart.config import DataSet

#from .charts import lineChart, progressChart

from .resources import sittingResource, progressResource, quizResource, questionResource

from django.core.management.base import BaseCommand

# view to display all study materials including pdfs ( as cards(materialcss) )
# coded by Kibuthi
class allPdfsView( View ):
    template_name = 'quiz/studymaterialsAll.html'
    args = {}

    def get( self, request,*args, **kwargs ):
        args = {}
        if request.user.is_authenticated:
            categorydata = Category.objects.all().order_by('level')
            args = {
                'categorydata' : categorydata
            }
            return render( request, self.template_name, args )
        else:
            args = {
                'site_message' : 'Please login to access the study materials.'
            }

            return redirect( 'users_login_link' % args )
# end : All-pdf-View

# the new index page for this app
class homeView( View ):
    template_name = 'quiz/quiz_home.html'
    args = {}

    def get( self, request, *args, **kwargs ):
        args = {}
        if request.user.is_authenticated:
            return render( request, self.template_name, args )
        else:
            args = {
                'site_message' : 'Please login to access the quizzes.'
            }

            return redirect( 'users_login_link' % args )

    def post( self, request, *args, **kwargs ):
        pass
# end : homeView

class QuizMarkerMixin(object):
    @method_decorator(login_required)
    @method_decorator(permission_required('quiz.view_sittings'))
    def dispatch(self, *args, **kwargs):
        return super(QuizMarkerMixin, self).dispatch(*args, **kwargs)


class SittingFilterTitleMixin(object):
    def get_queryset(self):
        queryset = super(SittingFilterTitleMixin, self).get_queryset()
        quiz_filter = self.request.GET.get('quiz_filter')
        if quiz_filter:
            queryset = queryset.filter(quiz__title__icontains=quiz_filter)

        return queryset


class QuizListView(ListView):
    model = Quiz

    def get_queryset(self):
        queryset = super(QuizListView, self).get_queryset().order_by('title')
        return queryset.filter(draft=False)


class QuizDetailView(DetailView):
    model = Quiz
    slug_field = 'url'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.draft and not request.user.has_perm('quiz.change_quiz'):
            raise PermissionDenied

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class CategoriesListView(ListView):
    model = Category


class ViewQuizListByCategory(ListView):
    model = Quiz
    template_name = 'view_quiz_category.html'

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(
            Category,
            category=self.kwargs['category_name']
        )

        return super(ViewQuizListByCategory, self).\
            dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ViewQuizListByCategory, self)\
            .get_context_data(**kwargs)

        context['category'] = self.category
        return context

    def get_queryset(self):
        queryset = super(ViewQuizListByCategory, self).get_queryset()
        return queryset.filter(category=self.category, draft=False)


class QuizUserProgressView(TemplateView):
    template_name = 'progress.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(QuizUserProgressView, self)\
            .dispatch(request, *args, **kwargs)

    def check_level( self, ** kwargs ):
        userprogresslevel = self.request.user.user.progressLevel
        print( '\n\tUser-progressLevel :: ' + str(userprogresslevel) )
        
        quizdata = Quiz.objects.filter( category__level=userprogresslevel )
        passmark_touse = 0
        
        for quizdataVal in quizdata:
            queried_passmark = quizdataVal.pass_mark
            passmark_touse += queried_passmark
            # #
        print( '\tpassmark_touse :: %d' % ( passmark_touse ) )
        #print( '\nDone showing quiz-data.\n' )

        userprog = Progress.objects.filter( user=self.request.user )
        for user in userprog:
            userExam = user.show_exams()
            #print( userExam )
            #print('\n\tjust shown userExam(has all quizzes done), going to userExam2...\n')
            userExam2 = user.show_exams_per_category() # show_exams_per_category
            #print( userExam2 )
            #print('\n\tJust shown userExam2(has quizzes specific to user\'s level), going to "if userExam2"...\n')
            if userExam2:
                totalPercentScore = 0
                status = 'proceed'
                for examDetail in userExam2:
                    quizcategorylevel = examDetail.quiz.category.level
                    quizcategorylevel = examDetail.quiz.category.level
                    totalPercentScore += examDetail.get_percent_correct
                    # #
                print( 'Current-Score: %d' % ( totalPercentScore ) )
            else:
                print( '\nThis user has not done any quiz in their current level' )
                status = 'leaveAlone'
                quizcategorylevel = userprogresslevel
                break
        
        if status == 'proceed' and userprogresslevel == quizcategorylevel and totalPercentScore >= passmark_touse:
            data = '\nTotal-pass-mark[ %d ] :: Total-percent-score[ %d ] in cat-level[ %s ]' % ( totalPassMark, totalPercentScore, str(quizcategorylevel) )
            print( data )
            result = '\tYou have met the level requirements, proceed to the next level'
            print( result )
            # code to update user-level to the next level
            nextLevel = userprogresslevel + 1
            validator = Sitting.objects.filter(user=self.request.user, complete=True).filter(quiz__category__level=nextLevel)
            if validator:
                print( 'No need to update user\'s level' )
            else:
                print( 'updating this user\'s level to [%d]' % (nextLevel) )
                userDetails = ProfileModel.objects.get( user=self.request.user )
                print( 'queried-user-level[ %d ]' % ( userDetails.progressLevel ) )
                userDetails.progressLevel = nextLevel
                userDetails.save()
                print( 'new-queried-user-level[ %d ]\n' % ( userDetails.progressLevel ) )
                check_level_output = userDetails.progressLevel
        else:
            result = 'No Analysis required, you maintain your current level'
            print(result)
            check_level_output = userprogresslevel

        confirmLevel = ProfileModel.objects.get( user=self.request.user )
        print( '\t\tat function end, this user\'s level is[ %d ]\n' % ( confirmLevel.progressLevel ) )
        return check_level_output

    def allIncorrect(self, **kwargs):
        print( '\tIncorrect-Qn-Gathering starting ...' )
        qndatalist = []

        userProgressData = Progress.objects.filter( user=self.request.user )
        if userProgressData:
            print('\tUser Has progress data !!')
            for progress in userProgressData:
                #print(progress)  sample-output>> Progress object (28)

                    # Getting exams data via 'show_exams()'
                examData = progress.show_exams().order_by('quiz__title')
                    # verify if examData has data
                if examData:
                    print('\tExams data FOUND !')
                    #print(examData)  sample-output>> <QuerySet [<Sitting: studone--1-digital-logic-circuits-num1>, <Sitting: studone--1-digital-logic-circuits-num2>]>
                        
                        # variables initialization
                    totalQuizzes = []
                    totalIncList = []
                    totalSubCatList = []
                    for quizData in examData:
                            # title data
                        qtitle = quizData.quiz.title
                        totalQuizzes.append(qtitle)
                        qcatlevel = quizData.quiz.category.level # type [int]
                        new_qtitle = '%s@%d' % (qtitle,qcatlevel)
                            # incorrect-questions data
                        qincorrect = quizData.incorrect_questions
                        qincorrect = qincorrect.split(',')
                        qincorrect = list( filter( None, qincorrect ) )
                        totalIncList.append(qincorrect)
                        # #
                    totalIncList = sum( totalIncList, [] )
                    #print(totalIncList)

                    for incorrect in totalIncList:
                        incorrect = int(incorrect)
                            # Get incorrect-Qns data
                        qndata = Question.objects.filter(id=incorrect)
                        for qn in qndata:
                            qn_subcat = qn.sub_category.sub_category
                            qn_content = qn.content
                            qn_explanation = qn.explanation
                                # put qn-data into a list then append into 'wrapper' list
                            qlist = [ incorrect, qn_subcat, qn_content, qn_explanation ]
                            qndatalist.append(qlist) # for 'progress.html'
                            
                            totalSubCatList.append( qn_subcat )
                            # #
                        # #
                    subcatCounter=collections.Counter( totalSubCatList )
                    #print( subcatCounter )
                    
                else:
                    print('\tNo Exams data found')
        else:
            print('\tUser has no progress data')

        print( '\tNumber of incorrect-qns : %d\n' % ( len(qndatalist) ) )
        analysisOutput = qndatalist
        return analysisOutput

    def get_context_data(self, **kwargs):
        context = super(QuizUserProgressView, self).get_context_data(**kwargs)
        progress, c = Progress.objects.get_or_create(user=self.request.user)
        context['cat_scores'] = progress.list_all_cat_scores
        exams = progress.show_exams()
        context['exams'] = exams
            
            # kib edit
        examTitleL = []
        examScoreL = []
        for exam in exams:
            examTitleL.append(exam.quiz.title)
            examScoreL.append(exam.get_percent_correct)
        #print(examTitleL)
        #print(examScoreL)
        context['examTitles'] = examTitleL
        context['examScores'] = examScoreL

        sittingData = Sitting.objects.filter(user=self.request.user)
        context['yourSitting'] = sittingData

        context[ 'checkLevelOutput' ] = self.check_level
        context['qn_analysis'] = self.allIncorrect
        if self.request.GET.get('analysis_message'):
            qGen_output = self.request.GET.get('analysis_message')
            print( qGen_output )
            context['analysis_message'] = qGen_output
            context['analysis_status'] = self.request.GET.get('status')
            context['qGen_url'] = self.request.GET.get('Qurl')
        else:
            context['analysis_message'] = 'No test-analysis performed yet, use the button provided to do so.'
            context['analysis_status'] = self.request.GET.get('status')
        #context['sampleChart'] = progChart()

        return context

def quizGeneration( request, *args, **kwargs ):
    print( '\n\tquizGen starting....' )
    print( request.user )
    new_q_name = ''
    progressData = Progress.objects.filter( user=request.user )
    if progressData is not None:
        for progress in progressData:
            sittingData = progress.show_exams().order_by('quiz__title')
            if sittingData is not None:
                totalQ = []
                totalI = []
                totalSubs = []
                for quizInfo in sittingData:
                    qtitle = quizInfo.quiz.title
                    totalQ.append( qtitle )
                    qinc = quizInfo.incorrect_questions
                    qinc = qinc.split(',')
                    qinc = list( filter( None, qinc ) )
                    totalI.append( qinc )
                    # #
                print( 'Number-of-quizzes-done : %d' % ( len(totalQ) ) )
                totalI = sum( totalI, [] )
                print( totalI )

                for inc in totalI:
                    inc = int( inc )
                    maswali = Question.objects.filter(id=inc)
                    for swali in maswali:
                        swali_subcat = swali.sub_category.sub_category
                        totalSubs.append( swali_subcat )
                        # #
                    # #
                SubsCounter = collections.Counter( totalSubs )

                if len(totalQ) >= 2:
                    print( '\tquizGen-processing commencing' )
                    notlinked = []
                    for sub in SubsCounter.keys():
                        print(sub)
                        qns = Question.objects.filter( sub_category__sub_category=sub, quiz__title__isnull=True )
                        qns = list( qns )
                        notlinked.append( qns )
                        # #
                    notlinked = sum( notlinked, [] )
                    print( notlinked )

                    stud = ProfileModel.objects.filter( user=request.user )
                    for studVal in stud:
                        got_level = studVal.progressLevel
                        # #
                    catdata = Category.objects.filter( level=got_level )
                    for cat in catdata:
                        got_cat = cat
                        # #
                    r = random.randint(201,999)
                    new_q_name = 'quiz-%d' % (r)
                    new_q_name_url = new_q_name + '-url'
                    print( 'Name[ %s ] : url[ %s ]' % ( new_q_name, new_q_name_url ) )
                    desc = "This is a newly generated quiz based on your failed questions."
                    quizCreate = Quiz.objects.create(title=new_q_name,url=new_q_name_url,category=got_cat,random_order=True,answers_at_end=True,exam_paper=True,pass_mark=55,description=desc)
                    for qn in notlinked:
                        tolink = Question.objects.get(content=qn)
                        qVal = tolink.quiz
                        print( 'Quiz-Value :: %s' % ( qVal ) )
                        tolink.quiz.add( quizCreate )
                        tolink.save()
                        # #
                    output = new_q_name
                else:
                    output = 'Too few exams attempted by user'
            else:
                output = 'No-Exams-Done'
            # #
    else:
        output = 'User-Has-No-Progress-Data'
    print( '\n\t...quizGen END' )

    if new_q_name:
        status = 'present'
        output = 'Use the provided link to take the generated quiz'
        return redirect( '/quiz/progress/?status=%s&analysis_message=%s&Qurl=%s' % ( status, output, new_q_name_url ) )
    else:
        status = 'absent'
        return redirect( '/quiz/progress/?status=%s&analysis_message=%s' % ( status, output ) )
    #return redirect( '/quiz/progress/' )

class QuizMarkingList(QuizMarkerMixin, SittingFilterTitleMixin, ListView):
    model = Sitting

    def get_queryset(self):
        queryset = super(QuizMarkingList, self).get_queryset()\
                                               .filter(complete=True)

        user_filter = self.request.GET.get('user_filter')
        if user_filter:
            queryset = queryset.filter(user__username__icontains=user_filter)

        return queryset


class QuizMarkingDetail(QuizMarkerMixin, DetailView):
    model = Sitting

    def post(self, request, *args, **kwargs):
        sitting = self.get_object()

        q_to_toggle = request.POST.get('qid', None)
        if q_to_toggle:
            q = Question.objects.get_subclass(id=int(q_to_toggle))
            if int(q_to_toggle) in sitting.get_incorrect_questions:
                sitting.remove_incorrect_question(q)
            else:
                sitting.add_incorrect_question(q)

        return self.get(request)

    def get_context_data(self, **kwargs):
        context = super(QuizMarkingDetail, self).get_context_data(**kwargs)
        context['questions'] =\
            context['sitting'].get_questions(with_answers=True)
        return context


class QuizTake(FormView):
    form_class = QuestionForm
    template_name = 'question.html'

    def dispatch(self, request, *args, **kwargs):
        self.quiz = get_object_or_404(Quiz, url=self.kwargs['quiz_name'])
        if self.quiz.draft and not request.user.has_perm('quiz.change_quiz'):
            raise PermissionDenied

        self.logged_in_user = self.request.user.is_authenticated

        if self.logged_in_user:
            self.sitting = Sitting.objects.user_sitting(request.user,
                                                        self.quiz)
        else:
            self.sitting = self.anon_load_sitting()

        if self.sitting is False:
            return render(request, 'single_complete.html')

        return super(QuizTake, self).dispatch(request, *args, **kwargs)

    def get_form(self): # , form_class
        if self.logged_in_user:
            self.question = self.sitting.get_first_question()
            self.progress = self.sitting.progress()
        else:
            self.question = self.anon_next_question()
            self.progress = self.anon_sitting_progress()

        if self.question.__class__ is Essay_Question:
            form_class = EssayForm

        return self.form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        kwargs = super(QuizTake, self).get_form_kwargs()

        return dict(kwargs, question=self.question)

    def form_valid(self, form):
        if self.logged_in_user:
            self.form_valid_user(form)
            if self.sitting.get_first_question() is False:
                return self.final_result_user()
        else:
            self.form_valid_anon(form)
            if not self.request.session[self.quiz.anon_q_list()]:
                return self.final_result_anon()

        self.request.POST = {}

        return super(QuizTake, self).get(self, self.request)

    def get_context_data(self, **kwargs):
        context = super(QuizTake, self).get_context_data(**kwargs)
        context['question'] = self.question
        context['quiz'] = self.quiz
        if hasattr(self, 'previous'):
            context['previous'] = self.previous
        if hasattr(self, 'progress'):
            context['progress'] = self.progress
        return context

    def form_valid_user(self, form):
        progress, c = Progress.objects.get_or_create(user=self.request.user)
        guess = form.cleaned_data['answers']
        is_correct = self.question.check_if_correct(guess)

        if is_correct is True:
            self.sitting.add_to_score(1)
            progress.update_score(self.question, 1, 1)
        else:
            self.sitting.add_incorrect_question(self.question)
            progress.update_score(self.question, 0, 1)

        if self.quiz.answers_at_end is not True:
            self.previous = {'previous_answer': guess,
                             'previous_outcome': is_correct,
                             'previous_question': self.question,
                             'answers': self.question.get_answers(),
                             'question_type': {self.question
                                               .__class__.__name__: True}}
        else:
            self.previous = {}

        self.sitting.add_user_answer(self.question, guess)
        self.sitting.remove_first_question()

    def final_result_user(self):
        results = {
            'quiz': self.quiz,
            'score': self.sitting.get_current_score,
            'max_score': self.sitting.get_max_score,
            'percent': self.sitting.get_percent_correct,
            'sitting': self.sitting,
            'previous': self.previous,
        }

        self.sitting.mark_quiz_complete()

        if self.quiz.answers_at_end:
            results['questions'] =\
                self.sitting.get_questions(with_answers=True)
            results['incorrect_questions'] =\
                self.sitting.get_incorrect_questions

        if self.quiz.exam_paper is False:
            self.sitting.delete()

        # export results of user to csv file :: sittingResource : request.user.username, request.user
        sitting_resource = sittingResource()
        userSittingData = Sitting.objects.filter(user=self.request.user).order_by('quiz')
        dataset = sitting_resource.export( userSittingData )
        #print(dataset.csv)
        path = 'media/csvFiles/sittingResourceFile-'+str(self.request.user.id)+'-'+str(self.request.user)+'.csv'
        print( path )
        datasetFile = open( path, 'w+')
        datasetFile.write(dataset.csv)
        datasetFile.close()
        return render(self.request, 'result.html', results)

    def anon_load_sitting(self):
        if self.quiz.single_attempt is True:
            return False

        if self.quiz.anon_q_list() in self.request.session:
            return self.request.session[self.quiz.anon_q_list()]
        else:
            return self.new_anon_quiz_session()

    def new_anon_quiz_session(self):
        """
        Sets the session variables when starting a quiz for the first time
        as a non signed-in user
        """
        self.request.session.set_expiry(259200)  # expires after 3 days
        questions = self.quiz.get_questions()
        question_list = [question.id for question in questions]

        if self.quiz.random_order is True:
            random.shuffle(question_list)

        if self.quiz.max_questions and (self.quiz.max_questions
                                        < len(question_list)):
            question_list = question_list[:self.quiz.max_questions]

        # session score for anon users
        self.request.session[self.quiz.anon_score_id()] = 0

        # session list of questions
        self.request.session[self.quiz.anon_q_list()] = question_list

        # session list of question order and incorrect questions
        self.request.session[self.quiz.anon_q_data()] = dict(
            incorrect_questions=[],
            order=question_list,
        )

        return self.request.session[self.quiz.anon_q_list()]

    def anon_next_question(self):
        next_question_id = self.request.session[self.quiz.anon_q_list()][0]
        return Question.objects.get_subclass(id=next_question_id)

    def anon_sitting_progress(self):
        total = len(self.request.session[self.quiz.anon_q_data()]['order'])
        answered = total - len(self.request.session[self.quiz.anon_q_list()])
        return (answered, total)

    def form_valid_anon(self, form):
        guess = form.cleaned_data['answers']
        is_correct = self.question.check_if_correct(guess)

        if is_correct:
            self.request.session[self.quiz.anon_score_id()] += 1
            anon_session_score(self.request.session, 1, 1)
        else:
            anon_session_score(self.request.session, 0, 1)
            self.request\
                .session[self.quiz.anon_q_data()]['incorrect_questions']\
                .append(self.question.id)

        self.previous = {}
        if self.quiz.answers_at_end is not True:
            self.previous = {'previous_answer': guess,
                             'previous_outcome': is_correct,
                             'previous_question': self.question,
                             'answers': self.question.get_answers(),
                             'question_type': {self.question
                                               .__class__.__name__: True}}

        self.request.session[self.quiz.anon_q_list()] =\
            self.request.session[self.quiz.anon_q_list()][1:]

    def final_result_anon(self):
        score = self.request.session[self.quiz.anon_score_id()]
        q_order = self.request.session[self.quiz.anon_q_data()]['order']
        max_score = len(q_order)
        percent = int(round((float(score) / max_score) * 100))
        session, session_possible = anon_session_score(self.request.session)
        if score is 0:
            score = "0"

        results = {
            'score': score,
            'max_score': max_score,
            'percent': percent,
            'session': session,
            'possible': session_possible
        }

        del self.request.session[self.quiz.anon_q_list()]

        if self.quiz.answers_at_end:
            results['questions'] = sorted(
                self.quiz.question_set.filter(id__in=q_order)
                                      .select_subclasses(),
                key=lambda q: q_order.index(q.id))

            results['incorrect_questions'] = (
                self.request
                    .session[self.quiz.anon_q_data()]['incorrect_questions'])

        else:
            results['previous'] = self.previous

        del self.request.session[self.quiz.anon_q_data()]

        return render(self.request, 'result.html', results)


def anon_session_score(session, to_add=0, possible=0):
    """
    Returns the session score for non-signed in users.
    If number passed in then add this to the running total and
    return session score.

    examples:
        anon_session_score(1, 1) will add 1 out of a possible 1
        anon_session_score(0, 2) will add 0 out of a possible 2
        x, y = anon_session_score() will return the session score
                                    without modification

    Left this as an individual function for unit testing
    """
    if "session_score" not in session:
        session["session_score"], session["session_score_possible"] = 0, 0

    if possible > 0:
        session["session_score"] += to_add
        session["session_score_possible"] += possible

    return session["session_score"], session["session_score_possible"]
