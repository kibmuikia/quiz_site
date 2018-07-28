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