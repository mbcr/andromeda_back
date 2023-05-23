from rest_framework import serializers
from .models import Survey, Question, Answer, Respondent

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = [
            'id',
            'respondent',
            'question',
            'answer_type',
            'answer_text',
            'answer_value',
            'answer_option_number',
            'survey',
            'date_created',
            'last_modified'
        ]


    