import random

from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect, HttpResponse, HttpResponseRedirect, reverse
from django.utils.decorators import method_decorator

# FileResponse - to display files
from django.http import FileResponse, Http404

from django.views.generic import DetailView, ListView, TemplateView, FormView, View

from .forms import QuestionForm, EssayForm
from .models import Quiz, Category, Progress, Sitting, Question
from essay.models import Essay_Question
from users.models import ProfileModel
from jchart import Chart
from jchart.config import DataSet

from .charts import lineChart, progressChart

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

# trying charts
class progChart( Chart ):
    chart_type = 'line'
    responsive = True

    def get_datasets( self, **kwargs ):
        print('\tIn funct-get_datasets')

        # test run
        data = [{
            'label' : "Testing progChart",
            'data' : [10,234,187,44,88,111,94],
            #'x':['one','two','three','four','five','six','seven']
        }]

        # output, for instance, Progress-model data
        progModelData, u = Progress.objects.get_or_create(user=26)
        progExam = progModelData.show_exams()
        titleList = []
        scoreList = []
        for prog in progExam:
            titleList.append(prog.quiz.title)
            scoreList.append(prog.get_percent_correct)
        print(titleList)
        print(scoreList)
        #data = [{'x': sitting.quiz.title, 'y': int(sitting.current_score)} for sitting in sitModelData]
        data = [{
            'label':titleList,
            #'label':'User Progress Chart',
            'data': scoreList
        }]
        #return [DataSet(data=data)]        
        return data
