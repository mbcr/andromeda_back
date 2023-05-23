from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from .models import Respondent, Survey, Question, QuestionOption, Answer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .serializers import AnswerSerializer

from pprint import pprint



#Copilot, use api_view (@api_view), to setup a GET api endpoint, but allow any user to access it
@api_view(['GET'])
@permission_classes([AllowAny])
def check_respondent(request):
    # print('surveys>check_respondent>request.GET: ', request.GET)
    unique_string = request.GET.get('survey_id')
    respondent_exists = False
    current_survey_pk = None
    try:
        respondent = Respondent.objects.get(unique_string=unique_string)
    except Respondent.DoesNotExist:
        respondent = None

    if not respondent:
        # print('surveys>check_respondent>Respondent does not exist')
        payload = {
            'respondent_exists': False,
            'message': 'Respondent does not exist'
        }
        return JsonResponse(payload, status=200)

    respondent_exists = True
    current_survey = respondent.current_survey
    if not current_survey:
        payload = {
            'respondent_exists': respondent_exists,
            'respondent_pk': respondent.pk,
            'respondent_name': respondent.name,
            'current_survey_active': False,
            'message': 'Respondent has no active survey'
        }
        return JsonResponse(payload, status=200)

    current_survey_pk = current_survey.pk
    payload = {
        'respondent_exists': respondent_exists,
        'respondent_pk': respondent.pk,
        'respondent_name': respondent.name,
        'current_survey_active': True,
        'current_survey_pk': current_survey_pk,
        'current_survey_name': current_survey.name,
    }
    return JsonResponse(payload,status=200)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_survey_questions(request):
    survey_pk = request.GET.get('survey_pk')
    if not survey_pk:
        return HttpResponseBadRequest('survey_pk parameter is required')

    if survey_pk == '0':
        survey = Survey.objects.first()
    else:
        try:
            survey = Survey.objects.get(pk=survey_pk)
        except Survey.DoesNotExist:
            print(f'surveys>get_surveyquestions> Survey with pk {survey_pk} does not exist')
            return HttpResponseBadRequest(f'Survey with pk {survey_pk} does not exist')

    questions = survey.questions.order_by('question_number')
    payload = {
        'survey_pk': survey.pk,
        'survey_name': survey.name,
        'survey_description': survey.description,
        'questions': []
    }
    question_list = []

    for question in questions:
        question_dict = {
            'question_pk': question.pk,
            'number': question.question_number,
            'type': question.question_type,
            'prompt': question.question_text,
            'is_required': question.is_required,
        }

        if question.question_type == 'select':
            options = question.options.order_by('option_number')
            option_list = []
            for option in options:
                option_dict = {
                    'option_number': option.option_number,
                    'option_text': option.option_text,
                }
                # option_dict = option.option_text
                option_list.append(option_dict)
            question_dict['options'] = option_list

        question_list.append(question_dict)
    payload['questions'] = question_list

    return JsonResponse(payload, safe=False, status=200)

@api_view(['POST'])
@permission_classes([AllowAny])
def save_answers(request):
    def identify_respondent_for_uninvited_respondent():
        new_respondent_name = request.data['questions'].pop(0)['answer']
        survey_respondent = Respondent.objects.create(name=new_respondent_name,was_invited=False,url=None)
        return survey_respondent
    def identify_respondent_for_uninvited_user():
        new_respondent_name = request.user.fullName()
        survey_respondent = Respondent.objects.get_or_create(
            name=new_respondent_name,
            user=request.user,
            was_invited=False,
            url=None
            )[0]
        return survey_respondent
    def identify_respondent_for_invited_respondent():
        survey_respondent = Respondent.objects.get(pk=survey_respondent_pk)
        return survey_respondent
    def create_answers_from(question_list:list) -> list:
        # print('creating answers from question_list:')
        # pprint(question_list)
        answer_list = []
        for question in question_list:
            answer = question.get('answer', {})
            question_pk = question.get('question_pk', None)
            question = Question.objects.get(pk=question_pk)
            question_type = question.question_type
            if question_type == 'select':
                question_options = question.options.all()
                answer_text = answer['option_text']
                selected_option = question_options.get(option_text=answer_text)
                answer_option_number = selected_option.option_number
                answer_value = selected_option.option_value
            if question_type == 'input':
                answer_value = None
                answer_option_number = None
                answer_text = answer

            answer = Answer.objects.create(
                respondent=survey_respondent,
                question=question,
                answer_type=question_type,
                answer_text=answer_text,
                answer_option_number=answer_option_number,
                answer_value=answer_value,
            )
            answer_list.append(answer)
        return answer_list

    # pprint(request.data)
    survey_respondent_pk = request.data['survey_respondent_pk']
    if not survey_respondent_pk:
        return HttpResponseBadRequest('survey_respondent_pk not found in request')

    try:
        if survey_respondent_pk == 'uninvited_respondent':
            survey_respondent = identify_respondent_for_uninvited_respondent()
            
        elif survey_respondent_pk == 'uninvited_user':
                survey_respondent = identify_respondent_for_uninvited_user()
        else:
            survey_respondent = identify_respondent_for_invited_respondent()
    except Respondent.DoesNotExist:
        return HttpResponseBadRequest('Respondent not found')

    survey_pk = request.data['survey_pk']
    if not survey_pk:
        return HttpResponseBadRequest('survey_pk not found in request')
    try:
        survey = Survey.objects.get(pk=survey_pk)
    except Survey.DoesNotExist:
        return HttpResponseBadRequest('Survey not found')

    question_list = request.data['questions']
    answers_list = create_answers_from(question_list)
    
    survey_respondent.current_survey = None
    answers_created = {
        'saved': True,
        'answers': [AnswerSerializer(answer, many=False).data for answer in answers_list]
    }
    return JsonResponse(answers_created, status=201)