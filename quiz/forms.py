from django import forms
from django.forms.widgets import RadioSelect, Textarea


class QuestionForm(forms.Form):
    def __init__(self, question, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)

        if question.get_answers_list() == False:
            self.fields["answers"] = forms.CharField( widget=Textarea( attrs={'style': 'width:100%'} ) )

        else:
            choice_list = [x for x in question.get_answers_list()]
            #choice_list = [ for x in question ]

            self.fields["answers"] = forms.ChoiceField(choices=choice_list,
                                                       widget=RadioSelect)


class EssayForm(forms.Form):
    def __init__(self, question, *args, **kwargs):

        super(EssayForm, self).__init__(*args, **kwargs)

        self.fields["answers"] = forms.CharField( widget=Textarea( attrs={'style': 'width:100%'} ) )
