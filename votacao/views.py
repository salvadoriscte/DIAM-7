from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse,HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from .models import Questao, Opcao, User, Aluno, Voto
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required



def index(request):
    latest_question_list =Questao.objects.order_by('-pub_data')[:5]
    total_votos = 0
    if request.user.is_authenticated:
        try:
            aluno = Aluno.objects.get(user=request.user)
            total_votos = Voto.objects.filter(aluno=aluno).count()
        except Aluno.DoesNotExist:
            pass
    context = {'latest_question_list': latest_question_list, 'total_votos': total_votos}
    return render(request, 'votacao/index.html', context)




def detalhe(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    return render(request, 'votacao/detalhe.html',{'questao': questao})


def resultados(request, questao_id):
        questao = get_object_or_404(Questao, pk=questao_id)
        return render(request,'votacao/resultados.html',{'questao': questao})

@login_required
def voto(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    aluno = Aluno.objects.get(user=request.user)
    # Limite de votos fixo LEI-PL 3 + 10
    limite_votos = 13

    # Verifique se o aluno já atingiu o limite de votos
    votos_aluno = Voto.objects.filter(aluno=aluno).count()
    if not request.user.is_superuser: #Se for admin n tem limite
        if votos_aluno >= limite_votos:
            # Se o aluno atingiu o limite de votos, retorne uma mensagem de erro
            return render(request, 'votacao/detalhe.html', {'questao': questao, 'error_message': "Limite de votos atingido!(13)", })
    try:
        opcao_seleccionada = questao.opcao_set.get(pk=request.POST['opcao'])

    except (KeyError, Opcao.DoesNotExist):
    # Apresenta de novo o form para votar
        return render(request, 'votacao/detalhe.html', {'questao': questao, 'error_message': "Não escolheu nenhuma opção!!!", })
    else:
        try:
            voto_existente = Voto.objects.get(aluno=aluno, opcao=opcao_seleccionada)
            # Se o voto já existir, retorne uma mensagem de erro ou simplesmente ignore a ação

            return render(request, 'votacao/detalhe.html',{'questao': questao, 'error_message': "Já escolheu esta opção!!!", })
        except Voto.DoesNotExist:
            opcao_seleccionada.votos += 1
            opcao_seleccionada.save()
            Voto.objects.create(aluno=aluno, opcao=opcao_seleccionada)
            # Retorne sempre HttpResponseRedirect depois de # tratar os dados POST de um form
            # pois isso impede os dados de serem tratados # repetidamente se o utilizador
            # voltar para a página web anterior.
            return HttpResponseRedirect( reverse('votacao:resultados', args=(questao.id,)))
@staff_member_required
def criar_questao(request):
    if request.method == 'POST':
        questao_texto = request.POST.get('texto')
        if questao_texto:
            q = Questao(questao_texto=questao_texto, pub_data=timezone.now())
            q.save()
            return HttpResponseRedirect(reverse('votacao:index'))
        else:
            mensagem_de_erro = "Insira algum texto para criar uma questão!!!"
            return render(request, 'votacao/criarquestao.html', {'error_message': mensagem_de_erro})
    else:
        return render(request, 'votacao/criarquestao.html')

@staff_member_required
def criar_opcao(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    if request.method == 'POST':
        texto_opcao = request.POST.get('texto_opcao')
        if texto_opcao:
            questao.opcao_set.create(opcao_texto=texto_opcao, votos=0)
            #redireciona para a página votacao_detalhe
            return HttpResponseRedirect(reverse('votacao:detalhe', args=(questao.id,)))
        else:
            mensagem_erro = "Por favor, digite texto para a opção!!!"
            return render(request, 'votacao/criaropcao.html', {'questao': questao, 'mensagem_erro': mensagem_erro})
    else:
        return render(request, 'votacao/criaropcao.html', {'questao': questao})

def registar_aluno(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        curso = request.POST.get('curso')
        error_message = None

        if not username:
            error_message = "Insira um username."
        elif not email:
            error_message = "Insira um e-mail."
        elif not password:
            error_message = "Insira uma password."
        elif User.objects.filter(username=username).exists():
            error_message = "Username já existe."
        elif User.objects.filter(email=email).exists():
            error_message = "Email já existe."
        elif len(password) < 8:
            error_message = "A password deve ter pelo menos 8 caracteres."
        elif not curso:
            error_message = "Insira um Curso."

        if error_message:
            return render(request, 'votacao/registo.html', {'error_message': error_message})
        else:
            # Cria user
            user = User.objects.create_user(username, email, password)
            user.save()

            # Cria aluno
            aluno=Aluno(user=user,curso=curso)
            aluno.save()

            # Log in do aluno
            login(request, user)

            # Redirect to the main page
            return HttpResponseRedirect(reverse('votacao:index'))
    else:
        return render(request, 'votacao/registo.html')

def aluno_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('votacao:index'))
        else:
            return render(request, 'votacao/login.html', {'error_message': 'Username ou Password inválidos'})
    else:
        return render(request, 'votacao/login.html')

@login_required
def aluno_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('votacao:index'))


@login_required
def perfil(request):
    aluno= Aluno.objects.get(user=request.user)
    total_votos = Voto.objects.filter(aluno=aluno).count()
    return render(request, 'votacao/perfil.html', {'aluno': aluno,'total_votos': total_votos})

@staff_member_required
def remover_questao(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    questao.delete()
    return HttpResponseRedirect(reverse('votacao:index'))

@staff_member_required
def remover_opcao(request, questao_id, opcao_id):
    opcao = get_object_or_404(Opcao, pk=opcao_id)
    opcao.delete()
    return HttpResponseRedirect(reverse('votacao:detalhe', args=(questao_id,)))