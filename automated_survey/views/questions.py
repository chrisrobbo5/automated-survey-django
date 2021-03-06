from django.core.urlresolvers import reverse
from twilio import twiml
from django.http import HttpResponse

from automated_survey.models import Question
from automated_survey.views.common import parameters_for_survey_url
from django.views.decorators.http import require_GET


@require_GET
def show_question(request, survey_id, question_id):
    question = Question.objects.get(id=question_id)

    url_parameters = parameters_for_survey_url(question.survey.id,
                                               question.id)

    question_store_url = reverse('record_response', kwargs=url_parameters)

    voice_response = twiml.Response()
    voice_response.say(question.body)
    voice_response.say(instructions[question.kind])
    voice_response = _attach_command_to_response(
        voice_response, question.kind, question_store_url
    )

    return HttpResponse(voice_response, content_type='application/xml')


def _attach_command_to_response(response, kind, action):
    if kind == Question.VOICE:
        response.record(action=action + '?Kind=voice', method='POST')
    elif kind == Question.NUMERIC:
        response.gather(action=action + '?Kind=numeric', method='POST')
    elif kind == Question.YES_NO:
        response.gather(action=action + '?Kind=yes-no', method='POST')
    else:
        raise NoSuchVerbException('%s is not a supported question type' % kind)

    return response

instructions = {
    'voice': 'Please record your answer after the beep and then hit the pound sign',
    'yes-no': 'Please press the one key for yes and the zero key for no and then hit the pound sign',
    'numeric': 'Please press a number between 1 and 10 and then hit the pound sign'
}


class NoSuchVerbException(Exception):
    pass
