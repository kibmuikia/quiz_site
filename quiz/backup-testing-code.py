		sittingData = Sitting.objects.filter(user=self.request.user)
        totalPassMark = 0
        totalUserScore = 0
        text = ''
        for sitValue in sittingData:
            userProgressData, c = Progress.objects.get_or_create( user=sitValue.user )
            userExamsData = userProgressData.show_exams()
            for userExams in userExamsData:
                totalUserScore += int(userExams.get_percent_correct) # totalUserScore +
                print( 'userScore-'+str(totalUserScore)+'\n' )
                #pass
        text += 'quiz[%s], quizPassMark[%s], catLevel[%s], comp[%s], user-score[%s], user-Level[%s].\n**\n' % ( str(sitValue.quiz),str(sitValue.quiz.pass_mark),str(sitValue.quiz.category.level),str(sitValue.complete),str(userExams.get_percent_correct),self.request.user.user.progressLevel )
        totalPassMark += int(sitValue.quiz.pass_mark) #totalPassMark + 
        print( 'passMark-'+str(totalPassMark)+'\n' )
        
        marksData = 'totalUserScore[ %d ] :: totalPassMark[ %d ]' % ( totalUserScore, totalPassMark )
        print( marksData )
        return text + marksData + '\n**\n'

        				for examDetail in userExam:
                    print( examDetail )
                    quizcategorylevel = examDetail.quiz.category.level
                    #if quizcategorylevel == userprogresslevel:
                    print( 'Quiz-title >> ' + examDetail.quiz.title )
                    print( 'Quiz-category >> ' + examDetail.quiz.category.category )
                    quizcategorylevel = examDetail.quiz.category.level
                    print( 'Quiz-category-level >> ' + str( quizcategorylevel ) )
                    print( 'Quiz-pass_mark >> ' + str(examDetail.quiz.pass_mark) )
                    #totalPassMark += examDetail.quiz.pass_mark
                    print( 'User-current-score(no. of correctly answered qns) >> ' + str(examDetail.current_score) )
                    print( 'Quiz-max-score(no. of qns) >> ' + str(examDetail.get_max_score) )
                    print( 'User-percent-correct >> ' + str(examDetail.get_percent_correct) )
                    #totalPercentScore += examDetail.get_percent_correct
                    print('\n')


    <ul>
        <li>
            {{quiztitle}}
            <ol style="list-style-type: circle;" >
                {% for qnid, qndata in qndict.items %}
                <li>
                    {{ qnid }}
                    <ol style="list-style-type: square;">
                        <li> {{ qndata.0 }} </li>
                        <li> {{ qndata.1 }} </li>
                        <li> {{ qndata.2 }} </li>
                        <li> {{ qndata.3 }} </li>
                    </ol>
                </li>
                {% endfor %}
            </ol>
        </li>
    </ul>

    <div class="card small">
        <div class="card-content">
            <span class="card-title"> {{ quiztitle }} </span>
            <h6> {{ qndata.0 }} </h6>
        </div>
        <div class="card-tabs">
            <ul class="tabs tabs-fixed-width">
                <li class="tab">
                    <a href="#subCat-{{qnid}}">Sub Category</a>
                </li>
                <li class="tab">
                    <a href="#reason-{{qnid}}" class="active">Explanation</a>
                </li>
            </ul>
        </div>
        <div class="card-content grey lighten-4">
            <div id="subCat-{{qnid}}"> {{ qndata.2 }} </div>
            <div id="reason-{{qnid}}"> {{ qndata.3 }} </div>
        </div>
    </div>