# END: chart-trial

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
    #template_name = 'progress.html'
    template_name = 'progress.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(QuizUserProgressView, self)\
            .dispatch(request, *args, **kwargs)

    def check_level( self, ** kwargs ):
        userprogresslevel = self.request.user.user.progressLevel
        print( '\n\tUser-progressLevel :: ' + str(userprogresslevel) )
        
        quizdata = Quiz.objects.filter( category__level=userprogresslevel )
        #print( '\nShowing quiz-data filtered with current user\'s level :: \n ' )
        #print( quizdata )
        passmark_touse = 0
        for quizdataVal in quizdata:
            queried_passmark = quizdataVal.pass_mark
            #print( 'queried_passmark :: %d' % ( queried_passmark ) )
            passmark_touse += queried_passmark
        print( '\tpassmark_touse :: %d' % ( passmark_touse ) )
        #print( '\nDone showing quiz-data.\n' )

        userprog = Progress.objects.filter( user=self.request.user )
        for user in userprog:
            print( user )
                # print( user.user.progressLevel ) << Error: 'User' object has no attribute 'progressLevel'
            #print('\n')
            userExam = user.show_exams()
            print( userExam )
            print('\n\tjust shown userExam(has all quizzes done), going to userExam2...\n')
            userExam2 = user.show_exams_per_category() # show_exams_per_category
            print( userExam2 )
            print('\n\tJust shown userExam2(has quizzes specific to user\'s level), going to "if userExam2"...\n')
            if userExam2:
                totalPassMark = 0
                totalPercentScore = 0
                status = 'proceed'
                for examDetail in userExam2:
                    print( examDetail )
                    quizcategorylevel = examDetail.quiz.category.level
                    print( 'Quiz-title >> ' + examDetail.quiz.title )
                    #print( 'Quiz-category >> ' + examDetail.quiz.category.category )
                    quizcategorylevel = examDetail.quiz.category.level
                    print( 'Quiz-category-level >> ' + str( quizcategorylevel ) )
                    #print( 'Quiz-pass_mark >> ' + str(examDetail.quiz.pass_mark) )
                    totalPassMark += examDetail.quiz.pass_mark
                    print( 'User-current-score(no. of correctly answered qns) >> ' + str(examDetail.current_score) )
                    #print( 'Quiz-max-score(no. of qns) >> ' + str(examDetail.get_max_score) )
                    print( 'User-percent-correct >> ' + str(examDetail.get_percent_correct) )
                    totalPercentScore += examDetail.get_percent_correct
                    print('\n')
            else:
                print( '\nThis user has not done any quiz in their current level' )
                status = 'leaveAlone'
                quizcategorylevel = userprogresslevel
                break
        
        if status == 'proceed' and userprogresslevel == quizcategorylevel and totalPercentScore >= passmark_touse:#totalPassMark:
            data = '\n\tTotal-pass-mark[ %d ] :: Total-percent-score[ %d ] in cat-level[ %s ]' % ( totalPassMark, totalPercentScore, str(quizcategorylevel) )
            print( data )
            result = '\n\tYou have met the level requirements, proceed to the next level'
            print( result )
            # code to update user-level to the next level
            nextLevel = userprogresslevel + 1
            validator = Sitting.objects.filter(user=self.request.user, complete=True).filter(quiz__category__level=nextLevel)
            print( validator )
            if validator:
                print( '\nNo need to update user\'s level' )
            else:
                print( '\nAdmin, please update this user\'s level to [%d]' % (nextLevel) )
                userDetails = ProfileModel.objects.get( user=self.request.user )
                print( 'queried-user-level[ %d ]' % ( userDetails.progressLevel ) )
                userDetails.progressLevel = nextLevel
                userDetails.save()
                print( 'new-queried-user-level[ %d ]' % ( userDetails.progressLevel ) )
                check_level_output = userDetails.progressLevel
        else:
                #result = '\n\tYour total score[%d] in level[%d] is below the level requirements[%d]' % ( totalPercentScore,quizcategorylevel,totalPassMark )
            result = '\nNo Analysis required, you maintain your current level'
            print(result)
            check_level_output = userprogresslevel

        confirmLevel = ProfileModel.objects.get( user=self.request.user )
        print( '\n\t\tat function end, this user\'s level is[ %d ]' % ( confirmLevel.progressLevel ) )
        print('\n')
        return check_level_output

    def incorrectAnalysis(self, **kwargs):
        print( 'Getting user progress data' )
        userProgressData = Progress.objects.filter( user=self.request.user )
        print( userProgressData )
        allIncorrectDict = {}

        for progvalue in userProgressData:
            print( progvalue )
            examinfo = progvalue.show_exams().order_by( 'quiz__title' )
            if examinfo:
                print( examinfo )
                for detail in examinfo:
                    print( '\n' )
                    qtitle = detail.quiz.title
                    #print( qtitle )
                    qcat_level = detail.quiz.category.level
                    qcat_level = str( qcat_level )
                    #print( qcat_level )
                    new_qtitle = qtitle + '@' + qcat_level
                    print( new_qtitle )
                    # print( (new_qtitle.split('@'))[1] ) :: to get back category level
                    qstate = detail.complete
                    #print( 'Has been complete? > %s' % (str(qstate)) )
                    qscore = detail.current_score
                    print( 'correct-qns : %d' % (qscore) )

                    qincorrect = detail.incorrect_questions
                    qincorrect = qincorrect.split(',')
                    listOfIncorrect = list( filter(None, qincorrect) )
                    print( listOfIncorrect )
                    allIncorrectDict[ new_qtitle ] = listOfIncorrect

                    qnData_dict = {}
                    for each_incorrect in listOfIncorrect:
                        qnData = Question.objects.get( id=int(each_incorrect) )
                        qn_id = int(each_incorrect)
                        qn_content = qnData.content
                        qn_cat_level = qnData.category.level
                        qn_subcat = qnData.sub_category
                        qn_reason = qnData.explanation
                        qnData_list = [ qn_id, qn_cat_level, qn_subcat, qn_reason ]
                        #print( qnData_list )
                        qnData_dict[ qn_id ] = [ qn_content, qn_cat_level, qn_subcat, qn_reason ]
                        #print( qnData_dict[qn_id] )
                    
                    print( qnData_dict )
                    allIncorrectDict[ new_qtitle ] = qnData_dict

            else:
                print('No exam has been done, yet.')

        print('\n')
        #if allIncorrectDict != '':
        print( allIncorrectDict )

        analysisOutput = allIncorrectDict

        return analysisOutput

    def get_context_data(self, **kwargs):
        context = super(QuizUserProgressView, self).get_context_data(**kwargs)
        progress, c = Progress.objects.get_or_create(user=self.request.user)
        context['cat_scores'] = progress.list_all_cat_scores
        exams = progress.show_exams()
        context['exams'] = exams
        examTitleL = []
        examScoreL = []
        for exam in exams:
            examTitleL.append(exam.quiz.title)
            examScoreL.append(exam.get_percent_correct)
        print(examTitleL)
        print(examScoreL)
        # kib edit
        sittingData = Sitting.objects.filter(user=self.request.user)
        context['yourSitting'] = sittingData
        context[ 'checkLevelOutput' ] = self.check_level
        context['qn_analysis'] = self.incorrectAnalysis
        #context['sampleChart'] = progChart()
        context['examTitles'] = examTitleL
        context['examScores'] = examScoreL

        return context


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
