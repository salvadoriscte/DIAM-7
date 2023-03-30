from votacao.models import Questao,Opcao
from django.db.models import Max
def total_votes():
    total = Opcao.objects.aggregate(models.Sum('votos'))
    print(f"Total de votos: {total['votos__sum']}")


def most_voted_option():

    for questao in Questao.objects.all():

        opcao_mais_votada = questao.opcao_set.aggregate(Max('votos'))['votos__max']

        # Filter the options to find the one with the most votes
        opcao_mais_votada = questao.opcao_set.filter(votos=opcao_mais_votada).first()


        print("\nQuestao : {}".format(questao.questao_texto))
        print("Opcao mais votada: {}".format(opcao_mais_votada.opcao_texto))


total_votes()
most_voted_option()