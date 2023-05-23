from django.db import models

from django.utils.crypto import get_random_string

class Respondent(models.Model):
    ## Independent fields
    unique_string = models.CharField(max_length=7, unique=True)
    url = models.URLField(unique=True, blank=True, null=True)
    name = models.CharField(max_length=100)
    invitation_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(to='users.CustomUser', on_delete=models.CASCADE, related_name='survey_id', null=True, blank=True)
    current_survey = models.ForeignKey(to='surveys.Survey', on_delete=models.CASCADE, related_name='survey_respondents', null=True, blank=True)
    was_invited = models.BooleanField(default=True, null=True, blank=True)

    ## Computed fields
    ## Cache fields
    ## Instance control fields
    
    def __str__(self):
        if self.was_invited:
            return f'Survey Respondent [{self.name}], invitation date: [{self.invitation_date}]'
        else:
            return f'[UNINVITED] Survey Respondent [{self.name}], registration date: [{self.invitation_date}]'

    def save(self, *args, **kwargs):
        self.update_computed_and_cache_fields()
        super().save()
    class meta:
        verbose_name = 'Survey Respondent'
        verbose_name_plural = 'Survey Respondents'

    def update_computed_and_cache_fields(self):
        if not self.unique_string:
            self.unique_string = get_random_string(length=7)

class Survey(models.Model):
    ## Independent fields
    name = models.CharField(max_length=100)
    description = models.TextField()
    active = models.BooleanField(default=True)
    
    ## Computed fields
    ## Cache fields
    ## Instance control fields
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Survey {self.name}'
    
    class meta:
        verbose_name = 'Survey'
        verbose_name_plural = 'Surveys'

class Question(models.Model):
    ## Independent fields
    survey = models.ForeignKey(to='surveys.Survey', on_delete=models.CASCADE, related_name='questions')
    question_number = models.IntegerField()
    question_text = models.TextField()
    question_type = models.CharField(max_length=10, choices=[('input', 'Input'), ('select', 'Select')])
    is_required = models.BooleanField(default=True)
    

    ## Computed fields
    ## Cache fields
    ## Instance control fields
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Survey {self.survey.name}, Q{self.question_number}. {self.question_text[:60]}'
    
    class meta:
        ordering = ['question_number']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        
    
class QuestionOption(models.Model):
    ## Independent fields
    question = models.ForeignKey(to='surveys.Question', on_delete=models.CASCADE, related_name='options')
    option_number = models.IntegerField()
    option_text = models.CharField(max_length=300, null=True, blank=True)
    option_value = models.CharField(max_length=100, null=True, blank=True)

    ## Computed fields

    ## Cache fields
    survey = models.ForeignKey(to='surveys.Survey', on_delete=models.CASCADE, null=True ,blank=True)

    ## Instance control fields
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Survey {self.survey.name}, Q{self.question.question_number}. {self.option_text[:80]}'
    
    class meta:
        verbose_name = 'Question Option'
        verbose_name_plural = 'Question Options'
    
    def save(self, *args, **kwargs):
        self.update_computed_and_cache_fields()
        super().save()
    
    def update_computed_and_cache_fields(self):
        self.survey = self.question.survey

class Answer(models.Model):
    ## Independent fields
    respondent = models.ForeignKey(to='surveys.Respondent', on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(to='surveys.Question', on_delete=models.CASCADE, related_name='answers')
    answer_type = models.CharField(max_length=10, choices=[('input', 'Input'), ('select', 'Select')])
    answer_text = models.TextField(null=True, blank=True)
    answer_value = models.CharField(max_length=100, null=True, blank=True)
    answer_option_number = models.IntegerField(null=True, blank=True)

    ## Computed fields

    ## Cache fields
    survey = models.ForeignKey(to='surveys.Survey', on_delete=models.CASCADE, null=True ,blank=True)

    ## Instance control fields
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Survey [{self.survey.name}], Respondent [{self.respondent.name}] Answer to Q{self.question.question_number}.'

    class meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
    
    def save(self, *args, **kwargs):
        self.update_computed_and_cache_fields()
        super().save()
    
    def update_computed_and_cache_fields(self):
        self.survey = self.question.survey

