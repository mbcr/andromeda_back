from apps.surveys.models import Survey, Question, QuestionOption

from pprint import pprint

questions = [
    {
    'question_number': 1,
    'question_type': 'input',
    'is_required': True,
    'question_text': 'Confirme o nome da sua empresa:'
    },
    {
    'question_number': 2,
    'question_type': 'select',
    'question_text': 'Qual é o tamanho da sua empresa?',
    'is_required': True,
    'options': [
        {
        'option_number': 1,
        'option_text': '1-100 funcionários'
        },
        {
        'option_number': 2,
        'option_text': '101-500 funcionários'
        },
        {
        'option_number': 3,
        'option_text': '501-1000 funcionários'
        },
        {
        'option_number': 4,
        'option_text': '1001-5000 funcionários'
        },
        {
        'option_number': 5,
        'option_text': '5001-10000 funcionários'
        },
        {
        'option_number': 6,
        'option_text': 'Mais de 10000 funcionários'
        }
    ]
    },
    {
    'question_number': 3,
    'question_type': 'select',
    'question_text': 'Qual opção melhor descreve sua função dentro de sua organização?',
    'is_required': True,
    'options': [
        {
        'option_number': 1,
        'option_text': 'Diretoria/Vice-Presidência (Dir. Gente, Dir. Recursos Humanos, Dir. Operações, etc.)'
        },
        {
        'option_number': 2,
        'option_text': 'Gerência (Gerente de Recursos Humanos, Gerente de Operações, Gerente de Saúde e Segurança, etc.)'
        },
        {
        'option_number': 3,
        'option_text': 'Supervisão (Supervisão de Recursos Humanos, Supervisão de Saúde ocupacional, etc.)'
        },
        {
        'option_number': 4,
        'option_text': 'Colaborador Individual (Analista de Recursos Humanos, Enfermagem do Trabalho, Engenharia do Trabalho, etc.)'
        }
        ]
    },
    {
    'question_number': 4,
    'question_type': 'select',
    'question_text': 'Qual é a categoria de risco que se aplica às atividades de sua organização?',
    'is_required': True,
    'options': [
        {
        'option_number': 1,
        'option_text': 'Categoria de risco 1'
        },
        {
        'option_number': 2,
        'option_text': 'Categoria de risco 2'
        },
        {
        'option_number': 3,
        'option_text': 'Categoria de risco 3'
        },
        {
        'option_number': 4,
        'option_text': 'Categoria de risco 4'
        },
        {
        'option_number': 5,
        'option_text': 'Não tenho certeza'
        }
    ]
    },
    {
    'question_number': 5,
    'question_type': 'select',
    'question_text': 'A gestão de saúde ocupacional é feito por uma equipe independente, ou em conjunto com a equipe de segurança ocupacional?',
    'is_required': True,
    'options': [
        {
        'option_number': 1,
        'option_text': 'A equipe de saúde ocupacional é completamente independente, possuindo uma gerência própria que reporta à diretoria'
        },
        {
        'option_number': 2,
        'option_text': 'A equipe de saúde ocupacional é independente, mas possui uma gerência em conjunto com a equipe de segurança ocupacional'
        },
        {
        'option_number': 3,
        'option_text': 'A equipe de saúde ocupacional é completamente integrada à equipe de segurança ocupacional'
        },
        {
        'option_number': 4,
        'option_text': 'A gestão de saúde ocupacional é terceirizada e reporta para a diretoria'
        },
        {
        'option_number': 5,
        'option_text': 'A gestão de saúde ocupacional é terceirizada e reporta para a gerência'
        },
        {
        'option_number': 6,
        'option_text': 'Não tenho certeza'
        }
    ]
    },
    {
    'question_number': 6,
    'question_type': 'select',
    'question_text': 'Qual o modelo de gestão de saúde ocupacional adotado por sua organização?',
    'is_required': True,
    'options': [
        {
        'option_number': 1,
        'option_text': 'A gestão e execução são feitas de forma completamente interna, com equipe própria, incluindo todos os exames necessários'
        },
        {
        'option_number': 2,
        'option_text': 'A gestão e execução são feitas de forma interna, com equipe própria, terceirizando apenas exames complementares'
        },
        {
        'option_number': 3,
        'option_text': 'A gestão e execução são feitas de forma interna, com equipe própria, terceirizando todos os exames'
        },
        {
        'option_number': 4,
        'option_text': 'A gestão é feita de forma interna, mas contamos com equipe parcialmente terceirizada'
        },
        {
        'option_number': 5,
        'option_text': 'A gestão é feita de forma interna, mas a execução é completamente terceirizada'
        },
        {
        'option_number': 6,
        'option_text': 'Tanto a gestão quanto a execução são terceirizadas, com os fornecedores reportando para a diretoria ou gestão'
        },
        {
        'option_number': 7,
        'option_text': 'Não tenho certeza'
        }
    ]
    },
    {
    'question_number': 7,
    'question_type': 'select',
    'question_text': 'As atividades de planejamento dos programas de saúde ocupacional incluem a preparação documentos como PCMSO, PPP, PPRA, e laudos, além de garantir que a organização atende à regulamentação vigente. Qual o modelo de planejamento adotado por sua organização?',
    'is_required': True,
    'options': [
        {
        'option_number': 1,
        'option_text': 'O planejamento é feito de forma completamente interna, com equipe própria de engenheiros, médicos e enfermeiros do trabalho.'
        },
        {
        'option_number': 2,
        'option_text': 'O planejamento é feito de forma parcialmente terceirizada, com consultoria externa elaborando alguns documentos para a equipe interna responsável.'
        },
        {
        'option_number': 3,
        'option_text': 'O planejamento é feito de forma completamente terceirizada, com consultoria externa para elaboração de todos os documentos.'
        },
        {
        'option_number': 4,
        'option_text': 'Não tenho certeza'
        }
    ]
    },
    {
    'question_number': 8,
    'question_type': 'select',
    'question_text': 'As atividades de gestão de saúde ocupacional incluem a construção de orçamentos, padronização de exames entre unidades de negócio semelhantes, gestão de contratos com fornecedores do serviço final (exames complementares, por exemplo), monitoramento e acompanhamento de indicadores. Qual o modelo de gestão adotado por sua organização?',
    'is_required': True,
    'options': [
        {
        'option_number': 1,
        'option_text': 'A gestão é feita de forma completamente interna, com equipe própria.'
        },
        {
        'option_number': 2,
        'option_text': 'A gestão é feita de forma parcialmente terceirizada.'
        },
        {
        'option_number': 3,
        'option_text': 'A gestão é feita de forma completamente terceirizada.'
        },
        {
        'option_number': 4,
        'option_text': 'Não tenho certeza'
        }
    ]
    },
    {
    'question_number': 9,
    'question_type': 'select',
    'question_text': 'As atividades de execução de saúde ocupacional incluem o planejamento de exames ocupacionais para colaboradores, agendamento de consultas e exames, cobrança de resultados de clínicas parceiras, integração dos resultados na ficha de cada colaborador, dentre outras. Qual o modelo de gestão adotado por sua organização?',
    'is_required': True,
    'options': [
        {
        'option_number': 1,
        'option_text': 'A execução é feita de forma completamente interna, com equipe própria.'
        },
        {
        'option_number': 2,
        'option_text': 'A execução é feita de forma parcialmente terceirizada.'
        },
        {
        'option_number': 3,
        'option_text': 'A execução é feita de forma completamente terceirizada.'
        },
        {
        'option_number': 4,
        'option_text': 'Não tenho certeza'
        }
    ]
    },
    {
    'question_number': 10,
    'question_type': 'select',
    'question_text': 'Caso sua organização terceirize os exames ocupacionais, seja os exames clínicos ou complementares, qual o modelo de precificação do contrato atual?',
    'is_required': True,
    'options': [
        {
        'option_number': 1,
        'option_text': 'Pagamos um valor fixo no contrato, independente do número de colaboradores ou exames realizados.'
        },
        {
        'option_number': 2,
        'option_text': 'Pagamos um valor fixo por colaborador, para toda a organização.'
        },
        {
        'option_number': 3,
        'option_text': 'Pagamos um valor fixo por colaborador, mas esse valor varia por localização da unidade de negócio onde o colaborador está alocado, ou outros fatores.'
        },
        {
        'option_number': 4,
        'option_text': 'Pagamos um valor variável, baseado no número de exames realizados, mas não temos acesso a quanto cada exame custa na ponta final (clínica).'
        },
        {
        'option_number': 5,
        'option_text': 'Pagamos um valor variável, baseado no custo exato de cada exame realizado, e o serviço de terceirização é transparente em sua taxa de serviço.'
        },
        {
        'option_number': 6,
        'option_text': 'Não tenho certeza'
        },
        {
        'option_number': 7,
        'option_text': 'Minha organização não terceiriza os exames ocupacionais.'
        }
    ]
    },
    {
    'question_number': 11,
    'question_type': 'select',
    'question_text': 'Quando foi a última vez que o modelo de gestão foi revisado?',
    'is_required': True,
    'options': [
        {
        'option_number': 1,
        'option_text': 'Há menos de 6 meses'
        },
        {
        'option_number': 2,
        'option_text': 'Entre 6 meses e 1 ano'
        },
        {
        'option_number': 3,
        'option_text': 'Entre 1 e 2 anos'
        },
        {
        'option_number': 4,
        'option_text': 'Há mais de 2 anos'
        },
        {
        'option_number': 5,
        'option_text': 'Não tenho certeza'
        }
    ]
    },
    {
    'question_number': 12,
    'question_type': 'select',
    'question_text': 'Onde você diria que a maior parte dos colaboradores realizam seus exames ocupacionais?',
    'is_required': True,
    'options': [
        {
        'option_number': 1,
        'option_text': 'No local de trabalho, possuímos enfermarias próprias.'
        },
        {
        'option_number': 2,
        'option_text': 'No local de trabalho, contratamos serviço in-loco de clínicas de saúde ocupacionais locais.'
        },
        {
        'option_number': 3,
        'option_text': 'Em clínicas de saúde ocupacional, com contrato direto com a organização.'
        },
        {
        'option_number': 4,
        'option_text': 'Em clínicas de saúde ocupacional, mas por intermédio de empresa terceirizada.'
        },
        {
        'option_number': 5,
        'option_text': 'Não tenho certeza.'
        }
    ]
    },
    {
    'question_number': 13,
    'question_type': 'select',
    'question_text': 'Qual o tamanho da equipe responsável por saúde ocupacional? Favor considerar toda a equipe interna que realiza a gestão (ex: gestão de contratos, custos, exames, etc.)',
    'is_required': True,
    'options': [
        {
        'option_number': 1,
        'option_text': '1 pessoa.'
        },
        {
        'option_number': 2,
        'option_text': '2 a 5 pessoas.'
        },
        {
        'option_number': 3,
        'option_text': '6 a 10 pessoas.'
        },
        {
        'option_number': 4,
        'option_text': '11 a 20 pessoas.'
        },
        {
        'option_number': 5,
        'option_text': 'Mais de 20 pessoas.'
        },
        {
        'option_number': 6,
        'option_text': 'Não tenho certeza.'
        }
    ]
    },
    {
    'question_number': 14,
    'question_type': 'select',
    'question_text': 'Como a equipe responsável realiza o agendamento de exames ocupacionais (incluindo complementares) para os colaboradores?',
    'is_required': True,
    'options': [
        {
        'option_number': 1,
        'option_text': 'A equipe agenda os exames de forma individual (para cada colaborador), diretamente com clínicas parceiras, por via telefônica ou e-mail.'
        },
        {
        'option_number': 2,
        'option_text': 'A equipe agenda os exames de forma individual (para cada colaborador), através de um sistema integrado (sistemas como SOU, SOC, FapOnline, etc.).'
        },
        {
        'option_number': 3,
        'option_text': 'A equipe agenda os exames em lote, para grupos de colaboradores, diretamente com clínicas parceiras, por via telefônica ou e-mail.'
        },
        {
        'option_number': 4,
        'option_text': 'A equipe agenda os exames em lote, para grupos de colaboradores, através de um sistema de tecnologia (sistemas como SOU, SOC, FapOnline, etc.).'
        },
        {
        'option_number': 5,
        'option_text': 'A equipe não agenda os exames manualmente. Um sistema de agendamento automático é utilizado, e a equipe faz apenas gestão de exceção e monitoramento de indicadores.'
        },
        {
        'option_number': 6,
        'option_text': 'Não tenho certeza.'
        }
    ]
    },
    {
    'question_number': 15,
    'question_type': 'select',
    'question_text': 'Quando foi a última vez que a diretoria da empresa solicitou uma análise de custos de exames ocupacionais?',
    'is_required': True,
    'options': [
        {
        'option_number': 1,
        'option_text': 'Há menos de 6 meses.'
        },
        {
        'option_number': 2,
        'option_text': 'Entre 6 meses e 1 ano.'
        },
        {
        'option_number': 3,
        'option_text': 'Entre 1 e 2 anos.'
        },
        {
        'option_number': 4,
        'option_text': 'Há mais de 2 anos.'
        },
        {
        'option_number': 5,
        'option_text': 'Não tenho certeza.'
        }
    ]
    },
    {
    'question_number': 16,
    'question_type': 'select',
    'question_text': 'Se a diretoria de sua organização precisasse de uma análise de custos incluindo um orçamento para exames ocupacionais por mês no próximo ano, além de uma comparação de quais e quantos exames são realizados por unidade de negócio e por tipo de atividade, qual o prazo para a disponibilização destes dados?',
    'is_required': True,
    'options': [
        {
        'option_number': 1,
        'option_text': 'A informação já está disponível de forma imediata, via sistema com painel de indicadores.'
        },
        {
        'option_number': 2,
        'option_text': 'Menos de 1 dia.'
        },
        {
        'option_number': 3,
        'option_text': 'Entre 1 e 2 dias.'
        },
        {
        'option_number': 4,
        'option_text': 'Entre 2 dias e 1 semana.'
        },
        {
        'option_number': 5,
        'option_text': 'Entre 1 e 2 semanas.'
        },
        {
        'option_number': 6,
        'option_text': 'Mais de 2 semanas.'
        },
        {
        'option_number': 7,
        'option_text': 'Não tenho certeza.'
        }
    ]
    },
    {
    'question_number': 17,
    'question_type': 'input',
    'question_text': 'Se você quiser receber uma análise com as respostas agregadas e anonimizadas desse questionário, por favor, informe seu e-mail abaixo:',
    'is_required': False,
    'options': []
    }
]

def add_question_to_survey(survey: Survey, question: dict):
    question_type = question['question_type']
    new_question = Question(
        survey = survey,
        question_number=question['question_number'],
        question_text=question['question_text'],
        question_type=question_type,
        is_required=question['is_required']
    )
    print(f'Survey {survey.name}: Adding question number {new_question.question_number}')
    new_question.save()
    if question_type == 'select':
        for option in question['options']:
            new_option = QuestionOption(
                question = new_question,
                option_number=option['option_number'],
                option_text=option['option_text']
            )
            new_option.save()

def clear_survey(survey: Survey):
    print(f'Clearing survey {survey.name}')
    for question in survey.questions.all():
        for option in question.options.all():
            option.delete()
        question.delete()

def run():
    target_survey = Survey.objects.get(name='Pesquisa Saúde Ocupacional')
    clear_survey(target_survey)
    for question in questions:
        add_question_to_survey(target_survey, question)
    print('.')
    print('.')
    print('.')
    print('Finished!')